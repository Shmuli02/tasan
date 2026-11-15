#!/usr/bin/env python3
"""Static server for the explainer page that also accepts rendered frames.

GET  /...            serves files from this folder
POST /frame?i=N      saves the PNG body as frames/f_NNNNN.png
POST /done           touches frames/DONE_<from>

Usage: python3 render_server.py 8767   (binds 127.0.0.1 only)
"""
import os, sys
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse, parse_qs

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "frames")
os.makedirs(OUT, exist_ok=True)

class H(SimpleHTTPRequestHandler):
    def __init__(self, *a, **k):
        super().__init__(*a, directory=HERE, **k)

    def log_message(self, *a):
        pass

    def do_POST(self):
        u = urlparse(self.path); q = parse_qs(u.query)
        body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
        if u.path == "/frame":
            i = int(q["i"][0])
            with open(os.path.join(OUT, f"f_{i:05d}.png"), "wb") as f:
                f.write(body)
        elif u.path == "/done":
            open(os.path.join(OUT, f"DONE_{q.get('from', ['0'])[0]}"), "w").close()
        self.send_response(204); self.end_headers()

port = int(sys.argv[1]) if len(sys.argv) > 1 else 8767
ThreadingHTTPServer(("127.0.0.1", port), H).serve_forever()
