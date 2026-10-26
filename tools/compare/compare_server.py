r"""Local helper for comparing the live PHT website with the replica, page by page.

Run from portobello-clone\:  python tools\compare\compare_server.py      (then open http://127.0.0.1:8767/)

  /replica/<path>   the replica's files (this folder)
  /live/<path>      the live site, passed through from https://www.portobelloheritagetrust.co.uk/
                    (each file fetched once and kept in tools\compare\cache\, so the live site
                    sees ordinary, light browsing; delete the cache folder to fetch fresh copies)
  /collect.js       the collector script that records what a visitor sees on a page
  POST /save/<side>/<page>   stores the collector's findings in tools\compare\results\<side>\

Serving both sites from one local address lets the same script read both and save its results.
Only listens on 127.0.0.1 (this PC)."""
import http.server, os, sys, urllib.request, urllib.parse, socketserver

HERE = os.path.dirname(os.path.abspath(__file__))
REPLICA = os.path.dirname(os.path.dirname(HERE))
LIVE = "https://www.portobelloheritagetrust.co.uk/"
CACHE = os.path.join(HERE, "cache")
RESULTS = os.path.join(HERE, "results")
PORT = 8767

TYPES = {".htm": "text/html", ".html": "text/html", ".css": "text/css", ".js": "application/javascript",
         ".png": "image/png", ".jpg": "image/jpeg", ".jpeg": "image/jpeg", ".gif": "image/gif",
         ".svg": "image/svg+xml", ".pdf": "application/pdf", ".json": "application/json",
         ".woff": "font/woff", ".woff2": "font/woff2", ".ttf": "font/ttf", ".webp": "image/webp"}

class H(http.server.BaseHTTPRequestHandler):
    def log_message(self, fmt, *args):
        pass                                              # keep the console quiet

    def send(self, code, body, ctype="text/plain"):
        if ctype.startswith("text/") or ctype.endswith("javascript"):
            try:                                          # say which character set, so the browser doesn't guess
                body.decode("utf-8"); ctype += "; charset=utf-8"
            except UnicodeDecodeError:
                ctype += "; charset=windows-1252"
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        path = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path)
        ctype = TYPES.get(os.path.splitext(path)[1].lower(), "application/octet-stream")
        if path in ("/collect.js", "/run_all.js"):
            return self.send(200, open(os.path.join(HERE, path[1:]), "rb").read(), TYPES[".js"])
        if path.startswith("/replica/"):
            f = os.path.normpath(os.path.join(REPLICA, path[len("/replica/"):]))
            if f.startswith(REPLICA) and os.path.isfile(f):
                return self.send(200, open(f, "rb").read(), ctype)
            return self.send(404, b"not found")
        if path.startswith("/live/"):
            rel = path[len("/live/"):] or "index.htm"
            f = os.path.normpath(os.path.join(CACHE, rel))
            if not f.startswith(CACHE):
                return self.send(404, b"not found")
            if not os.path.isfile(f):
                try:
                    url = LIVE + urllib.parse.quote(rel)
                    req = urllib.request.Request(url, headers={"User-Agent": "PHT replica comparison (owner check)"})
                    data = urllib.request.urlopen(req, timeout=30).read()
                except Exception as e:
                    return self.send(404, f"live fetch failed: {e}".encode())
                os.makedirs(os.path.dirname(f), exist_ok=True)
                open(f, "wb").write(data)
            return self.send(200, open(f, "rb").read(), ctype)
        if path == "/":
            return self.send(200, b"PHT comparison helper running. Pages: /live/<page>.htm and /replica/<page>.html")
        return self.send(404, b"not found")

    def do_POST(self):
        parts = urllib.parse.unquote(urllib.parse.urlsplit(self.path).path).strip("/").split("/", 2)
        if len(parts) != 3 or parts[0] != "save" or parts[1] not in ("live", "replica"):
            return self.send(400, b"bad request")
        name = "".join(c if c.isalnum() or c in "-_ ." else "_" for c in parts[2])
        os.makedirs(os.path.join(RESULTS, parts[1]), exist_ok=True)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        open(os.path.join(RESULTS, parts[1], name + ".json"), "wb").write(body)
        return self.send(200, b"saved")

class S(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True

if __name__ == "__main__":
    print(f"PHT comparison helper on http://127.0.0.1:{PORT}/  (Ctrl+C to stop)")
    S(("127.0.0.1", PORT), H).serve_forever()
