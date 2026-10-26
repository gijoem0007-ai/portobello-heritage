// Records what a visitor sees on the current page and posts it to the comparison helper.
// Set window.__CMP = {side: "live"|"replica", page: "<name>"} first. Sets window.__CMP_DONE.
(async function () {
  const side = window.__CMP.side, page = window.__CMP.page, live = side === "live";
  const shown = el => {                                   // rendered and not hidden by any ancestor
    if (!el.getClientRects().length) return false;
    for (let e = el; e && e !== document.documentElement; e = e.parentElement) {
      const cs = getComputedStyle(e);
      if (cs.display === "none" || cs.visibility === "hidden") return false;
    }
    return true;
  };
  // site chrome that is compared separately (menus) or deliberately different (replica's footer note)
  const NAV = new Set(["Home", "Heritage", "Events", "Links", "Contact Us", "Menu", "Industry", "Architecture",
    "Culture", "At The Sea Side", "People", "Plaques", "Coade Stone Pillars", "Oral History",
    "Forthcoming Events", "Archived Events"]);
  const inChrome = el => live
    ? !!el.closest(".xr_nb2, .xr_nb4") || (el.tagName === "IMG" && !!el.closest(".xr_nb0") && NAV.has((el.alt || "").trim()))
    : !!el.closest("nav, .site-header, footer .credit");

  const scrollIn = live ? [...document.querySelectorAll(".xr_apq img")].map(i => i.currentSrc || i.src) : [];
  for (let y = 0; y < document.documentElement.scrollHeight; y += 500) {
    scrollTo(0, y); await new Promise(r => setTimeout(r, 120));
  }
  scrollTo(0, 0); await new Promise(r => setTimeout(r, 600));

  // load every picture now (the replica loads them as you scroll), so sizes are real
  document.querySelectorAll("img[loading=lazy]").forEach(i => { i.loading = "eager"; });
  await Promise.all([...document.images].map(i => i.complete ? 0 :
    new Promise(res => { i.onload = i.onerror = res; setTimeout(res, 8000); })));

  // ---- text: what's on screen, in reading order, menus left out
  let text = "";
  if (live) {
    text = document.body.innerText;
  } else {
    const main = document.querySelector("main");
    // menus are compared separately, and button labels are pictures on the live site (buttons are
    // compared on their own): hide them while reading the text, then put them back
    const hide = [...main.querySelectorAll("nav, a.btn, .btn-row a, .btn-inactive")];
    const was = hide.map(e => e.style.display);
    hide.forEach(e => { e.style.display = "none"; });
    text = main.innerText;
    hide.forEach((e, i) => { e.style.display = was[i]; });
    const foot = document.querySelector("footer");
    if (foot) text += "\n" + [...foot.querySelectorAll("p:not(.credit)")].map(p => p.innerText).join("\n");
  }

  // ---- pictures, fingerprinted by content
  const hashes = {};
  async function fingerprint(url) {
    if (!(url in hashes)) {
      hashes[url] = fetch(url).then(r => r.ok ? r.arrayBuffer() : null).then(async b => {
        if (!b) return "missing";
        const d = new Uint8Array(await crypto.subtle.digest("SHA-256", b));
        return [...d.slice(0, 8)].map(x => x.toString(16).padStart(2, "0")).join("");
      }).catch(() => "missing");
    }
    return hashes[url];
  }
  const sliderSel = live ? ".xr_slider" : ".gt-slider";
  const images = [], buttons = [], descriptions = new Set();
  for (const img of document.querySelectorAll("img")) {
    if (inChrome(img) || img.closest(".site-header")) continue;
    const inSlider = img.closest(sliderSel);
    if (inSlider && live && !shown(inSlider)) continue;     // gallery in the hidden (phone) layout
    if (!inSlider && !shown(img)) continue;               // gallery slides count even while faded out
    if (live && img.classList.contains("xr_ro")) continue; // hover state of a button
    const a = img.closest("a");
    const alt = (img.getAttribute("alt") || "").trim();
    const href = a ? a.getAttribute("href") || "" : "";
    const social = !live && img.closest(".socials");
    const isButton = live ? (!inSlider && a && alt && !a.classList.contains("xr_hs"))
                          : !!img.closest(".oh-btn");
    if (isButton) { buttons.push({label: alt, href: !a || /^javascript:/.test(href) ? "popup" : a.href}); continue; }
    if (a && !alt && [...a.querySelectorAll("img[alt]")].some(i => i.alt.trim())) continue; // rest of a button
    if (live && !a && alt && img.classList.contains("xr_rnsp_")) {   // button shown inactive
      if (!img.classList.contains("xr_rs")) buttons.push({label: alt, href: "inactive"});
      continue;
    }
    const r = img.getBoundingClientRect();
    if (Math.min(r.width, r.height) <= 6 && !inSlider) continue; // hairline rules
    images.push({art: live && !!a && !alt && img.classList.contains("xr_rnsp_"),
                 src: img.currentSrc || img.src, hash: await fingerprint(img.currentSrc || img.src),
                 w: Math.round(r.width), h: Math.round(r.height), alt, slider: !!inSlider,
                 link: a ? a.href : ""});
    const tip = img.getAttribute("title") || (img.closest(".hover-tip") || {}).dataset?.tip || "";
    if (tip.trim()) descriptions.add(tip.trim());
    if (live && a && a.classList.contains("xr_hs")) {
      const m = (a.getAttribute("onclick") || "").match(/headingText:\s*'([^']*)'/);
      if (m) descriptions.add(m[1].trim());
    }
  }
  // an unlabelled picture linking where a labelled button links is part of that button's artwork
  const btnLinks = new Set(buttons.map(b => b.href));
  for (let i = images.length - 1; i >= 0; i--)
    if (images[i].art && btnLinks.has(images[i].link)) images.splice(i, 1);

  // replica buttons are text links styled as buttons
  if (!live) document.querySelectorAll("main a.btn, main .btn-row a").forEach(a => {
    if (!a.closest("nav")) buttons.push({label: a.innerText.trim(), href: a.href});
  });
  if (!live) document.querySelectorAll("main .btn-inactive").forEach(b => buttons.push({label: b.innerText.trim(), href: "inactive"}));

  // ---- links (visible, outside menus)
  const links = [];
  for (const a of document.querySelectorAll("a[href]")) {
    if (inChrome(a) || [...a.querySelectorAll("img")].some(inChrome)) continue;   // menu links
    if (!shown(a) && ![...a.querySelectorAll("img")].some(shown)) continue;
    const h = a.getAttribute("href");
    if (/^(javascript:|#)/.test(h)) continue;
    links.push({href: a.href, text: (a.innerText || "").trim().slice(0, 80)});
  }

  // ---- moving / interactive parts
  const videos = new Set();
  document.querySelectorAll("iframe[src*='youtube']").forEach(f => {
    const m = f.src.match(/embed\/([^?"/]+)/); if (m) videos.add(m[1]);
  });
  document.querySelectorAll("[data-video]").forEach(b => videos.add(b.dataset.video));
  const widgets = {
    galleries: [...document.querySelectorAll(sliderSel)].filter(s => live ? s.closest("[id^=xr_mvp_]") && shown(s.closest("[id^=xr_mvp_]")) : true)
                  .map(s => s.querySelectorAll("img").length),
    videos: [...videos].sort(),
    click_to_enlarge: live ? [...document.querySelectorAll("a.xr_hs")].filter(shown).length
                           : document.querySelectorAll("a.lightbox, [data-enlarge]").length,
    popups: live ? [...document.querySelectorAll("a[href^='javascript:xr_cpu']")].filter(a => {
                     const i = a.querySelector("img"); return i && shown(i); }).length
                 : document.querySelectorAll("dialog").length,
    hover_descriptions: descriptions.size,
  };

  const h1 = live ? null : document.querySelector("main h1.page-title");
  const result = {side, page, url: location.href, title: document.title, page_title: h1 ? h1.innerText.trim() : "",
                  text, images, buttons,
                  links, descriptions: [...descriptions], widgets, scroll_in: scrollIn,
                  viewport: [innerWidth, innerHeight], collected: new Date().toISOString()};
  const r = await fetch(`/save/${side}/${encodeURIComponent(page)}`, {method: "POST", body: JSON.stringify(result)});
  window.__CMP_DONE = r.ok ? `saved ${side}/${page}: ${images.length} images, ${buttons.length} buttons, ` +
                      `${links.length} links, ${text.length} chars` : "save failed";
})().catch(e => { window.__CMP_DONE = "error: " + e; });
