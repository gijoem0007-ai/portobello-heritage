r"""Runs on the NAS in the pht-build container (see docker-compose.yml next to this file).

- Every 30 seconds checks the site's sources (content/, css/, images/, files/, build.py). When
  anything has changed and then stayed unchanged for 10 seconds (so a half-copied batch of
  files isn't built), it runs build.py and tools/check_links.py.
- Writes BUILD-STATUS.md at the top of the replica folder (readable from a phone) and appends
  every run to tools/nas_build/build.log.
- Serves the built site at http://<NAS>:8780/ as a preview (home network and Tailscale only).

The site lives at /site inside the container (bind-mounted replica folder)."""
import datetime, http.server, os, socketserver, subprocess, sys, threading, time

SITE = "/site"
WATCH = ["content", "css", "images", "files", "build.py"]
STATUS = os.path.join(SITE, "BUILD-STATUS.md")
LOG = os.path.join(SITE, "tools", "nas_build", "build.log")
PORT = 8780
PREVIEW = f"http://nas-llm-wiki.tailb0821a.ts.net:{PORT}/"
CHECK_EVERY, SETTLE = 30, 10

def signature():
    """Names, sizes and modification times of every source file (cheap to compute)."""
    sig = []
    for top in WATCH:
        path = os.path.join(SITE, top)
        if os.path.isfile(path):
            st = os.stat(path); sig.append((top, st.st_size, st.st_mtime_ns))
            continue
        for dp, dn, fs in os.walk(path):
            for f in fs:
                p = os.path.join(dp, f)
                try:
                    st = os.stat(p)
                except FileNotFoundError:
                    continue
                sig.append((os.path.relpath(p, SITE), st.st_size, st.st_mtime_ns))
    return hash(tuple(sorted(sig))), len(sig)

def now():
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def run(cmd):
    r = subprocess.run([sys.executable] + cmd, cwd=SITE, capture_output=True, text=True, timeout=600)
    return r.returncode, (r.stdout + r.stderr).strip()

def build(reason):
    started = time.time()
    code, out = run(["build.py"])
    pages = out.count("wrote ")
    if code == 0:
        lcode, lout = run(["tools/check_links.py"])
        check = lout.splitlines()[0] if lout else ""
        ok = lcode == 0
    else:
        lcode, lout, check, ok = None, "", "not run (build failed)", False
    took = time.time() - started
    errors = "\n".join(l for l in out.splitlines() if "Error" in l or "Traceback" in l or "assert" in l.lower())
    status = ("**OK**: the site was rebuilt and every link and picture checks out."
              if ok else "**PROBLEM**: see the details below; the previous pages may still be in place.")
    with open(STATUS, "w", encoding="utf-8") as f:
        f.write(f"# PHT replica: build status\n\n{status}\n\n"
                f"- Last build: {now()} (took {took:.0f} s)\n- Why: {reason}\n- Pages written: {pages}\n"
                f"- Link check: {check}\n- Preview: {PREVIEW} (Tailscale, or http://192.168.4.226:{PORT}/ at home)\n")
        if not ok:
            f.write("\n## Details\n\n```\n" + (errors or out[-3000:]) + "\n" + (lout if lcode else "") + "\n```\n")
    with open(LOG, "a", encoding="utf-8") as f:
        f.write(f"{now()}  {'OK     ' if ok else 'PROBLEM'}  {pages} pages  {check}  ({reason})\n")
    print(f"{now()} build {'OK' if ok else 'PROBLEM'}: {pages} pages; {check}", flush=True)

class Quiet(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=SITE, **kw)
    def log_message(self, *a):
        pass
    def do_GET(self):                       # serve the website only, not the tools or the sources
        if self.path.split("?")[0].lstrip("/").split("/")[0] in ("tools", "content", "build.py", "crop.py",
                                                                  "process-form.php"):
            self.send_error(404); return
        super().do_GET()

def serve():
    socketserver.ThreadingTCPServer.allow_reuse_address = True
    with socketserver.ThreadingTCPServer(("0.0.0.0", PORT), Quiet) as httpd:
        httpd.serve_forever()

if __name__ == "__main__":
    os.umask(0o002)                         # files group-writable (UGOS share, gid 10)
    threading.Thread(target=serve, daemon=True).start()
    print(f"{now()} pht-build watching {SITE}; preview on port {PORT}", flush=True)
    last, n = signature()
    build(f"container started ({n} source files)")
    last, n = signature()
    while True:
        time.sleep(CHECK_EVERY)
        sig, n = signature()
        if sig == last:
            continue
        time.sleep(SETTLE)                  # wait until the change has finished landing
        settled, n = signature()
        if settled != sig:
            continue                        # still changing; look again next round
        build("source files changed")
        last, n = signature()
