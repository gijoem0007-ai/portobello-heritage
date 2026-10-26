r"""Compare the collector's findings for the live site and the replica, page by page.

Run from portobello-clone\:  python tools\compare\compare.py [page ...]
Reads tools\compare\results\{live,replica}\<page>.json, prints a summary, and writes
tools\compare\report.json (used by report.py). Differences listed in KNOWN are reported
separately as "intended", so they don't hide new problems."""
import json, os, re, sys, unicodedata

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, "results")

# (live page, replica page) — every page of the replica
PAGES = {
    "index": ("index.htm", "index.html"), "heritage": ("heritage.htm", "heritage.html"),
    "events": ("events page.htm", "events.html"), "links": ("links.htm", "links.html"),
    "contact": ("contact us.htm", "contact.html"), "terms": ("terms.htm", "terms.html"),
}
for slug, gt in [("beach", "beach"), ("chocolate-factory", "chocolate factory"),
                 ("coade-stone-pillars", "coade stone pillars"), ("entertainment", "entertainment"),
                 ("euphemia-tot-addy", "euphemia tot addy"), ("georgian-houses", "georgian houses"),
                 ("golden-days", "golden days"), ("helen-hopekirk", "helen hopkirk"),
                 ("hendersons-garage", "hendersons garage"), ("heritage-trail-leaflet", "heritage trail leaflet"),
                 ("high-days-and-holidays", "high days and holidays"), ("marine-gardens", "marine gardens"),
                 ("miss-meg-moir", "miss meg moir"), ("oral-history", "oral history"),
                 ("peggy-brown", "peggy brown"), ("photos-of-coade-stone-pillars", "photos of coade stone pillars"),
                 ("pier", "pier"), ("plaques", "plaques"), ("portobello-harbour", "portobello harbour"),
                 ("pottery-manufacture", "pottery manufacture"), ("prince-philip", "prince phillip"),
                 ("salt-pans", "salt pans"), ("shops-and-shopkeepers", "shops and shopkeepers"),
                 ("sir-peter-heatly", "sir peter heatly"), ("toddlers-hut", "toddlers hut"),
                 ("william-leatham", "william leatham")]:
    PAGES[slug] = (gt + ".htm", f"heritage/{slug}.html")
for slug, gt in [("forthcoming-events", "forthcoming events"), ("dig-portobello", "dig portobello"),
                 ("kiln-celebration", "kiln celebration"), ("porty-love-stories", "porty love stories")]:
    PAGES[slug] = (gt + ".htm", f"events/{slug}.html")

LIVE_TO_REPLICA = {v[0]: v[1] for v in PAGES.values()}
BANNERS = ("39931.", "40110.")                 # site banner (desktop / mobile), part of the frame
# deliberate differences, recorded in CHANGELOG.md
KNOWN_TEXT = {"local test replica rebuilt from the xara apr 2026 export",
              }
# replica-only blocks that are intended: Contact shows the membership pop-up's payment details
# on the page (CHANGELOG section 4)
KNOWN_SECTIONS = [(r"How to Pay", r"Payment Reference: Your name")]

# intended picture differences, by page (reported as "intended", not as problems)
KNOWN_PICTURES = {"plaques": "The 15 plaque detail panels: on the live page each one opens when you click "
                             "its plaque; the replica shows them under the thumbnails (CHANGELOG section 4)."}
# Contact: the membership pop-up form is deliberately not reproduced (CHANGELOG section 4)
KNOWN_BUTTONS = {"membership application form"}

def norm(s):
    s = unicodedata.normalize("NFKC", s).lower()
    s = re.sub(r"[‘’´`]", "'", s); s = re.sub(r"[“”]", '"', s); s = re.sub(r"[–—]", "-", s)
    return re.sub(r"\s+", " ", s).strip()

def squash(s):                                  # compare ignoring all spacing and punctuation
    return re.sub(r"[^a-z0-9£]", "", norm(s))

def sentences(text):
    """Split into sentences. Running lines are joined first (Xara breaks text at every printed
    line); a short line with no closing punctuation (a heading or caption) stays on its own."""
    units, para = [], []
    for line in (l.strip() for l in text.split("\n")):
        if not line:
            continue
        if len(line) < 60 and not re.search(r"[.!?:;,\"”')]$", line):
            if para: units.append(" ".join(para)); para = []
            units.append(line)
        else:
            para.append(line)
    if para: units.append(" ".join(para))
    out = []
    for u in units:
        out += [s.strip() for s in re.split(r"(?<=[.!?])\s+(?=[A-Z0-9“\"'(‘])", re.sub(r"\s+", " ", u))
                if len(squash(s)) >= 4]
    return out

def page_target(url):
    """A link target, made comparable between the two sites."""
    u = re.sub(r"^https?://(127\.0\.0\.1|localhost):8767/(live|replica)/", "", url)
    u = re.sub(r"[?#].*$", "", u)
    from urllib.parse import unquote
    u = unquote(u)
    if u.endswith(".htm") and u in LIVE_TO_REPLICA:
        return "page:" + LIVE_TO_REPLICA[u]
    if u.endswith(".html"):
        return "page:" + u
    if u.startswith("http"):
        return "web:" + re.sub(r"^https?://(www\.)?", "", u).rstrip("/").lower()
    return "file:" + os.path.basename(u).lower()

def compare(name):
    live_f, rep_f = (os.path.join(RES, s, name + ".json") for s in ("live", "replica"))
    if not (os.path.exists(live_f) and os.path.exists(rep_f)):
        return None
    L, R = json.load(open(live_f, encoding="utf-8")), json.load(open(rep_f, encoding="utf-8"))
    diffs = []

    # text
    for start, end in KNOWN_SECTIONS:
        R["text"] = re.sub(start + r".*?" + end, " ", R["text"], flags=re.S)
    for side in (L, R):                         # footer lines: site furniture, checked as links
        side["text"] = re.sub(r"Terms & Conditions|Created by jtm websites", " ", side["text"])
    lt, rt = sentences(L["text"]), sentences(R["text"])
    l_all, r_all = squash(L["text"]), squash(R["text"])

    def present(s, other):
        """Most of the sentence's 5-word stretches appear on the other site (tolerates a heading
        that runs into a neighbouring sentence differently on the two sites)."""
        w = re.findall(r"[a-z0-9£]+", norm(s))
        if len(w) < 6:
            return "".join(w) in other
        wins = ["".join(w[i:i + 5]) for i in range(len(w) - 4)]
        return sum(x in other for x in wins) >= 0.7 * len(wins)

    missing = [s for s in lt if not present(s, r_all)]
    extra = [s for s in rt if not present(s, l_all) and not any(k in norm(s) for k in KNOWN_TEXT)]
    intended = []
    title = norm(R.get("page_title", ""))
    if title and any(norm(s) == title for s in extra):            # decision: every page has a title (section 23)
        extra = [s for s in extra if norm(s) != title]
        intended.append(f'Page title "{R["page_title"]}" (the live page has none; every replica page has a title by decision, CHANGELOG section 23).')
    if missing: diffs.append({"kind": "text missing from replica", "items": missing})
    if extra: diffs.append({"kind": "text on replica but not on live page", "items": extra})

    # pictures (by content)
    li = [i for i in L["images"] if not os.path.basename(i["src"]).startswith(BANNERS)]
    ri = [i for i in R["images"] if not os.path.basename(i["src"]).startswith(BANNERS)]
    lh, rh = [i["hash"] for i in li], [i["hash"] for i in ri]
    gone = [i for i in li if i["hash"] not in rh]
    scroll_names = {os.path.basename(u) for u in L.get("scroll_in", [])}
    added = [i for i in ri if i["hash"] not in lh and os.path.basename(i["src"]) not in scroll_names]
    if gone: diffs.append({"kind": "pictures missing from replica",
                           "items": [f'{os.path.basename(i["src"])} ({i["w"]}x{i["h"]})' for i in gone]})
    if added and name in KNOWN_PICTURES:
        intended.append(KNOWN_PICTURES[name]); added = []
    if added: diffs.append({"kind": "pictures on replica but not on live page",
                            "items": [f'{os.path.basename(i["src"])} ({i["w"]}x{i["h"]})' for i in added]})
    if sorted(lh) != sorted(rh) and not gone and not added and not L.get("scroll_in") and not intended:
        diffs.append({"kind": "same pictures, different number of copies", "items": [f"live {len(lh)}, replica {len(rh)}"]})

    # buttons and links
    lb = {(norm(b["label"]), page_target(b["href"])) for b in L["buttons"] if norm(b["label"]) not in KNOWN_BUTTONS}
    rb = {(norm(b["label"]), page_target(b["href"])) for b in R["buttons"]}
    if lb - rb: diffs.append({"kind": "buttons missing or different on replica", "items": [f"{a} -> {b}" for a, b in sorted(lb - rb)]})
    if rb - lb: diffs.append({"kind": "buttons on replica only", "items": [f"{a} -> {b}" for a, b in sorted(rb - lb)]})
    ll = {page_target(l["href"]) for l in L["links"]} | {t for _, t in lb}
    rl = {page_target(l["href"]) for l in R["links"]} | {t for _, t in rb}
    ll.discard("page:terms.html"); rl.discard("page:terms.html"); ll.discard("file:popup"); rl.discard("file:popup")
    lonly = sorted(t for t in ll - rl if not t.startswith("web:jtmwebsites"))
    ronly = sorted(t for t in rl - ll if not t.startswith("web:jtmwebsites"))
    if lonly: diffs.append({"kind": "link targets missing from replica", "items": lonly})
    live_text = squash(L["text"])
    clickable = [t for t in ronly if t.startswith(("web:", "file:mailto:"))
                 and squash(re.sub(r"^(web:|file:mailto:)", "", t)) in live_text]
    if clickable:
        ronly = [t for t in ronly if t not in clickable]
        intended.append("Clickable on the replica, plain text on the live page (decision, CHANGELOG section 23): "
                        + ", ".join(re.sub(r"^(web:|file:mailto:)", "", t) for t in clickable) + ".")
    if ronly: diffs.append({"kind": "link targets on replica only", "items": ronly})

    # moving / interactive parts
    lw, rw = L["widgets"], R["widgets"]
    if sorted(lw["galleries"]) != sorted(rw["galleries"]):
        diffs.append({"kind": "galleries differ", "items": [f'live {lw["galleries"]} photos per gallery, replica {rw["galleries"]}']})
    if lw["videos"] != rw["videos"]:
        diffs.append({"kind": "videos differ", "items": [f'live {lw["videos"]}', f'replica {rw["videos"]}']})
    if lw["click_to_enlarge"] and not rw["click_to_enlarge"]:
        diffs.append({"kind": "click-to-enlarge photos not on replica", "items": [f'{lw["click_to_enlarge"]} on live page']})
    if L.get("scroll_in"):
        diffs.append({"kind": "pictures that appear as you scroll down on the live page",
                      "items": [f'{os.path.basename(u)} fades in when scrolled to on the live page; '
                                f'the replica shows it straight away' for u in L["scroll_in"]]})
    ld, rd = {norm(d) for d in L["descriptions"]}, {norm(d) for d in R["descriptions"]}
    if ld - rd: diffs.append({"kind": "photo descriptions missing from replica", "items": sorted(ld - rd)})
    return {"page": name, "live": PAGES[name][0], "replica": PAGES[name][1],
            "counts": {"live": {"sentences": len(lt), "pictures": len(li), "buttons": len(lb), "links": len(ll)},
                       "replica": {"sentences": len(rt), "pictures": len(ri), "buttons": len(rb), "links": len(rl)}},
            "widgets": {"live": lw, "replica": rw}, "differences": diffs, "intended": intended}

if __name__ == "__main__":
    names = sys.argv[1:] or list(PAGES)
    report = [r for r in (compare(n) for n in names) if r]
    for r in report:
        print(f"\n=== {r['page']}  ({r['live']} vs {r['replica']})  {r['counts']}")
        for d in r["differences"]:
            print(f"  - {d['kind']}:")
            for it in d["items"][:12]:
                print(f"      {it[:180]}")
            if len(d["items"]) > 12: print(f"      … and {len(d['items']) - 12} more")
        if not r["differences"]: print("  matches")
    if not sys.argv[1:]:
        json.dump(report, open(os.path.join(HERE, "report.json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)
    print(f"\n{len(report)} pages compared; {sum(1 for r in report if r['differences'])} with differences")
