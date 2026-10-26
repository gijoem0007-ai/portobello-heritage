r"""Check every page of the replica for broken local links and images.

Run from portobello-clone\ after build.py:  python tools\check_links.py
Reports the number of pages, image references (src + srcset) and local links, and lists any
reference whose target file doesn't exist. External links (http/https, mailto, ...) aren't fetched.
Exit code 1 if anything is broken."""
import os, re, sys
from urllib.parse import unquote, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKIP = re.compile(r"^(https?:|mailto:|tel:|javascript:|#|data:|//)")

pages = [os.path.join(dp, f) for dp, dn, fs in os.walk(ROOT) for f in fs
         if f.endswith(".html") and not {"tools", "release"} & set(os.path.relpath(dp, ROOT).split(os.sep))]
srcs = srcsets = links = 0
broken = []

def check(page, url):
    path = unquote(urlparse(url).path)
    if path and not os.path.exists(os.path.normpath(os.path.join(os.path.dirname(page), path))):
        broken.append((os.path.relpath(page, ROOT), url))

for p in pages:
    s = open(p, encoding="utf-8").read()
    for url in re.findall(r'\bdata-panel="([^"]+)"', s):                    # plaque pop-up panels
        srcs += 1
        check(p, url)
    for tag, url in re.findall(r'<(img|a|link|script)\b[^>]*?\b(?:src|href)="([^"]+)"', s):
        if SKIP.match(url):
            continue
        if tag == "img": srcs += 1
        else: links += 1
        check(p, url)
    for ss in re.findall(r'\bsrcset="([^"]+)"', s):
        for part in ss.split(","):
            srcsets += 1
            check(p, part.strip().split()[0])

print(f"{len(pages)} pages, {srcs + srcsets} image references ({srcs} src + {srcsets} srcset), "
      f"{links} local links, {len(broken)} broken")
for page, url in broken:
    print("  BROKEN", page, "->", url)
sys.exit(1 if broken else 0)
