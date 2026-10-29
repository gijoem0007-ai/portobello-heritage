# Portobello Heritage Trust website - handoff

## Active machine


## Last updated
2026-10-29 (laptop). Reconstructed from CLAUDE.md, git history, BUILD-STATUS.md and
file dates. There was no handoff before this, so anything marked (unconfirmed) needs
Joe to check.

## What the site is
- The Portobello Heritage Trust website (portobelloheritagetrust.co.uk). Joe is the
  volunteer webmaster.
- Rebuilt with Claude Code to replace the old Xara site; hosted on SiteGround.
- `build.py` writes the pages from `content\`. The NAS watcher (`tools\nas_build`)
  rebuilds automatically and updates `BUILD-STATUS.md`.
- Preview: http://192.168.4.226:8780/ at home (or the Tailscale address in BUILD-STATUS.md).
- Git: this folder, backed up to https://github.com/gijoem0007-ai/portobello-heritage (private).

## Current state
- Migrated from Xara Web Designer to HTML (Joe, 2026-10-29).
- Live on SiteGround since 14 Oct 2026 (from the wiki page `portobello/heritage-trust.md`).
- Last build: 2026-10-14 18:44, 36 pages, 0 broken links or images.
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

## Next

## Open questions for Joe
- Any changes or fixes waiting since go-live?
- Has the site been uploaded again since 14 Oct?

## Log (newest first)
- 2026-10-29 laptop: tidy: the git line under "Current state" said "2 commits", out of date after today's
  handoff commits.
- 2026-10-29 laptop: wording fix (Joe): the Xara -> HTML migration is finished, not in progress.
- 2026-10-29 laptop: added the Xara -> hand-written HTML migration line (Joe). "Next" left empty
  until Joe confirms the pending items Claude suggested in chat.
- 2026-10-29 laptop: HANDOFF.md created from git history (no site changes). Wiki status page
  `N:\LLM Wiki\projects\portobello-heritage.md` created; CLAUDE.md now says to refresh it each session.
