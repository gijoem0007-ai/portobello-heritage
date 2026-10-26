r"""Import step for the parts of the site that Xara builds from scripts and pop-ups rather than page
text: the Oral History chapters (buttons -> pop-up -> YouTube player) and the Photos of Coade Stone
Pillars galleries (mosaic + zoom widgets). Run by extract_ground_truth.py after the pages.

Writes plain data files to content\extras\ and copies the pictures they use into images\pht\.
build.py reads only those files, never the Xara export, so once the replica is the master copy
this step (and the whole import) can simply stop being run."""
import json, os, re, shutil

GT = r"N:\Websites\Portobello heritage\Xara Apr 2026"
GT_FILES = os.path.join(GT, "index_htm_files")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EXTRAS = os.path.join(ROOT, "content", "extras")
PHT = os.path.join(ROOT, "images", "pht")

def read(page):
    return open(os.path.join(GT, page), encoding="utf-8", errors="replace").read()

def desktop(src):
    """The desktop layout's part of a Xara page (it comes first; the phone layout follows)."""
    starts = [m.start() for m in re.finditer(r'id="xr_mvp_\d+"', src)]
    return src[starts[0]:starts[1]] if len(starts) > 1 else src

def copy_picture(name):
    """Copy a picture (and its @2x version) from the export into images/pht if new or changed."""
    for n in (name, re.sub(r"(\.\w+)$", r"@2x\1", name)):
        s, t = os.path.join(GT_FILES, n), os.path.join(PHT, n)
        if os.path.exists(s) and (not os.path.exists(t) or os.path.getsize(s) != os.path.getsize(t)):
            shutil.copy2(s, t)

def save(name, data):
    os.makedirs(EXTRAS, exist_ok=True)
    json.dump(data, open(os.path.join(EXTRAS, name + ".json"), "w", encoding="utf-8"), indent=1, ensure_ascii=False)

# ------------------------------------------------------------------ Oral History
def oral_history():
    """Each chapter's Video Essay / Audio File button links to the pop-up layer it opens
    (javascript:xr_cpu(41) -> layer xr_xp41), which holds one YouTube player. Chapters are matched
    to the title directly above their buttons. Also records the button artwork the page uses."""
    src = read("oral history.htm")
    layers = [(m.start(), m.group(1)) for m in re.finditer(r'id="xr_xp(\d+)"', src)]
    player = {}
    for i, (pos, n) in enumerate(layers):
        end = layers[i + 1][0] if i + 1 < len(layers) else len(src)
        ids = re.findall(r'youtube(?:-nocookie)?\.com/embed/([^?"/]+)', src[pos:end])
        if ids:
            player[n] = ids[0]
    desk = desktop(src)
    titles = sorted((float(top) + float(off), re.sub(r"\s+", " ", t).strip()) for top, off, t in re.findall(
        r'top:(\d+)px;[^>]*>\s*<span class="xr_tl[^"]*" style="left: [\d.-]+px; top: (-?[\d.]+)px;">'
        r'<span class="xr_s\d+ xr_underline" style="">([^<]+)', desk))
    found = {t: {} for _, t in titles}
    for n, label, top in re.findall(r'href="javascript:xr_cpu\((\d+)\)"[^>]*>\s*<img class="[^"]*" src="[^"]*" '
                                    r'alt="(Video Essay|Audio File)"[^>]*top:([\d.]+)px', desk):
        above = [t for t in titles if t[0] < float(top)]
        assert above and n in player, ("Oral History button not under a chapter / no player", label, top, n)
        found[max(above)[1]]["video" if label == "Video Essay" else "audio"] = player[n]
    chapters = [{"title": t, "video": found[t].get("video"), "audio": found[t].get("audio")} for _, t in titles]
    missing = [c for c in chapters if not (c["video"] and c["audio"])]
    assert not missing, ("Oral History chapter without both buttons wired", missing)
    art = {}
    for label, kind in (("Video Essay", "video"), ("Audio File", "audio")):
        m = re.search(r'href="javascript:xr_cpu\(\d+\)"[^>]*>\s*<img class="[^"]*" src="index_htm_files/([^"]+)" '
                      r'alt="' + label + r'"[^>]*width:(\d+)px;[^>]*>\s*<img class="[^"]*\bxr_ro\b[^"]*"[^>]*'
                      r'src="index_htm_files/([^"]+)"', src)
        assert m, ("Oral History button art not found", label)
        art[kind] = {"label": label, "image": m.group(1), "hover": m.group(3), "width": int(m.group(2))}
        copy_picture(m.group(1)); copy_picture(m.group(3))
    save("oral-history", {"chapters": chapters, "buttons": art})
    return f"oral history: {len(chapters)} chapters"

# ------------------------------------------------------------------ Photos of Coade Stone Pillars
def widgets(page):
    """Xara 'xwidget' galleries in a page's desktop layout, top to bottom. Each widget's content is
    in a small data script (index_htm_files/<n>.js) named after it."""
    src = read(page)
    data = {}
    for js in re.findall(r'src="index_htm_files/(\d+\.js)"', src):
        p = os.path.join(GT_FILES, js)
        if os.path.exists(p):
            t = open(p, encoding="utf-8", errors="replace").read()
            m = re.search(r"window\.local_(\w+?)_data\s*=", t)
            if m:
                data[m.group(1)] = [dict(re.findall(r'(\w+):\s*"([^"]*)"', e)) for e in re.findall(r"\{([^{}]*)\}", t)]
    out = []
    for m in re.finditer(r'left:(\d+)px;\s*top:(\d+)px;\s*width:(\d+)px;\s*height:(\d+)px;[^"]*">\s*'
                         r'<div id="(\w+)" class="xwidget">', desktop(src)):
        wid = m.group(5)
        out.append({"id": wid, "kind": re.sub(r"_\d+$", "", wid), "top": int(m.group(2)), "left": int(m.group(1)),
                    "entries": data.get(wid, [])})
    return sorted(out, key=lambda w: (w["top"], w["left"]))

def photo_descriptions(gt_page_json):
    """Recognise the same photo across Xara's two layouts by a 16x16 picture signature (Xara re-crops
    and renames between them), so the phone layout's photo descriptions can label the desktop photos."""
    try:
        from PIL import Image
    except ImportError:
        return lambda path: ""
    def sig(path):
        im = Image.open(path).convert("L").resize((16, 16))
        px = list(im.tobytes()); avg = sum(px) / len(px)
        return [p > avg for p in px]
    known = []
    for b in json.load(open(gt_page_json, encoding="utf-8"))["blocks"]:
        f = os.path.join(PHT, os.path.basename(b.get("src", "")))
        if b["type"] == "img" and b.get("alt") and os.path.exists(f):
            known.append((sig(f), b["alt"]))
    def describe(path):
        if not known or not os.path.exists(path):
            return ""
        s = sig(path)
        diff, alt = min((sum(a != c for a, c in zip(s, k)), alt) for k, alt in known)
        return alt.strip() if diff <= 90 else ""
    return describe

def coade_photos():
    page = "photos of coade stone pillars.htm"
    ws = widgets(page)
    mosaic = [w for w in ws if w["kind"] == "mosaic_fade" and len(w["entries"]) > 1]
    zoom = [w for w in ws if w["kind"] == "cloudZoomsmooth_v10" and w["entries"]]
    assert mosaic and zoom, "Coade photos: Xara galleries not found in the export"
    hints = list(dict.fromkeys(re.sub(r"\s+", " ", h).strip() for h in re.findall(r">(Hover over each Photo[^<]*)<", read(page))))
    describe = photo_descriptions(os.path.join(ROOT, "content", "gt", "photos of coade stone pillars.json"))
    grid = []
    for w in mosaic:
        name = os.path.basename(w["entries"][1]["image"])
        copy_picture(name)
        grid.append({"image": name, "description": describe(os.path.join(GT_FILES, name))})
    zooms = []
    for w in zoom:
        e = w["entries"][0]
        big = os.path.basename(e["imagebig"]); copy_picture(big)
        zooms.append({"image": big, "caption": e.get("viewertext", "").strip()})
    save("photos-of-coade-stone-pillars", {
        "grid_hint": next((h for h in hints if "zoom" not in h), ""),
        "grid": grid,
        "zoom_hint": next((h for h in hints if "zoom" in h), ""),
        "zoom": zooms})
    return f"coade photos: {len(grid)} grid photos ({sum(1 for g in grid if g['description'])} described), {len(zooms)} zoom photos"

# ------------------------------------------------------------------ Plaques
def plaques():
    """Each plaque thumbnail (drawn as a frame plus the photo, both linked) opens a pop-up layer
    (javascript:xr_cpu(N) -> xr_xpN) whose first picture is that plaque's details panel: a picture of
    text, with the text itself as its alt. Plaques are listed row by row as on the page."""
    page = "plaques.htm"
    src = read(page)
    layers = [(m.start(), m.group(1)) for m in re.finditer(r'id="xr_xp(\d+)"', src)]
    def panel(n):
        for i, (pos, k) in enumerate(layers):
            if k == n:
                end = layers[i + 1][0] if i + 1 < len(layers) else len(src)
                m = re.search(r'<img[^>]*src="index_htm_files/([^"]+)"[^>]*alt="([^"]*)"[^>]*'
                              r'width:(\d+)px;height:(\d+)px', src[pos:end])
                return m.groups() if m else None
    links = {}
    for m in re.finditer(r'href="javascript:xr_cpu\((\d+)\)"[^>]*>\s*<img[^>]*src="index_htm_files/([^"]+)"[^>]*'
                         r'style="left:(\d+)px;top:(\d+)px;width:(\d+)px;height:(\d+)px', desktop(src)):
        n, thumb, left, top, w, h = m.groups()
        links.setdefault(n, []).append((int(top), int(left), thumb, int(w), int(h)))
    out = []
    for n, imgs in links.items():
        p = panel(n)
        assert p, ("Plaques: no details panel for pop-up", n)
        top, left, thumb, w, h = sorted(imgs, key=lambda x: x[2])[-1]       # the photo (drawn on top of its frame)
        alt = re.sub(r"\s+", " ", p[1]).strip()
        name = re.split(r"\s+-\s+|\.\s", alt, maxsplit=1)[0].strip()
        out.append({"thumb": thumb, "w": w, "h": h, "panel": p[0], "panel_w": int(p[2]), "panel_h": int(p[3]),
                    "name": name, "text": alt, "_pos": (round(top / 60), left)})
        copy_picture(thumb); copy_picture(p[0])
    out.sort(key=lambda x: x.pop("_pos"))
    hint = re.search(r">\s*(\(Click on Plaque[^<]*\))\s*<", src)
    save("plaques", {"hint": hint.group(1).strip() if hint else "", "plaques": out})
    return f"plaques: {len(out)} plaques, each with its details panel"

def run():
    return [oral_history(), coade_photos(), plaques()]

if __name__ == "__main__":
    for line in run():
        print(line)
