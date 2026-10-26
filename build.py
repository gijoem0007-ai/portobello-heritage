#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Static-site generator for the Portobello Heritage Trust first-pass clone.
Renders every page from the CONTENT dict below into real .html files,
sharing one header/nav/footer template and css/style.css.
"""
import os, re, html

ROOT = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------- nav data

# Ground truth (Xara Apr 2026 export, desktop layout): the top nav on every page is five plain
# buttons with NO flyouts. The flyouts live on the vertical button bars that appear on
# heritage.htm (category buttons) and events page.htm only. Labels below are verbatim from those
# bars, including the source's own wording ("Georgian houses", "Portobello Love Sories").
MAIN_NAV = [
    ("Home", "index.html"),
    ("Heritage", "heritage.html"),
    ("Events", "events.html"),
    ("Links", "links.html"),
    ("Contact Us", "contact.html"),
]

# (button label, direct link or None, flyout items). A button with a flyout is not a link in the
# ground truth (href="javascript:;"); it only opens its flyout on hover.
HERITAGE_MENU = [
    ("Industry", None, [
        ("Pottery Manufacture", "heritage/pottery-manufacture.html"),
        ("Salt Pans", "heritage/salt-pans.html"),
    ]),
    ("Architecture", None, [
        ("Georgian houses", "heritage/georgian-houses.html"),
        ("Heritage trail leaflet", "heritage/heritage-trail-leaflet.html"),
        ("Chocolate factory", "heritage/chocolate-factory.html"),
    ]),
    ("Culture", None, [
        ("Entertainment", "heritage/entertainment.html"),
        ("Pier", "heritage/pier.html"),
        ("Marine Gardens", "heritage/marine-gardens.html"),
    ]),
    ("At The Sea Side", None, [
        ("Portobello Harbour", "heritage/portobello-harbour.html"),
        ("Beach", "heritage/beach.html"),
        ("Golden Days", "heritage/golden-days.html"),
    ]),
    ("People", None, [
        ("Toddler's Hut", "heritage/toddlers-hut.html"),
        ("Helen Hopekirk", "heritage/helen-hopekirk.html"),
        ("Sir Peter Heatly", "heritage/sir-peter-heatly.html"),
        ("Euphemia (Tot) Addy", "heritage/euphemia-tot-addy.html"),
        ("William Leatham Policeman", "heritage/william-leatham.html"),
        ("Peggy Brown", "heritage/peggy-brown.html"),
        ("Shops and Shopkeepers", "heritage/shops-and-shopkeepers.html"),
        ("High Days and Holidays", "heritage/high-days-and-holidays.html"),
        ("Charles William Schulze and W.M. Ramsay", "heritage/chocolate-factory.html"),
        ("Miss MEG Moir", "heritage/miss-meg-moir.html"),
        ("Prince Philip", "heritage/prince-philip.html"),
        ("Henderson's garage", "heritage/hendersons-garage.html"),
    ]),
    ("Plaques", "heritage/plaques.html", []),
    ("Coade Stone Pillars", None, [
        ("Coade Stone Pillars", "heritage/coade-stone-pillars.html"),
        ("Photos of Coade Stone Pillars", "heritage/photos-of-coade-stone-pillars.html"),
    ]),
    ("Oral History", "heritage/oral-history.html", []),
]

EVENTS_MENU = [
    ("Forthcoming Events", "events/forthcoming-events.html", []),
    ("Archived Events", None, [
        ("Dig Portobello", "events/dig-portobello.html"),
        ("Kiln Celebration", "events/kiln-celebration.html"),
        ("Portobello Love Sories", "events/porty-love-stories.html"),
    ]),
]

# ------------------------------------------------------------ html helpers

def rel(path_from_root, target):
    """target is root-relative (e.g. 'heritage/foo.html' or 'index.html');
    path_from_root is the depth prefix ('' or '../') of the CURRENT page."""
    return path_from_root + target

def render_nav(depth_prefix, current):
    parts = ['<nav class="main-nav">']
    for label, href in MAIN_NAV:
        cls = ' class="active"' if href == current else ''
        parts.append(f'<a href="{rel(depth_prefix, href)}"{cls}>{label}</a>')
    parts.append('</nav>')
    return "\n".join(parts)

def render_side_menu(depth_prefix, menu):
    """Vertical button bar with hover flyouts, as on the ground truth's Heritage and Events pages."""
    out = ['<nav class="subnav side-menu">']
    for label, href, items in menu:
        if not items:
            out.append(f'<div class="sm-item"><a class="sm-btn" href="{rel(depth_prefix, href)}">{label}</a></div>')
            continue
        out.append(f'<div class="sm-item has-flyout"><a class="sm-btn" role="button" tabindex="0" aria-haspopup="true">{label}</a>'
                   '<div class="sm-flyout">')
        out += [f'<a href="{rel(depth_prefix, h)}">&rarr; {html.escape(l)}</a>' for l, h in items]
        out.append('</div></div>')
    out.append('</nav>')
    return "".join(out)

def render_footer(depth_prefix, socials=False):
    # Ground truth: the Facebook/Twitter icons appear only on the home page; every page's footer
    # carries "Terms & Conditions" and the "Created by jtm websites" credit.
    img = rel(depth_prefix, "images/pht/")
    icons = f'''
  <div class="socials">
    <a href="https://www.facebook.com/portyhistory" target="_blank" rel="noopener"><img src="{img}39937.png" alt="Facebook"></a>
    <a href="https://twitter.com/portyhistory" target="_blank" rel="noopener"><img src="{img}39938.png" alt="Twitter"></a>
  </div>''' if socials else ""
    return f'''<footer class="site-footer">{icons}
  <p><a href="{rel(depth_prefix, "terms.html")}">Terms &amp; Conditions</a></p>
  <p><a href="https://jtmwebsites.uk/" target="_blank" rel="noopener">Created by jtm websites</a></p>
  <p class="credit">Local test replica rebuilt from the Xara Apr 2026 export &mdash; not the live Portobello Heritage Trust site.</p>
</footer>'''

PAGE_TEMPLATE = '''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>{title}</title>
<meta name="description" content="{description}">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Lora:ital,wght@0,400;0,600;0,700;1,600&family=Open+Sans:wght@400;600;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="{css}">
</head>
<body>
<header class="site-header">
<a href="{home}"><img class="banner" src="{img}pht/39931.jpg" alt="Portobello Heritage Trust"></a>
</header>
{nav}
<main>
{body}
</main>
{footer}
</body>
</html>
'''

def wrap(title, description, body_html, depth_prefix, current, extra_nav_current=None):
    return PAGE_TEMPLATE.format(
        title=html.escape(title),
        description=html.escape(description),
        css=rel(depth_prefix, "css/style.css"),
        home=rel(depth_prefix, "index.html"),
        img=rel(depth_prefix, "images/"),
        nav=render_nav(depth_prefix, extra_nav_current or current),
        body=body_html,
        footer=render_footer(depth_prefix, socials=(current == "index.html")),
    )

def paragraphs(text, cls="article"):
    """Split on blank lines -> <p> tags. cls picks font style (article=serif quote-y, plain=sans)."""
    blocks = [b.strip() for b in re.split(r'\n\s*\n', text.strip()) if b.strip()]
    out = [f'<div class="{cls}">']
    for b in blocks:
        b = b.replace('\n', ' ')
        out.append(f'<p>{b}</p>')
    out.append('</div>')
    return "\n".join(out)

def figure(img_src, caption, depth_prefix, cls="hero-photo"):
    return f'<figure><img class="{cls}" src="{rel(depth_prefix, "images/"+img_src)}" alt="{html.escape(caption)}"><figcaption>{html.escape(caption)}</figcaption></figure>'

def write_page(rel_path, html_content):
    full = os.path.join(ROOT, rel_path)
    os.makedirs(os.path.dirname(full), exist_ok=True)
    with open(full, "w", encoding="utf-8") as f:
        f.write(html_content)
    print("wrote", rel_path)

print("build.py engine loaded OK")

# =========================================================== GROUND-TRUTH CONTENT
# 2026-09-25 correction pass: every page body is now rendered from content/gt/<page>.json,
# produced by tools/extract_ground_truth.py from the Xara Apr 2026 export (the ground truth).
# The earlier hand-written summaries were condensed paraphrases with invented filler, and
# used cropped screenshots instead of the real images. Images are now the real originals in
# images/pht/ (same numbered filenames as index_htm_files/), downloads the real files in files/.
# See ../CHANGELOG.md (in the "PHT replica website" folder) for the page-by-page record.

import json
from urllib.parse import unquote, quote

GT_DIR = os.path.join(ROOT, "content", "gt")
IMG_EXT = (".jpg", ".jpeg", ".png", ".gif")

# ground-truth page -> clone page (for links between pages)
GT_TO_CLONE = {
    "index.htm": "index.html", "heritage.htm": "heritage.html", "events page.htm": "events.html",
    "links.htm": "links.html", "contact us.htm": "contact.html", "terms.htm": "terms.html",
    "oral history.htm": "heritage/oral-history.html",
    "photos of coade stone pillars.htm": "heritage/photos-of-coade-stone-pillars.html",
    "plaques.htm": "heritage/plaques.html",
    "forthcoming events.htm": "events/forthcoming-events.html",
    "dig portobello.htm": "events/dig-portobello.html",
    "kiln celebration.htm": "events/kiln-celebration.html",
    "porty love stories.htm": "events/porty-love-stories.html",
}
SITE_CHROME = {"index.htm", "heritage.htm", "events page.htm", "links.htm", "contact us.htm",
               "terms.htm", "https://jtmwebsites.uk/", "#"}

def load_gt(name):
    with open(os.path.join(GT_DIR, name + ".json"), encoding="utf-8") as f:
        return json.load(f)

def gt_href(target, d):
    """Map a link found in a ground-truth page to its place in this clone."""
    t = unquote(target)
    if t.startswith("index_htm_files/"):
        name = t.split("/", 1)[1]
        folder = "images/pht/" if name.lower().endswith(IMG_EXT) else "files/"
        return rel(d, folder + quote(name))
    if t in GT_TO_CLONE:
        return rel(d, GT_TO_CLONE[t])
    return target

def asset_exists(target):
    t = unquote(target)
    if not t.startswith("index_htm_files/"):
        return True
    name = t.split("/", 1)[1]
    folder = "images/pht" if name.lower().endswith(IMG_EXT) else "files"
    return os.path.exists(os.path.join(ROOT, folder, name))

def img_tag(src, alt, d, w=None, hover=False):
    name = unquote(src.split("/")[-1])
    stem, ext = os.path.splitext(name)
    url = rel(d, "images/pht/" + quote(name))
    srcset = ""
    if os.path.exists(os.path.join(ROOT, "images", "pht", stem + "@2x" + ext)):
        srcset = f' srcset="{url} 1x, {rel(d, "images/pht/" + quote(stem + "@2x" + ext))} 2x"'
    style = f' style="width:{int(w)}px"' if w else ""
    tag = f'<img class="gt-img" src="{url}"{srcset} alt="{html.escape(alt)}" loading="lazy"{style}>'
    if hover:   # ground truth shows these descriptions as a pop-up on hover; tabindex lets a tap show it too
        tag = f'<span class="hover-tip" tabindex="0" data-tip="{html.escape(alt)}">{tag}</span>'
    return tag

def clean(t):
    t = re.sub(r"(\d) (st|nd|rd|th)\b", r"\1\2", t)      # Xara superscript ordinals: "19 th" -> "19th"
    t = re.sub(r"\bM r\b", "Mr", t)                      # superscript in "Mr"
    return t

URL_RE = re.compile(r"(https?://[^\s<>()]+[^\s<>().,;:!?'\"’”]"
                    r"|www\.[^\s<>()]+[^\s<>().,;:!?'\"’”]"
                    r"|[\w.+-]+@[\w-]+\.[\w.-]*\w)")

def linkify(t):
    out, pos = [], 0
    for m in URL_RE.finditer(t):
        out.append(html.escape(t[pos:m.start()]))
        u = m.group(0)
        glued = re.match(r".*?\.(?:uk|com|org|net)(?=[A-Z])", u)   # e.g. "www.rcahms.gov.ukYou" in the source
        if glued:
            u = glued.group(0)
            out.append(f'<a href="http://{html.escape(u)}" target="_blank" rel="noopener">{html.escape(u)}</a>')
            pos = m.start() + len(u)
            continue
        if "@" in u and not u.startswith("http"):
            out.append(f'<a href="mailto:{html.escape(u)}">{html.escape(u)}</a>')
        else:
            href = u if u.startswith("http") else "http://" + u
            out.append(f'<a href="{html.escape(href)}" target="_blank" rel="noopener">{html.escape(u)}</a>')
        pos = m.end()
    out.append(html.escape(t[pos:]))
    return "".join(out)

def norm_txt(s):
    return re.sub(r"[^a-z0-9]+", " ", s.lower().replace("’", "'")).strip()

CLICK_RE = re.compile(r"^click (here|on)\b", re.I)
MISSING = '<span class="missing-asset">[linked file missing from the ground-truth export]</span>'

HOVER_HINT_RE = re.compile(r"^hover over\b", re.I)
CAPTION_LOG = []   # (page, caption) pairs tied to images; listed at the end of the build

# Xara sliders (Events, Kiln Celebration): photo galleries that fade to the next photo every 4 s
# (Xara's own setting on every slider in the export: 4000 ms per photo, ~0.5 s fade, no buttons).
# Each photo keeps its place in the frame; narrower ones sit on the white panel Xara gives them.
SLIDE_MS = 4000
SLIDER_SCRIPT = '''<script>
(function () {
  var still = window.matchMedia && matchMedia("(prefers-reduced-motion: reduce)").matches;
  document.querySelectorAll(".gt-slider").forEach(function (box) {
    var slides = box.querySelectorAll(".gt-slide"), i = 0;
    if (slides.length < 2) return;
    setInterval(function () {
      if (document.hidden) return;                       // don't race ahead in a background tab
      slides[i].classList.remove("on");
      i = (i + 1) % slides.length;
      slides[i].classList.add("on");
    }, still ? SLIDE_MS_SLOW : SLIDE_MS);
  });
})();
</script>'''.replace("SLIDE_MS_SLOW", str(SLIDE_MS * 2)).replace("SLIDE_MS", str(SLIDE_MS))

def render_slider(b, d, title):
    w, h = b["w"], b["h"]
    pct = lambda v, of: f"{100 * v / of:.3f}%"
    slides = []
    for k, sl in enumerate(b["slides"]):
        tag = img_tag(sl["src"], sl.get("alt") or title, d).replace(' loading="lazy"', "")
        tag = tag.replace("<img ", f'<img style="left:{pct(sl["left"], w)};top:{pct(sl["top"], h)};'
                                   f'width:{pct(sl["w"], w)};height:{pct(sl["h"], h)}" ', 1)
        slides.append(f'<div class="gt-slide{" on" if k == 0 else ""}">{tag}</div>')
    return (f'<div class="gt-slider" style="max-width:{int(w)}px;aspect-ratio:{int(w)}/{int(h)}" '
            f'role="img" aria-label="{html.escape(title)}: slideshow of {len(slides)} photos">'
            + "".join(slides) + "</div>")

# ---------------------------------------------------------------- membership form
# The ground truth's membership pop-up (Contact; Home has a button for it too): the application
# form, then "How to Pay". It posts to process-form.php at the site root (kept in this folder and
# uploaded with the site), which emails the application to the Trust. Previews (this PC, the NAS)
# can't run PHP, so there the form says it can't send instead of trying.
MEMBERSHIP_BUTTON = ('<button type="button" class="btn mf-open" aria-haspopup="dialog">'
                     'Membership Application Form</button>')

def membership_form(d):
    fields = [("name", "Name", "text", "name"), ("address", "Address", "textarea", "street-address"),
              ("postcode", "Post code", "text", "postal-code"), ("phone", "Telephone Number", "tel", "tel"),
              ("email", "E-mail Address", "email", "email")]
    rows = []
    for fid, label, kind, auto in fields:
        inp = (f'<textarea id="mf-{fid}" name="{fid}" required autocomplete="{auto}"></textarea>' if kind == "textarea"
               else f'<input id="mf-{fid}" name="{fid}" type="{kind}" required autocomplete="{auto}">')
        rows.append(f'<label for="mf-{fid}">{label}</label>{inp}')
    return f'''<dialog class="mf-dialog" aria-labelledby="mf-title">
<div class="mf-card">
<button type="button" class="mf-close" aria-label="Close">&times;</button>
<h2 id="mf-title">Membership Application Form</h2>
<div class="mf-done" role="alert" tabindex="-1" hidden>
<p class="mf-done-tick" aria-hidden="true">&#10004;</p>
<p class="mf-done-title">Thank you &ndash; your application has been submitted!</p>
<p>Your annual membership subscription can be paid using either of the methods below.</p>
<button type="button" class="btn mf-done-close">Close</button>
</div>
<form class="mf-form" novalidate>
{"".join(rows)}
<label for="mf-skills">Are there any areas in which you would be willing to offer advice/skills?</label>
<textarea id="mf-skills" name="skills"></textarea>
<div class="mf-check"><input id="mf-agree" name="agree" type="checkbox" required>
<label for="mf-agree">I agree to my details and information, as given above, being included in the membership directory of Portobello Heritage Trust. My details will not be passed on to any other individual or organisation.</label></div>
<label for="mf-signature">Typed Signature (type your full name)</label>
<input id="mf-signature" name="signature" type="text" required autocomplete="name">
<div class="mf-trap" aria-hidden="true"><label for="mf-website">Leave this empty</label>
<input id="mf-website" name="website" type="text" tabindex="-1" autocomplete="off"></div>
<button type="submit" class="btn mf-submit">Submit Application</button>
<p class="mf-msg" role="status" aria-live="polite"></p>
</form>
<h3>How to Pay</h3>
<p><strong>Annual Membership Subscription: &pound;10</strong></p>
<p>Donations to the Trust are very welcome and may be paid using either method below.</p>
<p><strong>(a) Cheque</strong><br>Made payable to Portobello Heritage Trust, sent to:<br>Stephen Hawkins &ndash; PHT Treasurer<br>12 West Brighton Crescent, Edinburgh EH15 1LU</p>
<p><strong>(b) Electronic Transfer</strong><br>Sort Code: 80&ndash;18-31<br>Account No: 06002462<br>Account Name: Portobello Heritage Trust<br>Payment Reference: Your name</p>
</div>
</dialog>
<script>
(function () {{
  var dlg = document.querySelector(".mf-dialog"), form = dlg.querySelector(".mf-form"), msg = dlg.querySelector(".mf-msg");
  var done = dlg.querySelector(".mf-done"), submit = form.querySelector(".mf-submit");
  var preview = location.protocol === "file:" || /^(localhost|127\\.|192\\.168\\.|10\\.|[^.]+\\.[^.]+\\.ts\\.net$)/.test(location.hostname);
  function say(text) {{ msg.textContent = text; msg.scrollIntoView({{block: "nearest"}}); }}
  function busy(on) {{ submit.disabled = on; submit.textContent = on ? "Sending\\u2026" : "Submit Application"; }}
  function fresh() {{ done.hidden = true; form.hidden = false; msg.textContent = ""; busy(false); }}
  document.querySelectorAll(".mf-open").forEach(function (b) {{ b.addEventListener("click", function () {{
    if (!done.hidden) fresh();                       // after a sent application, start again with an empty form
    dlg.showModal();
  }}); }});
  dlg.querySelector(".mf-close").addEventListener("click", function () {{ dlg.close(); }});
  dlg.querySelector(".mf-done-close").addEventListener("click", function () {{ dlg.close(); }});
  dlg.addEventListener("click", function (e) {{ if (e.target === dlg) dlg.close(); }});
  form.addEventListener("submit", function (e) {{
    e.preventDefault();
    if (!form.reportValidity()) {{ say("Please fill in all the boxes and tick the agreement."); return; }}
    if (preview) {{ say("This is a preview copy of the website, so the form can't send from here. It sends from the real website."); return; }}
    busy(true); msg.textContent = "";
    fetch("{rel(d, "process-form.php")}", {{ method: "POST", body: new FormData(form) }})
      .then(function (r) {{ return r.json(); }})
      .then(function (result) {{
        if (result.success) {{                         // replace the form with a clear confirmation, at the top
          form.reset(); form.hidden = true; done.hidden = false;
          dlg.scrollTop = 0; done.focus();
        }} else {{ busy(false); say(result.error || "Something went wrong. Please try again."); }}
      }})
      .catch(function () {{ busy(false); say("Something went wrong. Your details are still here, so please try again."); }});
  }});
}})();
</script>'''

def render_gt(name, d, title, img_links=False, popup_min_w=None):
    """Render a ground-truth page body. `title` becomes the h1; if the page's first paragraph
    is that title (optionally run together with a byline), it is consumed, not repeated."""
    page = load_gt(name)
    blocks = page["blocks"]
    # content links = links that are not site chrome / nav / social / buttons, in page order
    btn_targets = {b["href"] for b in blocks if b["type"] == "button"}
    content_links = [l for l in page["links"]
                     if l not in SITE_CHROME and l not in btn_targets and "twitter.com" not in l
                     and "facebook.com" not in l and not l.endswith(".htm") and "ehive.com" not in l]
    n_click = sum(1 for b in blocks if b["type"] == "text" for p in b["paras"] if CLICK_RE.match(p))
    click_links = list(content_links) if n_click == len(content_links) else []
    img_links_q = list(content_links) if (img_links and not click_links) else []
    used = set()

    popups = []
    if popup_min_w:
        popups = [b for b in blocks if b["type"] == "img" and (b.get("w") or 0) >= popup_min_w]
        blocks = [b for b in blocks if b not in popups]

    # Captions: in the ground truth an image label is a short one-line text box placed directly
    # under that image. Tie each such label to its own image (as a <figcaption>) by position,
    # instead of letting it render as a loose paragraph after the whole row.
    captions, cap_blocks = {}, set()
    imgs = [b for b in blocks if b["type"] == "img" and b.get("h")]
    def is_caption(t, im):
        if t.get("side"):                # label set beside the image, ending just left of it
            return -10 <= im["left"] - t["right"] <= 40 and im["top"] <= t["top"] <= im["top"] + im["h"]
        n, gap, dl = len(t["paras"][0]), t["top"] - (im["top"] + im["h"]), t["left"] - im["left"]
        if n <= 40:                      # short label, may be centred under the image
            return -8 <= gap <= 55 and -80 <= dl <= im["w"] * 0.6
        if n <= 90:                      # one-line caption, left-aligned with the image
            return -8 <= gap <= 45 and -25 <= dl <= im["w"] * 0.6
        if n <= 170:                     # long "Figure N ..." caption: must hug the image
            return -8 <= gap <= 20 and abs(dl) <= 15
        return False

    for t in blocks:
        if t["type"] != "text" or len(t["paras"]) != 1:
            continue
        best = None
        for im in imgs:
            gap = im["left"] - t["right"] if t.get("side") else t["top"] - (im["top"] + im["h"])
            if is_caption(t, im) and id(im) not in captions:
                if best is None or gap < best[0]:
                    best = (gap, im)
        if best:
            captions[id(best[1])] = clean(t["paras"][0])
            cap_blocks.add(id(t))
    # Gallery captions: a one-line text box set just below a slider and within its width
    # (Events: "Photo Gallery of Kiln Celebrations" ~43 px under its gallery).
    for s in (b for b in blocks if b["type"] == "slider"):
        for t in blocks:
            if (t["type"] == "text" and len(t["paras"]) == 1 and id(t) not in cap_blocks
                    and 0 <= t["top"] - (s["top"] + s["h"]) <= 80 and s["left"] - 150 <= t["left"] <= s["left"] + s["w"]):
                captions[id(s)] = clean(t["paras"][0])
                cap_blocks.add(id(t))
                break
    blocks = [b for b in blocks if id(b) not in cap_blocks]
    CAPTION_LOG.extend((name, c) for c in captions.values())

    out = [f'<h1 class="page-title">{html.escape(clean(title))}</h1>']
    first_para, after_title, prev_img, embeds, buttons = True, False, False, [], []
    i = 0
    while i < len(blocks):
        b = blocks[i]
        if b["type"] == "img":
            row = [b]
            while (i + 1 < len(blocks) and blocks[i + 1]["type"] == "img"
                   and abs(blocks[i + 1]["top"] - b["top"]) <= 24):
                i += 1
                row.append(blocks[i])
            row = [r for r in row if not r["src"].endswith(("39937.png", "39938.png"))]  # social icons -> footer
            if not row:
                i += 1
                continue
            # image links (e.g. leaflet thumbnails -> full pages) belong to the row that has one
            # image per link, not to whichever images happen to come first
            link_row = bool(img_links_q) and len(row) == len(img_links_q)
            items = []
            for r in row:
                tag = img_tag(r["src"], r.get("alt") or title, d, r.get("w"), hover=bool(r.get("alt")))
                if link_row:
                    l = img_links_q.pop(0)
                    used.add(l)
                    tag = f'<a href="{gt_href(l, d)}" target="_blank" rel="noopener">{tag}</a>'
                cap = captions.get(id(r))
                if cap:   # caption sits outside the link: the image is the click target, the label is not
                    w = f' style="max-width:{int(r["w"])}px"' if r.get("w") else ""
                    tag = (f'<figure class="gt-fig"{w}>{tag}'
                           f'<figcaption class="gt-cap">{html.escape(cap)}</figcaption></figure>')
                items.append(tag)
            cls = "gt-figure" if len(row) == 1 else "gt-row"
            out.append(f'<div class="{cls}">' + "".join(items) + "</div>")
            prev_img = True
        elif b["type"] == "text":
            signoffs = {clean(s) for s in b.get("signoffs", ())}
            for p in b["paras"]:
                p = clean(p)
                if b.get("align") == "center":             # notice set by hand, e.g. "No further events planned"
                    out.append(f'<p class="center">{linkify(p)}</p>')
                    prev_img = False
                    continue
                if p in signoffs:                          # right-aligned author sign-off
                    out.append(f'<p class="signoff">{html.escape(p)}</p>')
                    prev_img = False
                    continue
                if first_para:
                    first_para = False
                    nt, np_ = norm_txt(title), norm_txt(p)
                    if np_ == nt:
                        after_title = True
                        continue
                    if np_.startswith(nt + " "):          # "Title Byline" run together
                        out.append(f'<h3 class="byline">{html.escape(p[len(clean(title)):].strip())}</h3>')
                        continue
                if after_title:
                    after_title = False
                    if len(p) < 70 and not p.rstrip().endswith("."):   # author / subtitle line under the title
                        out.append(f'<h3 class="byline">{html.escape(p)}</h3>')
                        continue
                if CLICK_RE.match(p) and click_links:
                    l = click_links.pop(0)
                    used.add(l)
                    if asset_exists(l):
                        out.append(f'<p class="gt-click"><a href="{gt_href(l, d)}" target="_blank" '
                                   f'rel="noopener">{html.escape(p)}</a></p>')
                    else:
                        out.append(f'<p class="gt-click">{html.escape(p)} {MISSING}</p>')
                    continue
                if HOVER_HINT_RE.match(p):                     # "Hover over each Photo to see description."
                    out.append(f'<p class="gt-hint">{html.escape(p)}</p>')
                    continue
                short = len(p) < 70 and not p.rstrip().endswith((".", ",", ";", ":", "?", "!", "’", "'", '"', "”"))
                if short and prev_img:
                    out.append(f'<p class="caption">{linkify(p)}</p>')
                    continue                                   # consecutive captions stay captions
                elif short and not re.match(r"^[\(\[\d]", p):
                    out.append(f'<h2 class="section-title gt-sub">{linkify(p)}</h2>')
                else:
                    out.append(f'<p>{linkify(p)}</p>')
                prev_img = False
            prev_img = prev_img and out[-1].startswith('<p class="caption">')
        elif b["type"] == "slider":
            cap = captions.get(id(b))
            if cap:
                out.append(f'<figure class="gt-gallery">{render_slider(b, d, cap)}'
                           f'<figcaption>{html.escape(cap)}</figcaption></figure>')
            else:
                out.append(render_slider(b, d, title))
            prev_img = False
        elif b["type"] == "embed":
            embeds.append(b)
        elif b["type"] == "button":
            buttons.append(b)
        i += 1

    # a short name-like line closing the article is the author's sign-off, not a heading
    last = out[-1]
    m_sig = re.fullmatch(r'<h2 class="section-title gt-sub">([A-Z][A-Za-z.’ -]{2,40})</h2>', last)
    if m_sig and len(out) > 2:
        out[-1] = f'<p class="signoff">{m_sig.group(1)}</p>'
    if popups:
        out.append('<div class="gt-popups">' + "".join(
            f'<div class="gt-figure">{img_tag(p["src"], p.get("alt") or title, d, p.get("w"))}</div>'
            for p in popups) + "</div>")
    if embeds:
        out.append('<div class="gt-embeds">' + "".join(
            f'<div class="embed"><iframe src="{html.escape(e["src"])}" title="{html.escape(e["title"] or title)}" '
            f'loading="lazy" allow="accelerometer; clipboard-write; encrypted-media; gyroscope; '
            f'picture-in-picture; web-share" referrerpolicy="strict-origin-when-cross-origin" '
            f'allowfullscreen></iframe></div>' for e in embeds) + "</div>")
    # a web address already written (and so linked) in the page text isn't a leftover link
    def bare(u):
        return re.sub(r"^(https?://)?(www\.)?", "", unquote(u).strip().lower()).rstrip("/")
    page_text = " ".join(bare(w) for b in blocks if b["type"] == "text" for p in b["paras"] for w in p.split())
    used.update(l for l in content_links if l.startswith(("http", "www.")) and bare(l) in page_text)
    for l in (l for l in content_links if l not in used):
        label = unquote(l.split("/")[-1])
        if asset_exists(l):
            out.append(f'<p class="gt-click"><a href="{gt_href(l, d)}" target="_blank" rel="noopener">'
                       f'{html.escape(label)}</a></p>')
        else:
            out.append(f'<p class="gt-click">{html.escape(label)} {MISSING}</p>')
    btns = []
    want_form = False
    for bt in buttons:
        if bt["label"] == "Membership Application Form":   # Home: opens the membership pop-up (Xara links it to "#")
            btns.append(MEMBERSHIP_BUTTON); want_form = True
            continue
        if bt.get("inactive"):          # shown greyed out in Xara, goes nowhere (Events: "Back to Events Page")
            btns.append(f'<span class="btn btn-inactive" aria-disabled="true">{html.escape(bt["label"])}</span>')
            continue
        if bt["href"] == "#":
            continue
        if asset_exists(bt["href"]):
            tgt = ' target="_blank" rel="noopener"' if bt["href"].startswith(("http", "index_htm_files")) else ""
            btns.append(f'<a class="btn" href="{gt_href(bt["href"], d)}"{tgt}>{html.escape(bt["label"])}</a>')
        else:
            btns.append(f'<span class="btn btn-missing" title="Linked file missing from the ground-truth '
                        f'export">{html.escape(bt["label"])}</span>')
    if btns:
        out.append('<div class="btn-row">' + "".join(btns) + "</div>")
    if want_form:
        out.append(membership_form(d))
    if any(b["type"] == "slider" for b in blocks):
        out.append(SLIDER_SCRIPT)
    return "\n".join(out)

def sidebar(d):
    return render_side_menu(d, HERITAGE_MENU)

def events_sidebar(d):
    return render_side_menu(d, EVENTS_MENU)

# ---------------------------------------------------------------- oral history
# Each chapter has a "Video Essay" and an "Audio File" button that open a YouTube player in a pop-up.
# Chapters, video ids and button artwork come from content/extras/oral-history.json (written by the
# import step, tools/xara_extras.py). To add a chapter, add it to that file.
def load_extras(name):
    with open(os.path.join(ROOT, "content", "extras", name + ".json"), encoding="utf-8") as f:
        return json.load(f)

OH_PLAYER = '''<dialog class="oh-player" aria-label="Video player">
<div class="oh-head"><span class="oh-title"></span><button type="button" class="oh-close" aria-label="Close">&times;</button></div>
<div class="oh-frame"></div>
</dialog>
<script>
(function () {
  var dlg = document.querySelector(".oh-player"), frame = dlg.querySelector(".oh-frame");
  document.querySelectorAll(".oh-btn").forEach(function (b) {
    b.addEventListener("click", function () {
      dlg.querySelector(".oh-title").textContent = b.dataset.title;
      // YouTube refuses embeds that can't say which site they're on (error 153). A page opened
      // straight from disk (file://) has no site address, so explain in the box instead of failing.
      if (location.protocol === "file:") {
        frame.innerHTML = '<div class="oh-msg">This video can\\'t play because the page was opened straight from ' +
          'the drive. Double-click <b>Preview replica.bat</b> in the portobello-clone folder and the videos ' +
          'will play here, just as they will on the live website.</div>';
        dlg.showModal();
        return;
      }
      frame.innerHTML = '<iframe src="https://www.youtube-nocookie.com/embed/' + b.dataset.video +
        '?autoplay=1&rel=0' + (b.dataset.start ? '&start=' + b.dataset.start : '') + '" title="' + b.dataset.title.replace(/"/g, "&quot;") + '" allow="autoplay; encrypted-media; ' +
        'picture-in-picture; fullscreen" referrerpolicy="strict-origin-when-cross-origin" allowfullscreen></iframe>';
      dlg.showModal();
    });
  });
  function close() { frame.innerHTML = ""; if (dlg.open) dlg.close(); }          // removing the player stops playback
  dlg.querySelector(".oh-close").addEventListener("click", close);
  dlg.addEventListener("click", function (e) { if (e.target === dlg) close(); });   // click outside the player
  dlg.addEventListener("cancel", function (e) { e.preventDefault(); close(); });    // Esc
  document.addEventListener("keydown", function (e) { if (e.key === "Escape" && dlg.open) close(); });
  dlg.addEventListener("close", function () { frame.innerHTML = ""; });
})();
</script>'''

def oral_history_clips(slug, d):
    """'Hear it remembered' buttons for a heritage page: moments from the Oral History video essays
    (content/extras/oral-history-clips.json, kept by hand), each opening the pop-up player at that moment."""
    data = load_extras("oral-history-clips")
    clips = [c for c in data["clips"] if c["page"] == slug]
    if not clips:
        return ""
    chapters = {c["title"].split()[0]: c for c in load_extras("oral-history")["chapters"]}
    items = []
    for c in clips:
        ch = chapters[c["chapter"]]                     # KeyError = the clip names a chapter that isn't on the page
        m, sec = divmod(c["start"], 60)
        title = f'{data["speaker"]}: {ch["title"]} (from {m}:{sec:02d})'
        items.append(f'<li><button type="button" class="oh-btn oh-clip" data-video="{ch["video"]}" '
                     f'data-start="{c["start"]}" data-title="{html.escape(title)}">'
                     f'<span class="oh-play" aria-hidden="true">&#9654;</span>'
                     f'<span class="oh-quote">&ldquo;{html.escape(c["quote"])}&rdquo;</span>'
                     f'<span class="oh-src">{html.escape(data["speaker"])}, {html.escape(ch["title"])}</span></button></li>')
    return (f'<aside class="oh-clips"><h2>Hear it remembered</h2>'
            f'<p>From the <a href="{d}heritage/oral-history.html">Portobello Oral History Archive</a>.</p>'
            f'<ul>{"".join(items)}</ul></aside>\n{OH_PLAYER}')

def oral_history_body(d):
    extras = load_extras("oral-history")
    art = {k: (v["label"], v["image"], v["hover"], v["width"]) for k, v in extras["buttons"].items()}
    paras = [clean(p) for b in load_gt("oral history")["blocks"] if b["type"] == "text" for p in b["paras"]]
    title, intro, speaker, chapter_titles = paras[0], paras[1], paras[2], paras[3:]
    oral_history = [(c["title"], c["video"], c["audio"]) for c in extras["chapters"]]
    assert [c for c, _, _ in oral_history] == chapter_titles, (chapter_titles, "chapter list vs page text mismatch")
    for c in oral_history:
        print("  [oral history]", c)

    def btn(kind, vid, chapter):
        label, img, ro, w = art[kind]
        return (f'<button type="button" class="oh-btn" data-video="{vid}" '
                f'data-title="{html.escape(chapter)} ({label})" aria-label="{label}: {html.escape(chapter)}">'
                f'{img_tag(img, label, d, w)}{img_tag(ro, label, d, w).replace("gt-img", "gt-img oh-ro")}</button>'
                ).replace(' loading="lazy"', '')
    out = [f'<h1 class="page-title">{html.escape(title)}</h1>',
           f'<p class="oh-intro">{html.escape(intro)}</p>',
           f'<h2 class="oh-speaker">{html.escape(speaker)}</h2>']
    for chapter, video, audio in oral_history:
        out.append(f'<div class="oh-chapter"><h3>{html.escape(chapter)}</h3>'
                   f'<div class="oh-btns">{btn("video", video, chapter)}{btn("audio", audio, chapter)}</div></div>')
    out.append(OH_PLAYER)
    return "\n".join(out)

ZOOM_SCRIPT = '''<script>
(function () {
  // magnify the large photo under the pointer (mouse: hover; touch: tap to zoom, tap again to stop)
  document.querySelectorAll(".zoom-tile").forEach(function (t) {
    var frame = t.querySelector(".zoom-frame");
    function at(e) {
      var r = frame.getBoundingClientRect();
      var x = Math.min(100, Math.max(0, (e.clientX - r.left) / r.width * 100));
      var y = Math.min(100, Math.max(0, (e.clientY - r.top) / r.height * 100));
      frame.style.backgroundPosition = x + "% " + y + "%";
    }
    frame.addEventListener("pointerenter", function (e) { if (e.pointerType === "mouse") { t.classList.add("zooming"); at(e); } });
    frame.addEventListener("pointermove", function (e) {   // also starts the zoom if the page opened under the pointer
      if (e.pointerType === "mouse") t.classList.add("zooming");
      if (t.classList.contains("zooming")) at(e);
    });
    frame.addEventListener("pointerleave", function (e) { if (e.pointerType === "mouse") t.classList.remove("zooming"); });
    frame.addEventListener("pointerdown", function (e) {
      if (e.pointerType === "mouse") return;
      t.classList.toggle("zooming"); at(e);
    });
    frame.addEventListener("keydown", function (e) {
      if (e.key === "Enter" || e.key === " ") { e.preventDefault(); t.classList.toggle("zooming"); frame.style.backgroundPosition = "50% 50%"; }
    });
  });
})();
</script>'''

def coade_photos_body(d):
    """Photos of Coade Stone Pillars: a grid of photos with descriptions on hover, then photos to
    zoom into (from content/extras/photos-of-coade-stone-pillars.json)."""
    g = load_extras("photos-of-coade-stone-pillars")
    out = ['<h1 class="page-title">Photos of Coade Stone Pillars</h1>']
    if g["grid_hint"]:
        out.append(f'<p class="gt-hint">{html.escape(g["grid_hint"])}</p>')
    tiles = []
    for p in g["grid"]:
        alt = p["description"]
        img = img_tag(p["image"], alt or "Coade Stone Pillars", d)
        tiles.append(f'<span class="hover-tip" tabindex="0" data-tip="{html.escape(alt)}">{img}</span>' if alt else img)
    out.append('<div class="mosaic-grid">' + "".join(tiles) + "</div>")
    if g["zoom_hint"]:
        out.append(f'<p class="gt-hint">{html.escape(g["zoom_hint"])}</p>')
    zt = []
    for p in g["zoom"]:
        url = rel(d, "images/pht/" + quote(p["image"]))
        cap = p["caption"]
        zt.append(f'<figure class="zoom-tile"><div class="zoom-frame" tabindex="0" role="img" '
                  f'aria-label="{html.escape(cap)} (zoomable photo)" style="background-image:url(\'{url}\')">'
                  f'<img src="{url}" alt="{html.escape(cap)}" loading="lazy"></div>'
                  f'<figcaption>{html.escape(cap)}</figcaption></figure>')
    out.append('<div class="zoom-grid">' + "".join(zt) + "</div>")
    for b in load_gt("photos of coade stone pillars")["blocks"]:          # the page's own buttons
        if b["type"] == "button" and b["href"] != "#":
            out.append(f'<div class="btn-row"><a class="btn" href="{gt_href(b["href"], d)}">{html.escape(b["label"])}</a></div>')
    out.append(ZOOM_SCRIPT)
    print(f"  [coade photos] {len(g['grid'])} grid photos, {len(g['zoom'])} zoom photos, "
          f"{sum('data-tip' in t for t in tiles)} with descriptions")
    return "\n".join(out)

PLAQUES_SCRIPT = '''<script>
(function () {
  var dlg = document.querySelector(".pl-dialog"), img = dlg.querySelector(".pl-panel"), txt = dlg.querySelector(".pl-text");
  document.querySelectorAll(".pl-thumb").forEach(function (b) {
    b.addEventListener("click", function () {
      img.src = b.dataset.panel; img.alt = b.dataset.text; txt.textContent = b.dataset.text;
      dlg.showModal();
    });
  });
  dlg.querySelector(".pl-close").addEventListener("click", function () { dlg.close(); });
  dlg.addEventListener("click", function (e) { if (e.target === dlg) dlg.close(); });
})();
</script>'''

def plaques_body(d):
    """Plaques: the plaque photos; clicking one pops up its details panel (a picture of text), as on
    the live site. On phones the panel's words are also shown as text, as the picture gets too small."""
    g = load_extras("plaques")
    out = ['<h1 class="page-title">Plaques</h1>']
    if g["hint"]:
        out.append(f'<p class="gt-hint">{html.escape(g["hint"])}</p>')
    tiles = []
    for p in g["plaques"]:
        label = (p["name"][:60] + "…") if len(p["name"]) > 60 else p["name"]
        tiles.append(f'<button type="button" class="pl-thumb" aria-haspopup="dialog" '
                     f'aria-label="{html.escape(label)}: show details" '
                     f'data-panel="{rel(d, "images/pht/" + quote(p["panel"]))}" data-text="{html.escape(p["text"])}">'
                     f'{img_tag(p["thumb"], label, d, p["w"])}</button>')
    out.append('<div class="pl-grid">' + "".join(tiles) + "</div>")
    out.append('<dialog class="pl-dialog" aria-label="Plaque details"><div class="pl-card">'
               '<button type="button" class="pl-close" aria-label="Close">&times;</button>'
               '<img class="pl-panel" src="" alt=""><p class="pl-text"></p></div></dialog>')
    for b in load_gt("plaques")["blocks"]:                                # the page's own buttons
        if b["type"] == "button" and b["href"] not in (None, "#"):
            out.append(f'<div class="btn-row"><a class="btn" href="{gt_href(b["href"], d)}">{html.escape(b["label"])}</a></div>')
    out.append(PLAQUES_SCRIPT)
    return "\n".join(out)

def gt_heritage_page(slug, gt_name, title, head_title=None, **kw):
    d = "../"
    body = (f'<div class="two-col">{sidebar(d)}<div class="content">{render_gt(gt_name, d, title, **kw)}'
            f'{oral_history_clips(slug, d)}</div></div>')
    head = head_title or title
    write_page(f"heritage/{slug}.html", wrap(head, f"Portobello Heritage Trust - {head}", body, d,
                                              "heritage.html", extra_nav_current="heritage.html"))

def gt_events_page(slug, gt_name, title, **kw):
    d = "../"
    body = f'<div class="container">{render_gt(gt_name, d, title, **kw)}</div>'
    write_page(f"events/{slug}.html", wrap(title, f"Portobello Heritage Trust - {title}", body, d,
                                            "events.html", extra_nav_current="events.html"))

# =========================================================== TOP-LEVEL PAGES

# HOME: ground-truth index.htm (hero 40841.jpg, welcome text, Catalogue button -> ehive)
home_body = '<div class="container">' + render_gt("index", "", "Portobello Heritage Trust") + "</div>"
# Membership button: directly under the "Join the Portobello Heritage Trust…" paragraph, as on the live page
_join = re.search(r'<p>Join the Portobello Heritage Trust.*?</p>', home_body, re.S)
if _join and MEMBERSHIP_BUTTON in home_body:                     # other buttons (Catalogue) stay put
    home_body = home_body.replace(MEMBERSHIP_BUTTON, "", 1).replace('<div class="btn-row"></div>', "")
    home_body = home_body.replace(_join.group(0), _join.group(0) + f'<div class="btn-row">{MEMBERSHIP_BUTTON}</div>', 1)
write_page("index.html", wrap("Portobello Heritage Trust", "Portobello Heritage Trust Home Page",
                              home_body, "", "index.html"))

# HERITAGE index: the ground truth has no text here, only the animated banner (phtgif04.gif)
# and the category buttons (reproduced as the sidebar).
heritage_heading = "".join(f'<h1 class="page-title">{html.escape(clean(p))}</h1>' for b in load_gt("heritage")["blocks"]
                           if b["type"] == "text" for p in b["paras"])   # Xara: the underlined "Heritage" heading
heritage_index_body = (f'<div class="two-col">{sidebar("")}<div class="content">{heritage_heading}'
                       f'<div class="gt-figure">{img_tag("index_htm_files/phtgif04.gif", "Portobello Heritage", "", 439)}</div>'
                       '</div></div>')
write_page("heritage.html", wrap("Heritage", "Portobello Heritage Trust - Heritage",
                                 heritage_index_body, "", "heritage.html"))

# EVENTS index: the ground truth has no text, only four image slideshows of past events.
events_index_body = (f'<div class="two-col">{events_sidebar("")}<div class="content">'
                     + render_gt("events page", "", "Events") + "</div></div>")
write_page("events.html", wrap("Events", "Portobello Heritage Trust, Edinburgh, events page",
                               events_index_body, "", "events.html"))

links_body = '<div class="container">' + render_gt("links", "", "Websites to aid your research") + "</div>"
write_page("links.html", wrap("Links", "Portobello Heritage Trust website - Links", links_body, "", "links.html"))

# CONTACT: ground-truth text + its two PDF buttons, and the Membership Application Form button
# (the ground truth's pop-up form, with "How to Pay" beneath it, as on the live page).
contact_body = ('<div class="container">' + render_gt("contact us", "", "Contact Us")
                + f'<div class="btn-row">{MEMBERSHIP_BUTTON}</div>' + membership_form("") + '</div>')
write_page("contact.html", wrap("Contact Us", "Portobello Heritage Trust, contact us", contact_body, "", "contact.html"))

terms_body = '<div class="container">' + render_gt("terms", "", "Terms & Conditions") + "</div>"
write_page("terms.html", wrap("Terms & Conditions", "Portobello Heritage Trust website - Terms & Conditions",
                              terms_body, "", "terms.html"))

# =========================================================== HERITAGE SUB-PAGES

gt_heritage_page("pottery-manufacture", "pottery manufacture", "Portobello Pottery")
gt_heritage_page("salt-pans", "salt pans", "Joppa Salt Works")
gt_heritage_page("georgian-houses", "georgian houses",
                 "The Architectural Development of Portobello in the early 19th Century")
gt_heritage_page("heritage-trail-leaflet", "heritage trail leaflet", "Architecture Heritage Trail Leaflet",
                 img_links=True)
gt_heritage_page("chocolate-factory", "chocolate factory", "Chocolate Factory")
gt_heritage_page("entertainment", "entertainment", "That was Entertainment")
gt_heritage_page("pier", "pier", "When Portobello Got its Pier!")
gt_heritage_page("marine-gardens", "marine gardens", "Marine Gardens")
gt_heritage_page("portobello-harbour", "portobello harbour", "Harbour Walls")
gt_heritage_page("beach", "beach", "Portobello Beach")
gt_heritage_page("golden-days", "golden days", "Golden Days")
gt_heritage_page("toddlers-hut", "toddlers hut", "BACK TO THE FUTURE", head_title="Toddler's Hut")
gt_heritage_page("helen-hopekirk", "helen hopkirk", "HELEN HOPEKIRK (1856 – 1945)", head_title="Helen Hopekirk")
gt_heritage_page("sir-peter-heatly", "sir peter heatly", "Sir Peter Heatly")
gt_heritage_page("euphemia-tot-addy", "euphemia tot addy", "Euphemia (Tot) Addy")
gt_heritage_page("william-leatham", "william leatham", "William Leatham Policeman")
gt_heritage_page("peggy-brown", "peggy brown", "Peggy Brown (neé Hume)")
gt_heritage_page("shops-and-shopkeepers", "shops and shopkeepers", "Some Characters and Shopkeepers of Portobello")
gt_heritage_page("high-days-and-holidays", "high days and holidays", "High Days and Holidays")
gt_heritage_page("miss-meg-moir", "miss meg moir", "M.E.G. MOIR", head_title="Miss M.E.G. Moir")
gt_heritage_page("prince-philip", "prince phillip", "Prince Philip Visits Portobello")
gt_heritage_page("hendersons-garage", "hendersons garage", "Henderson’s Garage")
write_page("heritage/plaques.html", wrap(
    "Plaques", "Portobello Heritage Trust - Plaques",
    f'<div class="two-col">{sidebar("../")}<div class="content">{plaques_body("../")}</div></div>',
    "../", "heritage.html", extra_nav_current="heritage.html"))
gt_heritage_page("coade-stone-pillars", "coade stone pillars", "The Portobello Coade Stone Pillars")
write_page("heritage/photos-of-coade-stone-pillars.html", wrap(
    "Photos of Coade Stone Pillars", "Portobello Heritage Trust - Photos of Coade Stone Pillars",
    f'<div class="two-col">{sidebar("../")}<div class="content">{coade_photos_body("../")}</div></div>',
    "../", "heritage.html", extra_nav_current="heritage.html"))
write_page("heritage/oral-history.html", wrap(
    "Portobello Oral History Archive", "Portobello Heritage Trust - Portobello Oral History Archive",
    f'<div class="two-col">{sidebar("../")}<div class="content">{oral_history_body("../")}</div></div>',
    "../", "heritage.html", extra_nav_current="heritage.html"))

# =========================================================== EVENTS SUB-PAGES

gt_events_page("forthcoming-events", "forthcoming events", "Forthcoming Events")
gt_events_page("dig-portobello", "dig portobello", "Dig Portobello")
gt_events_page("kiln-celebration", "kiln celebration", "Kiln Community Celebration")
gt_events_page("porty-love-stories", "porty love stories", "Portobello Love Stories")

print(f"\n{len(CAPTION_LOG)} captions tied to their images:")
for pg, cap in CAPTION_LOG:
    print(f"  [{pg}] {cap}")
print("\nAll pages generated.")
