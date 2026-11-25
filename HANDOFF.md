# Portobello Heritage Trust website - handoff

## Active machine


## Last updated
2026-11-25 (desktop): notes tidied with Joe; no site changes. The site is stable: nothing waiting.
Last site change 2026-11-24: chapter 05 (Isa Dean Ep 05) now points at the corrected v2 YouTube upload
`AI0yKpQs4eA` (Oral History page + Beach page clip). Committed 6a85efb and pushed; live on SiteGround since 2026-11-24 (checked after Joe's cache flush).
Before that: 2026-11-05, Isa Dean Tape 2 (Episodes 06-14) added and uploaded over SSH.

## What the site is
- The Portobello Heritage Trust website (portobelloheritagetrust.co.uk). Joe is the
  volunteer webmaster.
- Rebuilt with Claude Code to replace the old Xara site; hosted on SiteGround.
- `build.py` writes the pages from `content\`. The NAS watcher (`tools\nas_build`)
  rebuilds automatically and updates `BUILD-STATUS.md`.
- Preview: http://192.168.4.226:8780/ at home (or the Tailscale address in BUILD-STATUS.md).
- Git: this folder, backed up to https://github.com/gijoem0007-ai/portobello-heritage (private).

## How to upload (SSH, set up 2026-11-05)
- Host ssh.portobelloheritagetrust.co.uk, port 18765, user u1082-bzf6u63zujuu.
- Desktop key: `~/.ssh/siteground_portobellolegacy` (same key as the Legacy site), imported in PHT
  Site Tools > Devs > SSH Keys Manager as "claude-desktop".
- Note (not a to-do): Claude Code does the uploads, from the desktop. The laptop has no key, so a
  Claude Code session on the laptop can't upload; do uploads from the desktop. Only if Joe ever wants
  laptop uploads would he import a laptop key in the same SSH Keys Manager.
- Live site folder: `www/portobelloheritagetrust.co.uk/public_html`. Staging copy:
  `www/new.portobelloheritagetrust.co.uk/public_html`.
- Build with `python tools\make_release.py live`, then copy only the changed files from `release\live\`.
  Before replacing a file, copy it on the server to `<name>.bak-YYYYMMDD`; after upload, check the
  md5sum matches the NAS copy. Upload only with Joe's yes.
- Then flush SiteGround's Dynamic Cache, or the bare domain keeps serving the old page.

## Current state
- Migrated from Xara Web Designer to HTML (Joe, 2026-10-29).
- Live on SiteGround since 14 Oct 2026 (from the wiki page `portobello/heritage-trust.md`).
- Last build: 2026-11-05 17:44, 36 pages, 0 broken links or images.
- Oral History page (`heritage/oral-history.html`): 14 chapters as of 2026-11-05. Chapters come from
  `content\extras\oral-history.json` (title + video id + audio id). 01-05 = Isa Dean Tape 1;
  06-14 = Tape 2, added by hand (don't re-run `tools\xara_extras.py`, it would drop them).
  Live on SiteGround since 2026-11-05; all four addresses checked after the cache flush.
- Chapter 05 and the Beach page clip use the corrected Ep 05 video `AI0yKpQs4eA` (since 2026-11-24).
- Git: working tree clean and in step with GitHub (checked 2026-11-25).
- Uploads since go-live: 2026-11-05 (Oral History page) and 2026-11-24 (Oral History + Beach pages),
  each time only the changed pages, checked by md5 after upload.

## Done
- Sept-Oct 2026: site rebuilt from the Xara source on the NAS (via `content\gt\` text extracts
  and `tools\extract_ground_truth.py`), with a link checker and release builder (`tools\make_release.py`).
- 14 Oct 2026: went live on SiteGround.
- 26 Oct 2026: put under git + GitHub; CLAUDE.md written.
- 5 Nov 2026: Oral History page: added Isa Dean Tape 2, Episodes 06-14 (commit dfe83a9). Checked on the
  NAS preview (Episode 14 audio plays in the pop-up); all 18 new YouTube ids allow embedding.
- 24 Nov 2026: chapter 05 + Beach page clip switched to the corrected Ep 05 video; uploaded and live.

## Next
- Nothing waiting. The site is stable; new work comes from the Oral History project (new chapters).
- Whenever pages are next uploaded, send `release\live\sitemap.xml` too (only its dates changed; not worth
  an upload on its own).

## Open questions for Joe
- None.

## Log (newest first)
- 2026-11-25 desktop: notes tidied with Joe, no site changes. The laptop SSH key is now a note under
  "How to upload", not a to-do (Claude Code uploads from the desktop); answered the old open questions
  (uploads since go-live were 5 and 24 Nov); sitemap folded into the next upload.
- 2026-11-24 desktop: Joe's first flush didn't reach the PHT site; the second did. Server now returns the new
  pages (AI0yKpQs4eA, no FeSR1T1RgzU) at https with and without www; chapter 05 plays the new video with
  subtitles. A browser that visited earlier may need a hard refresh (Ctrl+F5).
- 2026-11-24 desktop: old Ep 05 video FeSR1T1RgzU already deleted on YouTube, but SiteGround's cache still
  served the old pages, so visitors got "video unavailable". Server files are new: bypassing the cache
  (`?check=...`) the chapter 05 button plays AI0yKpQs4eA with subtitles. Waiting on Joe to flush the
  Dynamic Cache in Site Tools (a browser refresh doesn't clear it).
- 2026-11-24 desktop: with Joe's yes, uploaded heritage/oral-history.html and heritage/beach.html (Ep 05 id
  swap). Live copies first confirmed identical apart from the video id, then backed up on the server as
  *.bak-20261124; md5 of uploads matches release\live. All four addresses still served the old pages from
  SiteGround's cache: waiting on Joe to flush it.
- 2026-11-24 desktop: Isa Dean Episode 05 re-made with Lisa's corrections (new pictures + fixed subtitles;
  see `Audio Files\Isa Deans 01\Episode 05\HANDOFF.md`) and uploaded by Joe to YouTube as `AI0yKpQs4eA`.
  Chapter 05 video id changed in `content\extras\oral-history.json` (the Beach page clip follows it; its
  1:14 start is unchanged because v2 has identical timing). Rebuilt, 0 broken links, new id allows embedding.
  Commit 6a85efb, pushed. A Windows build rewrote line endings on every page; those were restored with git.
  Live release build was blocked by a permission check; nothing uploaded.
- 2026-11-05 desktop: Joe flushed SiteGround's Dynamic Cache; Oral History page shows 14 chapters at
  http/https, with and without www.
- 2026-11-05 desktop: SSH set up for the PHT site (Joe imported the desktop key). Live
  heritage/oral-history.html matched the 14 Oct release; backed up on the server as
  oral-history.html.bak-20261105, new page uploaded (md5 matches). www addresses show 14 chapters and
  Episode 06 audio plays; bare domain still cached (5 chapters) until Joe flushes the cache.
- 2026-11-05 desktop: built the live release (`make_release.py live`); only oral-history.html and
  sitemap.xml differ from 14 Oct. Waiting on Joe to upload it to SiteGround.
- 2026-11-05 desktop: added Isa Dean Tape 2 (Episodes 06-14, video + audio each) to the Oral History
  page; build check relaxed so only chapters 01-05 must match the old Xara text. Commit dfe83a9, pushed.
  Waiting on Joe's yes to upload to SiteGround.
- 2026-10-29 laptop: tidy: the git line under "Current state" said "2 commits", out of date after today's
  handoff commits.
- 2026-10-29 laptop: wording fix (Joe): the Xara -> HTML migration is finished, not in progress.
- 2026-10-29 laptop: added the Xara -> hand-written HTML migration line (Joe). "Next" left empty
  until Joe confirms the pending items Claude suggested in chat.
- 2026-10-29 laptop: HANDOFF.md created from git history (no site changes). Wiki status page
  `N:\LLM Wiki\projects\portobello-heritage.md` created; CLAUDE.md now says to refresh it each session.
