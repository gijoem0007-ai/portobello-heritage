r"""Make the upload-ready copy of the website (what goes on SiteGround), from the built pages.

Run from portobello-clone\ after build.py:
    python tools\make_release.py staging   -> release\staging\  + release\pht-website-staging.zip
    python tools\make_release.py live      -> release\live\     + release\pht-website-live.zip

Both copies contain only the website: the pages, css, the pictures and PDFs the pages actually use,
process-form.php (the membership form), .htaccess (redirects from the old Xara addresses) and
robots.txt. Never the build tools, content data, previews or this script.
  - The "local test replica" footer line is removed.
  - staging (new.portobelloheritagetrust.co.uk): every page says "noindex" and robots.txt blocks
    all crawlers, so search engines leave the trial copy alone. No visitor statistics.
  - live (www.portobelloheritagetrust.co.uk): the site's Google Analytics tag on every page, a
    sitemap.xml with the new addresses, normal indexing."""
import os, re, shutil, sys, zipfile
from datetime import date
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://www.portobelloheritagetrust.co.uk"

GA = """<!-- Google tag (gtag.js) -->
<script async src="https://www.googletagmanager.com/gtag/js?id=G-5LN3J2NVR4"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-5LN3J2NVR4');
</script>"""

# old Xara page (live site address) -> new page. Includes the empty Xara group pages, which
# nothing links to but which could be bookmarked or listed by search engines.
OLD_PAGES = {
    "index.htm": "", "heritage.htm": "heritage.html", "events page.htm": "events.html",
    "links.htm": "links.html", "contact us.htm": "contact.html", "terms.htm": "terms.html",
    "helen hopkirk.htm": "heritage/helen-hopekirk.html", "prince phillip.htm": "heritage/prince-philip.html",
    "industry-b.htm": "heritage.html", "architechture.htm": "heritage.html", "culture.htm": "heritage.html",
    "at the sea side.htm": "heritage.html", "people.htm": "heritage.html",
    "Charles William Schulze and W.M. Ramsay.htm": "heritage/chocolate-factory.html",
}
for slug in ["beach", "chocolate-factory", "coade-stone-pillars", "entertainment", "euphemia-tot-addy",
             "georgian-houses", "golden-days", "hendersons-garage", "heritage-trail-leaflet",
             "high-days-and-holidays", "marine-gardens", "miss-meg-moir", "oral-history", "peggy-brown",
             "photos-of-coade-stone-pillars", "pier", "plaques", "portobello-harbour", "pottery-manufacture",
             "salt-pans", "shops-and-shopkeepers", "sir-peter-heatly", "toddlers-hut", "william-leatham"]:
    OLD_PAGES[slug.replace("-", " ") + ".htm"] = f"heritage/{slug}.html"
for slug in ["forthcoming-events", "dig-portobello", "kiln-celebration", "porty-love-stories"]:
    OLD_PAGES[slug.replace("-", " ") + ".htm"] = f"events/{slug}.html"

def pages():
    out = []
    for dp, dn, fs in os.walk(ROOT):
        rel = os.path.relpath(dp, ROOT)
        if rel != "." and rel.split(os.sep)[0] not in ("heritage", "events"):
            continue
        out += [os.path.normpath(os.path.join(rel, f)) for f in fs if f.endswith(".html")]
    return sorted(out)

def referenced_files(page_rel, text):
    """Local files a page uses: src/href/srcset/inline url(...)."""
    refs = re.findall(r'\b(?:src|href|data-panel)="([^"]+)"', text)       # data-panel: plaque pop-ups
    refs += [p.strip().split()[0] for ss in re.findall(r'\bsrcset="([^"]+)"', text) for p in ss.split(",")]
    refs += re.findall(r"url\(['\"]?([^'\")]+)['\"]?\)", text)
    found = set()
    for r in refs:
        if re.match(r"^(https?:|mailto:|tel:|javascript:|#|data:|//)", r):
            continue
        path = unquote(urlparse(r).path)
        if path:
            found.add(os.path.normpath(os.path.join(os.path.dirname(page_rel), path)))
    return found

def htaccess():
    lines = ["# Portobello Heritage Trust: redirects from the old Xara addresses (made by tools/make_release.py)",
             "DirectoryIndex index.html", "Options -Indexes", "", "# old pages -> new pages"]
    for old, new in sorted(OLD_PAGES.items()):
        pattern = "^/" + re.escape(old).replace("\\ ", " ") + "$"
        lines.append(f'RedirectMatch 301 "{pattern}" "/{new}"')
    lines += ["", "# old picture and PDF addresses (/index_htm_files/...) -> their new place, if it exists",
              "RewriteEngine On",
              "RewriteCond %{DOCUMENT_ROOT}/files/$1 -f",
              "RewriteRule ^index_htm_files/(.+)$ /files/$1 [R=301,L,NE]",
              "RewriteCond %{DOCUMENT_ROOT}/images/pht/$1 -f",
              "RewriteRule ^index_htm_files/(.+)$ /images/pht/$1 [R=301,L,NE]", ""]
    return "\n".join(lines)

def main(mode):
    assert mode in ("staging", "live"), "usage: make_release.py staging|live"
    # Build in a private temporary folder, then bring release\<mode> up to date file by file (see sync()).
    # Deleting and recreating release\<mode> fails if it's open in Explorer or still being deleted on
    # the network drive.
    import tempfile
    final = os.path.join(ROOT, "release", mode)
    out = tempfile.mkdtemp(prefix=f"pht-{mode}-")
    needed, pages_done = set(), []
    for rel in pages():
        text = open(os.path.join(ROOT, rel), encoding="utf-8").read()
        text = re.sub(r'\s*<p class="credit">.*?</p>', "", text, flags=re.S)        # test-copy footer note
        if mode == "staging":
            text = text.replace("<head>", '<head>\n<meta name="robots" content="noindex, nofollow">', 1)
        else:
            text = text.replace("</head>", GA + "\n</head>", 1)
        needed |= referenced_files(rel, text)
        os.makedirs(os.path.join(out, os.path.dirname(rel)), exist_ok=True)
        with open(os.path.join(out, rel), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        pages_done.append(rel)
    css = open(os.path.join(ROOT, "css", "style.css"), encoding="utf-8").read()
    needed |= referenced_files("css/style.css", css)
    needed.add(os.path.normpath("css/style.css"))
    needed.add("process-form.php")
    missing, copied = [], 0
    for rel in sorted(needed):
        if rel.endswith(".html"):
            continue
        src = os.path.join(ROOT, rel)
        if not os.path.isfile(src):
            missing.append(rel); continue
        os.makedirs(os.path.join(out, os.path.dirname(rel)), exist_ok=True)
        shutil.copy2(src, os.path.join(out, rel)); copied += 1
    with open(os.path.join(out, ".htaccess"), "w", encoding="utf-8", newline="\n") as f:
        f.write(htaccess())
    with open(os.path.join(out, "robots.txt"), "w", encoding="utf-8", newline="\n") as f:
        f.write("User-agent: *\nDisallow: /\n" if mode == "staging"
                else f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    if mode == "live":
        urls = "".join(f"  <url><loc>{SITE}/{'' if p == 'index.html' else p.replace(os.sep, '/').replace(' ', '%20')}</loc>"
                       f"<lastmod>{date.today().isoformat()}</lastmod></url>\n" for p in pages_done)
        with open(os.path.join(out, "sitemap.xml"), "w", encoding="utf-8", newline="\n") as f:
            f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                    f'<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n{urls}</urlset>\n')
    zpath = os.path.join(ROOT, "release", f"pht-website-{mode}.zip")
    with zipfile.ZipFile(zpath, "w", zipfile.ZIP_DEFLATED) as z:
        for dp, dn, fs in os.walk(out):
            for f in fs:
                full = os.path.join(dp, f)
                z.write(full, os.path.relpath(full, out).replace(os.sep, "/"))
    size = sum(os.path.getsize(os.path.join(dp, f)) for dp, dn, fs in os.walk(out) for f in fs)
    changed, removed = sync(out, final)
    shutil.rmtree(out, ignore_errors=True)
    print(f"{mode}: {len(pages_done)} pages, {copied} other files, {size / 1e6:.1f} MB; "
          f"zip {os.path.getsize(zpath) / 1e6:.1f} MB -> {zpath}")
    print(f"  {final}: {len(changed)} files new or changed, {removed} old files removed"
          + (f" (changed: {', '.join(changed[:8])}{' …' if len(changed) > 8 else ''})" if changed else ""))
    if missing:
        print("  MISSING (referenced but not found):", missing)
    return not missing

def sync(src, dst):
    """Make dst match src, copying only files that differ and deleting files no longer present.
    Returns (changed files, number removed). Empty leftover folders are left alone."""
    import filecmp
    changed, removed = [], 0
    for dp, dn, fs in os.walk(src):
        rel = os.path.relpath(dp, src)
        os.makedirs(os.path.join(dst, rel), exist_ok=True)
        for f in fs:
            s, t = os.path.join(dp, f), os.path.join(dst, rel, f)
            if not os.path.exists(t) or not filecmp.cmp(s, t, shallow=False):
                shutil.copy2(s, t)
                changed.append(os.path.normpath(os.path.join(rel, f)).replace(os.sep, "/"))
    for dp, dn, fs in os.walk(dst):
        rel = os.path.relpath(dp, dst)
        for f in fs:
            if not os.path.exists(os.path.join(src, rel, f)):
                try:
                    os.remove(os.path.join(dp, f)); removed += 1
                except OSError:
                    pass
    return changed, removed

if __name__ == "__main__":
    sys.exit(0 if main(sys.argv[1] if len(sys.argv) > 1 else "") else 1)
