// Collects every page of the live site and the replica, one after another, in a 1280px-wide frame
// (so Xara shows its desktop layout). Open http://127.0.0.1:8767/ (compare_server.py running), then
// load this script there; progress shows on the page and in window.__RUN. Keep the tab in front:
// browsers slow background tabs right down.
(function () {
  const H = ["beach", "chocolate-factory", "coade-stone-pillars", "entertainment", "euphemia-tot-addy",
    "georgian-houses", "golden-days", "helen-hopekirk", "hendersons-garage", "heritage-trail-leaflet",
    "high-days-and-holidays", "marine-gardens", "miss-meg-moir", "oral-history", "peggy-brown",
    "photos-of-coade-stone-pillars", "pier", "plaques", "portobello-harbour", "pottery-manufacture",
    "prince-philip", "salt-pans", "shops-and-shopkeepers", "sir-peter-heatly", "toddlers-hut", "william-leatham"];
  const LIVE_NAME = {"helen-hopekirk": "helen hopkirk", "prince-philip": "prince phillip"};
  const pages = [["index", "index.htm", "index.html"], ["heritage", "heritage.htm", "heritage.html"],
    ["events", "events page.htm", "events.html"], ["links", "links.htm", "links.html"],
    ["contact", "contact us.htm", "contact.html"], ["terms", "terms.htm", "terms.html"]];
  for (const s of H) pages.push([s, (LIVE_NAME[s] || s.replace(/-/g, " ")) + ".htm", "heritage/" + s + ".html"]);
  for (const s of ["forthcoming-events", "dig-portobello", "kiln-celebration", "porty-love-stories"])
    pages.push([s, s.replace(/-/g, " ") + ".htm", "events/" + s + ".html"]);

  document.body.innerHTML = '<p id="cmp-status" style="font:14px sans-serif"></p>';
  const status = document.getElementById("cmp-status");
  const f = document.createElement("iframe");
  f.style.cssText = "width:1280px;height:1000px;border:1px solid #ccc";
  document.body.appendChild(f);
  const log = [];
  window.__RUN = {pages, log, done: false};

  async function collect(side, name, url) {
    await new Promise(res => { f.onload = res; f.src = url; setTimeout(res, 20000); });
    await new Promise(r => setTimeout(r, 2500));                 // let Xara lay the page out
    const w = f.contentWindow;
    w.__CMP = {side, page: name}; w.__CMP_DONE = null;
    const s = w.document.createElement("script");
    s.src = "/collect.js?" + Date.now();
    w.document.body.appendChild(s);
    for (let i = 0; i < 120 && !w.__CMP_DONE; i++) await new Promise(r => setTimeout(r, 250));
    return w.__CMP_DONE || `timeout ${side}/${name}`;
  }
  (async () => {
    for (const [name, livePage, replicaPage] of pages) {
      if (window.__ONLY !== "replica")              // set window.__ONLY = "replica" to redo just the replica
        log.push(await collect("live", name, "/live/" + encodeURIComponent(livePage)));
      log.push(await collect("replica", name, "/replica/" + replicaPage));
      status.textContent = `${log.length} of ${pages.length * 2} pages collected`;
    }
    window.__RUN.done = true;
    status.textContent += " — finished. Now run: python tools\\compare\\compare.py, then report.py";
  })();
})();
