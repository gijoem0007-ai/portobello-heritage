r"""Turn tools\compare\report.json (from compare.py) into a readable page: tools\compare\report.html.

Run from portobello-clone\:  python tools\compare\report.py"""
import html, json, os
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
report = json.load(open(os.path.join(HERE, "report.json"), encoding="utf-8"))
notes_f = os.path.join(HERE, "review_notes.json")       # reviewer's findings for this run (optional)
notes = json.load(open(notes_f, encoding="utf-8")) if os.path.exists(notes_f) else {}
LEVEL = {"fixed": ("good", "Fixed"), "high": ("warn", "Fix"), "medium": ("info", "Decide"), "low": ("muted", "Effect"), "check": ("check", "Check")}

def findings_html():
    if not notes.get("groups"):
        return ""
    out = ['<h2>Findings</h2>']
    if notes.get("live_note"):
        out.append(f'<p class="lede">{html.escape(notes["live_note"])}</p>')
    for g in notes["groups"]:
        cls, tag = LEVEL.get(g.get("level"), ("info", ""))
        items = "".join(f'<li><span class="pill {cls}">{tag}</span> {html.escape(i["text"])} '
                        f'<a href="#{html.escape(i["page"])}">Page details</a></li>' for i in g["items"])
        out.append(f'<section class="finding"><h3>{html.escape(g["title"])}</h3><ul>{items}</ul></section>')
    if notes.get("not_covered"):
        out.append(f'<p class="lede small">{html.escape(notes["not_covered"])}</p>')
    return "".join(out)

NICE = {  # plain-words headings for each kind of difference
    "text missing from replica": "Text on the live page that the replica doesn't have",
    "text on replica but not on live page": "Text on the replica that isn't on the live page",
    "pictures missing from replica": "Pictures on the live page that the replica doesn't show",
    "pictures on replica but not on live page": "Pictures on the replica that aren't on the live page",
    "same pictures, different number of copies": "Same pictures, but a different number of them",
    "buttons missing or different on replica": "Buttons on the live page missing or different on the replica",
    "buttons on replica only": "Buttons on the replica only",
    "link targets missing from replica": "Links on the live page that the replica doesn't have",
    "link targets on replica only": "Links on the replica only",
    "galleries differ": "Photo galleries differ",
    "videos differ": "Videos differ",
    "click-to-enlarge photos not on replica": "Photos you can click to enlarge on the live page, but not on the replica",
    "photo descriptions missing from replica": "Photo descriptions missing from the replica",
    "pictures that appear as you scroll down on the live page": "Pictures that appear as you scroll down on the live page (an effect, not missing content)",
}

def title_of(r):
    return r["replica"].split("/")[-1].replace(".html", "").replace("-", " ").title().replace("Index", "Home")

def intended_html(r):
    if not r.get("intended"):
        return ""
    return ('<div class="intended-note"><b>Intended difference</b><ul>'
            + "".join(f"<li>{html.escape(i)}</li>" for i in r["intended"]) + "</ul></div>")

def counts_table(r):
    lc, rc = r["counts"]["live"], r["counts"]["replica"]
    lw, rw = r["widgets"]["live"], r["widgets"]["replica"]
    rows = [("Sentences", lc["sentences"], rc["sentences"]), ("Pictures", lc["pictures"], rc["pictures"]),
            ("Buttons", lc["buttons"], rc["buttons"]), ("Links", lc["links"], rc["links"]),
            ("Galleries", len(lw["galleries"]), len(rw["galleries"])),
            ("Videos", len(lw["videos"]), len(rw["videos"]))]
    body = "".join(f'<tr{" class=diff" if a != b else ""}><th scope="row">{n}</th><td>{a}</td><td>{b}</td></tr>'
                   for n, a, b in rows)
    return f'<table class="counts"><thead><tr><th></th><th>Live</th><th>Replica</th></tr></thead><tbody>{body}</tbody></table>'

cards, n_diff = [], 0
for r in sorted(report, key=lambda r: (not r["differences"], title_of(r))):
    has = bool(r["differences"])
    n_diff += has
    diffs = ""
    for d in r["differences"]:
        items = "".join(f"<li>{html.escape(i)}</li>" for i in d["items"])
        n = len(d["items"])
        diffs += (f'<details class="diff-group"{" open" if n <= 6 else ""}><summary>{html.escape(NICE.get(d["kind"], d["kind"]))}'
                  f' <span class="n">{n}</span></summary><ul>{items}</ul></details>')
    cards.append(f'''<article class="page {'has' if has else 'ok'}" id="{html.escape(r["page"])}">
<header><h3>{html.escape(title_of(r))}</h3><span class="pill {'warn' if has else 'good'}">{'Differences found' if has else 'Matches'}</span></header>
<p class="files"><span>Live: <code>{html.escape(r["live"])}</code></span><span>Replica: <code>{html.escape(r["replica"])}</code></span></p>
{('<p class="page-note">' + html.escape(notes.get("page_notes", {}).get(r["page"], "")) + '</p>') if notes.get("page_notes", {}).get(r["page"]) else ''}<div class="body">{counts_table(r)}<div class="diffs">{diffs or '<p class="none">Text, pictures, buttons, links, galleries and videos all match.</p>'}{intended_html(r)}</div></div>
</article>''')

page = f'''<title>PHT Replica Check</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Lora:wght@500;600&family=Open+Sans:wght@400;600&family=IBM+Plex+Mono:wght@400&display=swap">
<style>
/* Layout: one reading column of page cards; pages with differences first, matches folded below. */
:root {{
  --bg: #fbfaf6; --surface: #ffffff; --ink: #24211d; --muted: #6d665c; --line: #e4ded3;
  --brick: #9c4a33; --info-bg: #f6e7e1; --good: #2f6b45; --good-bg: #e6f1e9; --warn: #8a5a00; --warn-bg: #fbefd6;
  --display: "Lora", Georgia, serif; --body: "Open Sans", "Segoe UI", system-ui, sans-serif;
  --mono: "IBM Plex Mono", Consolas, monospace;
}}
@media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{
  --bg: #1b1916; --surface: #24211d; --ink: #ece6dc; --muted: #a79f93; --line: #3a352e;
  --brick: #e08d72; --info-bg: #3a2620; --good: #8fd1a5; --good-bg: #1f3326; --warn: #f0c46b; --warn-bg: #3a2f17; color-scheme: dark }} }}
:root[data-theme="dark"] {{
  --bg: #1b1916; --surface: #24211d; --ink: #ece6dc; --muted: #a79f93; --line: #3a352e;
  --brick: #e08d72; --info-bg: #3a2620; --good: #8fd1a5; --good-bg: #1f3326; --warn: #f0c46b; --warn-bg: #3a2f17; color-scheme: dark }}
body {{ background: var(--bg); color: var(--ink); font: 15px/1.55 var(--body); }}
.wrap {{ max-width: 860px; margin: 0 auto; padding-inline: 16px; padding-block: 28px 64px; }}
h1 {{ font: 600 2rem/1.15 var(--display); margin: 0 0 .3rem; text-wrap: balance; }}
h2 {{ font: 600 1.25rem/1.3 var(--display); margin: 2.2rem 0 .8rem; }}
h3 {{ font: 600 1.1rem/1.3 var(--display); margin: 0; }}
.lede {{ color: var(--muted); margin: 0 0 1.4rem; max-width: 65ch; }}
.summary {{ display: flex; flex-wrap: wrap; gap: 12px; margin: 0 0 1rem; }}
.stat {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 12px 16px; min-width: 140px; }}
.stat b {{ display: block; font: 600 1.6rem/1.1 var(--display); font-variant-numeric: tabular-nums; }}
.stat span {{ color: var(--muted); font-size: .85rem; }}
.how {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 18px; }}
.how ul {{ margin: .4rem 0 0; padding-left: 1.2rem; }}
.how li {{ margin: .2rem 0; }}
.intended li {{ color: var(--muted); }}
.page {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 16px 18px; margin: 0 0 12px; }}
.page.has {{ border-left: 4px solid var(--warn); }}
.page header {{ display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; }}
.pill {{ font-size: .78rem; font-weight: 600; letter-spacing: .02em; padding: 3px 10px; border-radius: 999px; }}
.pill.good {{ color: var(--good); background: var(--good-bg); }}
.pill.warn {{ color: var(--warn); background: var(--warn-bg); }}
.files {{ display: flex; flex-wrap: wrap; gap: 4px 18px; margin: .35rem 0 .8rem; color: var(--muted); font-size: .82rem; }}
code {{ font: .82rem var(--mono); }}
.body {{ display: grid; grid-template-columns: minmax(0, 190px) minmax(0, 1fr); gap: 18px; align-items: start; }}
@media (max-width: 620px) {{ .body {{ grid-template-columns: minmax(0, 1fr); }} }}
.counts {{ border-collapse: collapse; font-size: .85rem; width: 100%; font-variant-numeric: tabular-nums; }}
.counts th, .counts td {{ text-align: right; padding: 3px 6px; border-bottom: 1px solid var(--line); }}
.counts th[scope=row] {{ text-align: left; font-weight: 400; color: var(--muted); }}
.counts thead th {{ font-weight: 600; color: var(--muted); font-size: .78rem; }}
.counts tr.diff td {{ color: var(--warn); font-weight: 600; }}
.diffs {{ min-width: 0; }}
.diff-group {{ border-top: 1px solid var(--line); padding: 6px 0; }}
.diff-group:first-child {{ border-top: 0; padding-top: 0; }}
.diff-group summary {{ cursor: pointer; font-weight: 600; }}
.diff-group summary:focus-visible {{ outline: 2px solid var(--brick); outline-offset: 2px; }}
.diff-group .n {{ color: var(--muted); font-weight: 400; font-size: .85rem; }}
.diff-group ul {{ margin: .4rem 0 .2rem; padding-left: 1.1rem; }}
.diff-group li {{ margin: .25rem 0; overflow-wrap: anywhere; }}
.none {{ color: var(--good); margin: 0; }}
.finding {{ background: var(--surface); border: 1px solid var(--line); border-radius: 8px; padding: 14px 18px; margin: 0 0 12px; }}
.finding ul {{ list-style: none; margin: .5rem 0 0; padding: 0; display: grid; gap: .7rem; }}
.finding li {{ max-width: 75ch; }}
.finding .pill {{ margin-right: .35rem; }}
.pill.info {{ color: var(--brick); background: var(--info-bg); }}
.pill.muted {{ color: var(--muted); background: var(--line); }}
.pill.check {{ color: var(--warn); background: var(--warn-bg); }}
.page-note {{ background: var(--info-bg); border-radius: 6px; padding: 8px 12px; font-size: .88rem; margin: 0 0 .8rem; }}
.small {{ font-size: .88rem; margin-top: .4rem; }}
h3.sub {{ font: 600 1.05rem/1.3 var(--display); color: var(--muted); margin: 1rem 0 .6rem; }}
.intended-note {{ margin-top: .6rem; color: var(--muted); font-size: .88rem; }}
.intended-note ul {{ margin: .2rem 0 0; padding-left: 1.1rem; }}
.ok-list summary {{ cursor: pointer; font: 600 1.25rem/1.3 var(--display); margin: 2.2rem 0 .8rem; }}
a {{ color: var(--brick); }}
</style>
<div class="wrap">
<h1>PHT Replica Check</h1>
<p class="lede">Every page of the replica compared with the live Portobello Heritage Trust website, as a visitor sees them in a browser at desktop width. Checked {date.today().strftime("%-d %B %Y") if os.name != "nt" else date.today().strftime("%#d %B %Y")}.</p>
<div class="summary">
  <div class="stat"><b>{len(report)}</b><span>pages compared</span></div>
  <div class="stat"><b>{len(report) - n_diff}</b><span>match</span></div>
  <div class="stat"><b>{n_diff}</b><span>with differences</span></div>
</div>
<div class="how">
<strong>What was compared on each page</strong>
<ul>
<li><b>Text</b>: every sentence a visitor can read, ignoring spacing and line breaks.</li>
<li><b>Pictures</b>: matched by the picture itself, not its file name, so a different picture is caught even if the name is the same.</li>
<li><b>Buttons and links</b>: their labels and where they lead (pages, PDFs, other websites).</li>
<li><b>Galleries and videos</b>: how many galleries, how many photos in each, and which YouTube videos the page plays.</li>
</ul>
<strong>Left out on purpose</strong> <span class="lede">(these differences are intended and recorded in the changelog)</span>
<ul class="intended">
<li>The menus, already checked against the live site separately. The replica also shows the category menu on article pages.</li>
<li>The replica's footer note saying it is a local test copy.</li>
</ul>
</div>
{findings_html()}
<h2>Page by page</h2>
<h3 class="sub">Pages with differences</h3>
{''.join(c for c in cards if 'class="page has"' in c) or '<p class="none">None.</p>'}
<details class="ok-list"><summary>Pages that match ({len(report) - n_diff})</summary>
{''.join(c for c in cards if 'class="page ok"' in c)}
</details>
</div>
'''
open(os.path.join(HERE, "report.html"), "w", encoding="utf-8").write(page)
print("wrote", os.path.join(HERE, "report.html"))
