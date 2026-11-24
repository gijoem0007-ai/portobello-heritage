# Portobello Heritage Trust website - handoff

## Active machine


## Last updated
2026-11-24 (desktop). Chapter 05 (Isa Dean Ep 05) now points at the corrected v2 YouTube upload
`AI0yKpQs4eA` (Oral History page + Beach page clip). Committed 6a85efb and pushed; uploaded to SiteGround 2026-11-24 (md5 matches); waiting on Joe's cache flush.
Before that: 2026-11-05, Isa Dean Tape 2 (Episodes 06-14) added and uploaded over SSH. Earlier sections reconstructed 2026-10-29 from git history;
anything marked (unconfirmed) needs Joe to check.

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
  Site Tools > Devs > SSH Keys Manager as "claude-desktop". Laptop: not set up yet.
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
- Git: the site itself was committed on 2026-10-26; later commits (2026-10-29) only touch this
  HANDOFF.md and CLAUDE.md. Working tree clean and in step with GitHub (checked 2026-10-29).
- Newest site files (`build.py`, the HTML pages, `release\`, `tools\`) are dated 14 Oct 2026,
  so that was the last real work on the site itself. The 26 Oct commits only put that work under git.
- (unconfirmed) That what's on SiteGround matches this folder exactly. The first commit says
  "site as uploaded to SiteGround", but nothing here records an upload since.

## Done
- Sept-Oct 2026: site rebuilt from the Xara source on the NAS (via `content\gt\` text extracts
  and `tools\extract_ground_truth.py`), with a link checker and release builder (`tools\make_release.py`).
- 14 Oct 2026: went live on SiteGround.
- 26 Oct 2026: put under git + GitHub; CLAUDE.md written.
- 5 Nov 2026: Oral History page: added Isa Dean Tape 2, Episodes 06-14 (commit dfe83a9). Checked on the
  NAS preview (Episode 14 audio plays in the pop-up); all 18 new YouTube ids allow embedding.

## Next
- Joe: flush SiteGround's Dynamic Cache, then check all four addresses show `AI0yKpQs4eA`.
- After that: Joe deletes (or sets Private) the old Ep 05 YouTube video `FeSR1T1RgzU`.
- Optional: upload `release\live\sitemap.xml` (only the dates changed).
- Laptop: needs its own key imported in PHT Site Tools > Devs > SSH Keys Manager before it can upload.

## Open questions for Joe
- Any changes or fixes waiting since go-live?
- Has the site been uploaded again since 14 Oct?

## Log (newest first)
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
