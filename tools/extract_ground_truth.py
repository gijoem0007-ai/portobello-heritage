"""Import ground-truth content from the Xara export into this clone.

Reads every .htm page in the Xara Apr 2026 export (the ground truth) and extracts its content
blocks (text paragraphs, images, embeds) in reading order, from the desktop layout, or from
the mobile layout where the desktop one is missing content. It writes:
  content/gt/<page>.json   data rendered by build.py
  content/gt/<page>.txt    human-readable dump for review
It also copies every image / downloadable file the pages reference from index_htm_files/
into images/pht/ and files/, keeping the original numbered filenames (plus @2x variants).
Run this, then build.py."""
import os, re, json, shutil
from html.parser import HTMLParser
from urllib.parse import unquote

GT = r"N:\Websites\Portobello heritage\Xara Apr 2026"
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "content", "gt")
os.makedirs(OUT, exist_ok=True)

# footer lines on every page (site furniture, rendered by build.py's footer)
NOISE = {"Created by jtm websites", "Terms & Conditions"}
# labels of menu buttons (top menu, Heritage and Events side menus). Only buttons with these labels
# are menu items; the same words as page text are real content (e.g. Heritage's own "Heritage" heading)
MENU_WORDS = {"Home", "Heritage", "Events", "Links", "Contact Us", "Menu", "Industry", "Architecture",
              "Culture", "At The Sea Side", "People", "Plaques", "Coade Stone Pillars", "Oral History",
              "Forthcoming Events", "Archived Events"}

def px(style, key):
    m = re.search(key + r":\s*(-?[\d.]+)px", style or "")
    return float(m.group(1)) if m else None

class P(HTMLParser):
    def __init__(self, want=1):
        super().__init__(convert_charrefs=True)
        self.want = want
        self.variant = 0
        self.inside = False
        self.skip = 0
        self.blocks = []
        self.box = None      # current text box
        self.line = None     # current line
        self.box_depth = 0
        self.div_depth = 0
        self.g = 0           # global div depth
        self.mob = None      # depth of the mobile-variant div while inside it
        self.title = ""; self.in_title = False
        self.links = []
        self.last_top = 0
        self.cur_a = None
        self.cur_lightbox = self.cur_popup = False
        self.rs_alts = set()     # labels of button art drawn in an inactive state (set by run())
        self.seen_btn = set()
        self.slider = None       # current Xara slider (auto-advancing photo gallery)
        self.slider_depth = 0
    def start_box(self, a):
        self.box = {"type": "text", "top": px(a.get("style"), "top") or 0,
                    "left": px(a.get("style"), "left") or 0,
                    "width": px(a.get("style"), "width") or 0, "lines": []}
        self.box_depth = self.div_depth
    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "title": self.in_title = True
        if tag in ("script", "style"): self.skip += 1
        if tag == "div":
            self.g += 1
        if tag == "div" and re.fullmatch(r"xr_mvp_\d+", a.get("id") or ""):
            self.variant += 1
            self.inside = self.variant == self.want
            if self.variant != self.want: self.mob = self.g
        if not self.inside: return
        cls = a.get("class") or ""
        if tag == "div":
            self.div_depth += 1
            if "xr_txt" in cls.split():
                self.start_box(a)
            if "xr_slider" in cls.split():
                s = a.get("style")
                self.slider = {"type": "slider", "top": px(s, "top") or 0, "left": px(s, "left") or 0,
                               "w": px(s, "width"), "h": px(s, "height"), "slides": []}
                self.slider_depth = self.div_depth
        if tag == "span" and self.box is not None and {"xr_tc", "xr_tl", "xr_tr"} & set(cls.split()):
            s = a.get("style")
            self.line = {"top": px(s, "top") or 0, "text": "", "right_aligned": "xr_tr" in cls.split(),
                         "left": px(s, "left") or 0, "width": px(s, "width") or 0}
            self.box["lines"].append(self.line)
        # Xara also tags plain pictures "xr_rnsp_" in some exports (the 2026-10-02 re-export does),
        # so the class alone doesn't mean "button": only an xr_rnsp_ image inside an ordinary link
        # is a button. Inside a click-to-enlarge link (xr_hs), or an unlabelled image inside a
        # show-a-popup link (plaque thumbnails), it is a picture; a labelled one ("Video Essay") is a button.
        if tag == "img" and self.slider is not None and a.get("src"):   # one slide of a gallery
            s = a.get("style")
            self.slider["slides"].append({"src": a.get("src"), "alt": a.get("alt") or "",
                                          "left": px(s, "left") or 0, "top": px(s, "top") or 0,
                                          "w": px(s, "width"), "h": px(s, "height")})
            return
        pic_link = tag == "img" and (self.cur_lightbox or (self.cur_popup and not (a.get("alt") or "").strip()))
        if tag == "img" and "xr_rnsp_" in cls and "xr_ro" not in cls and self.cur_a and not pic_link:
            # Xara button: an image link whose alt text is the button label
            label = (a.get("alt") or "").strip()
            key = (self.cur_a, label)
            if label and label not in NOISE and label not in MENU_WORDS and key not in self.seen_btn \
                    and not self.cur_a.startswith("javascript"):
                self.seen_btn.add(key)
                t = px(a.get("style"), "top") or 0
                self.blocks.append({"type": "button", "href": self.cur_a, "label": label,
                                    "top": t if t > 0 else self.last_top, "left": px(a.get("style"), "left") or 0})
            return
        if tag == "img":
            if not a.get("src"): return
            if "xr_rnsp_" in cls and ("xr_ro" in cls or (self.cur_a and not pic_link)):
                return                                   # button artwork / its hover state
            s = a.get("style")
            if "xr_rnsp_" in cls and not self.cur_a and (
                    "xr_rs" in cls.split() or min(px(s, "width") or 99, px(s, "height") or 99) <= 6):
                return                                   # unlinked button state art; hairline rules
            if "xr_rnsp_" in cls and not self.cur_a and a.get("alt") and a.get("alt") in self.rs_alts:
                # a button drawn in its inactive (greyed) state, e.g. "Back to Events Page" on the
                # Events page itself: shown, but it goes nowhere
                key = (None, a["alt"].strip())
                if key not in self.seen_btn:
                    self.seen_btn.add(key)
                    self.blocks.append({"type": "button", "href": None, "label": a["alt"].strip(), "inactive": True,
                                        "top": px(s, "top") or 0, "left": px(s, "left") or 0})
                return
            self.blocks.append({"type": "img", "src": a.get("src"), "alt": a.get("alt") or "",
                                "rollover": "xr_ro" in cls,
                                "top": px(s, "top") or 0, "left": px(s, "left") or 0,
                                "w": px(s, "width"), "h": px(s, "height")})
        if tag == "iframe" and a.get("src"):
            s = a.get("style")
            self.blocks.append({"type": "embed", "src": a.get("src"), "title": a.get("title") or "",
                                "top": px(s, "top") or self.last_top, "left": px(s, "left") or 0})
        if tag == "div":
            t = px(a.get("style"), "top")
            if t is not None: self.last_top = t
        if tag == "a" and a.get("href"):
            self.cur_lightbox = "xr_hs" in cls.split()                  # click-to-enlarge
            self.cur_popup = a["href"].startswith("javascript:xr_cpu")   # shows a popup layer
            if not self.cur_lightbox:                    # enlarge-on-click targets aren't page links
                self.links.append(a.get("href"))
            self.cur_a = a.get("href")
    def handle_endtag(self, tag):
        if tag == "a": self.cur_a = None; self.cur_lightbox = self.cur_popup = False
        if tag == "title": self.in_title = False
        # never below 0: Xara pages can carry a stray "</script>" (events page.htm, heritage.htm),
        # which browsers ignore but which would otherwise hide every word of text after it
        if tag in ("script", "style"): self.skip = max(0, self.skip - 1)
        if tag == "div":
            self.g -= 1
            if self.mob is not None and self.g < self.mob:
                self.mob = None; self.inside = True; self.div_depth = 0   # shared layer after variants
                return
        if not self.inside: return
        if tag == "div":
            if self.slider is not None and self.div_depth == self.slider_depth:
                if self.slider["slides"]:
                    self.blocks.append(self.slider)
                self.slider = None
            if self.box is not None and self.div_depth == self.box_depth:
                self.box["side_labels"] = side_labels(self.box)
                self.blocks.append(self.box); self.box = None; self.line = None
            self.div_depth -= 1
    def handle_data(self, d):
        if self.in_title: self.title += d
        if self.inside and not self.skip and self.line is not None:
            self.line["text"] += d

def paras_of(box):
    """Join lines into paragraphs. Same-top fragments join directly; a new line continues the
    paragraph when the previous line ended with a space (soft wrap), else starts a new one."""
    lines = [l for l in box["lines"] if l["text"] != ""]
    tops = sorted({round(l["top"], 1) for l in lines})
    gaps = sorted(b - a for a, b in zip(tops, tops[1:]) if b - a >= 6)
    step = gaps[len(gaps) // 4] if gaps else 999
    paras, cur, last_top, prev_own = [], "", None, False
    for l in lines:
        t = l["text"]
        own = l.get("own_para", False)
        if (own or prev_own) and cur:                 # a sign-off is always a paragraph of its own
            paras.append(cur); cur = t
        elif last_top is None or abs(l["top"] - last_top) < 6:
            cur += t
        elif l["top"] - last_top > step * 1.35:
            paras.append(cur); cur = t
        elif cur.endswith((" ", "\u00a0")) or cur.endswith("-") and not cur.endswith(" -"):
            cur += t
        else:
            paras.append(cur); cur = t
        last_top, prev_own = l["top"], own
    if cur: paras.append(cur)
    paras = [re.sub(r"\s+", " ", p).strip() for p in paras]
    return [p for p in paras if p and p not in NOISE]

def side_labels(box):
    """Pull out right-aligned label text floating inside a text column (e.g. a caption set beside
    an image: Georgian Houses' "Portico of the now demolished Windsor Lodge..."). Each becomes its
    own text block with absolute position and right edge, so build.py can tie it to that image.
    Other right-aligned text (author sign-offs flush with the right margin) stays in the box as
    its own paragraph and is listed in box["signoffs"]; blank right-aligned spans run on to the
    line before them as they always did."""
    out, run_, keep = [], [], []
    def flush():
        raw = "".join(l["text"] for l in run_)
        text = re.sub(r"\s+", " ", raw).strip()
        right = max(l["left"] + l["width"] for l in run_)
        if text and len(text) <= 170 and box["width"] and right < box["width"] - 60:
            out.append({"type": "text", "side": True, "top": box["top"] + run_[0]["top"],
                        "left": box["left"] + min(l["left"] for l in run_),
                        "right": box["left"] + right, "paras": [text]})
        elif text:
            keep.append({"top": run_[0]["top"], "text": text, "own_para": True})
            box.setdefault("signoffs", []).append(text)
        elif keep:
            keep[-1]["text"] += raw
        run_.clear()
    for l in box["lines"]:
        if l.get("right_aligned"):
            if run_ and l["top"] - run_[-1]["top"] > 30:
                flush()
            run_.append(l)
        else:
            if run_: flush()
            keep.append(l)
    if run_: flush()
    box["lines"] = keep
    return out

def score(p):
    t = sum(len(q) for b in p.blocks if b["type"] == "text" for q in paras_of(b))
    i = sum(1 for b in p.blocks if b["type"] == "img" and "39931" not in b["src"]) + \
        sum(len(b["slides"]) for b in p.blocks if b["type"] == "slider")
    return t, i

def run(fn):
    src = open(os.path.join(GT, fn), encoding="utf-8", errors="replace").read()
    rs_alts = set(re.findall(r'<img class="[^"]*\bxr_rs\b[^"]*"[^>]*\balt="([^"]+)"', src))
    p = P(1); p.rs_alts = rs_alts; p.feed(src)
    m = P(2); m.rs_alts = rs_alts; m.feed(src)
    (dt, di), (mt, mi) = score(p), score(m)
    variant = "desktop"
    if mt > dt * 1.15 + 50 or mi >= di + 3:
        p = m; variant = "mobile"
    VARIANT[fn] = f"{variant} (desktop text={dt} imgs={di}; mobile text={mt} imgs={mi})"
    out = []
    for b in p.blocks:
        if b["type"] == "text":
            out.extend(b["side_labels"])
            ps = paras_of(b)
            if ps:
                blk = {"type": "text", "top": b["top"], "left": b["left"], "paras": ps}
                if b.get("signoffs"):
                    blk["signoffs"] = b["signoffs"]
                out.append(blk)
        else:
            if b["type"] in ("embed", "button", "slider"):
                out.append(b); continue
            if b["src"].endswith(("39931.jpg", "40110.jpg")):   # site banner (desktop / mobile)
                continue
            out.append(b)
    out.sort(key=lambda b: (round(b["top"] / 8), b["left"]))
    page = {"file": fn, "variant": VARIANT[fn], "title": p.title.strip(), "blocks": out,
            "links": list(dict.fromkeys(l for l in p.links if not l.startswith("javascript")))}
    base = os.path.join(OUT, fn[:-4])
    json.dump(page, open(base + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    with open(base + ".txt", "w", encoding="utf-8") as f:
        f.write(f"# {fn} | title={page['title']}\n")
        for b in out:
            if b["type"] == "text":
                f.write(f"\n--- text @top={b['top']:.0f} left={b['left']:.0f}\n")
                for q in b["paras"]: f.write(q + "\n")
            elif b["type"] == "button":
                f.write(f"\n[BUTTON {b['label']!r} -> {b['href']} @top={b['top']:.0f}]\n")
            elif b["type"] == "slider":
                f.write(f"\n[SLIDER @top={b['top']:.0f} left={b['left']:.0f} {b['w']}x{b['h']}: "
                        + ", ".join(os.path.basename(x["src"]) for x in b["slides"]) + "]\n")
            elif b["type"] == "embed":
                f.write(f"\n[EMBED {b['src']} @top={b['top']:.0f}]\n")
            else:
                f.write(f"\n[IMG{' rollover' if b['rollover'] else ''} {b['src']} @top={b['top']:.0f} "
                        f"left={b['left']:.0f} {b['w']}x{b['h']}]" + (f" alt={b['alt']!r}" if b['alt'] else "") + "\n")
        f.write("\n## LINKS\n" + "\n".join(page["links"]) + "\n")
    return sum(len(q) for b in out if b["type"] == "text" for q in b["paras"])

VARIANT = {}
for fn in sorted(os.listdir(GT)):
    if fn.endswith(".htm"):
        print(f"{run(fn):7d}  {fn:45s} {VARIANT[fn]}")

# ------------------------------------------------------------------ copy referenced assets
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif")
SRC = os.path.join(GT, "index_htm_files")
os.makedirs(os.path.join(ROOT, "images", "pht"), exist_ok=True)
os.makedirs(os.path.join(ROOT, "files"), exist_ok=True)
wanted = {"39931.jpg", "39937.png", "39938.png"}          # banner + social icons
for fn in os.listdir(OUT):
    if not fn.endswith(".json"): continue
    page = json.load(open(os.path.join(OUT, fn), encoding="utf-8"))
    for b in page["blocks"]:
        if b["type"] == "img": wanted.add(unquote(os.path.basename(b["src"])))
        if b["type"] == "slider": wanted.update(unquote(os.path.basename(x["src"])) for x in b["slides"])
    for l in page["links"]:
        if l.startswith("index_htm_files/"): wanted.add(unquote(os.path.basename(l)))
copied, missing = 0, []
for name in sorted(wanted):
    src = os.path.join(SRC, name)
    if not os.path.exists(src):
        missing.append(name); continue
    dest = os.path.join(ROOT, "images", "pht") if name.lower().endswith(IMG_EXT) else os.path.join(ROOT, "files")
    shutil.copy2(src, os.path.join(dest, name)); copied += 1
    stem, ext = os.path.splitext(name)
    hi = os.path.join(SRC, stem + "@2x" + ext)
    if os.path.exists(hi):
        shutil.copy2(hi, os.path.join(dest, stem + "@2x" + ext)); copied += 1
print(f"copied {copied} asset files; missing from ground truth: {missing}")

# ------------------------------------------------------------------ script-built parts (content/extras)
import xara_extras
for line in xara_extras.run():
    print("extras:", line)
