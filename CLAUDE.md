# Portobello Heritage Trust website - standing instructions

Site built by Claude Code (replacing the old Xara site) and hosted on
SiteGround. Worked on from two machines (desktop and laptop).

## Version history (git + GitHub)
- This folder is a git repository, backed up to
  https://github.com/gijoem0007-ai/portobello-heritage (private).
- Start of session: run `git status`. If there are uncommitted changes
  you didn't make, tell Joe before doing anything else.
- After each meaningful change, commit with a plain-English message
  (e.g. "Add 2026 AGM to events page"), then `git push`.
- To undo, use git history (revert or restore a file) - never delete
  files by hand to "undo".
- release\ and tools\compare\cache\ are not in git (built/downloaded);
  everything else is.

## Building and checking
- build.py writes the pages; the NAS watcher (tools\nas_build) rebuilds
  automatically and updates BUILD-STATUS.md.
- Preview: http://192.168.4.226:8780/ at home.
- After changes, check BUILD-STATUS.md shows 0 broken links.

## Publishing
- Uploading to SiteGround changes the live site: show Joe what will
  change and get a yes first.
- process-form.php sends membership applications to the Trust's admin
  email - don't change it without asking.
