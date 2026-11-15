"""HTTP entrypoint for Verda Serverless Containers *batch jobs* (stdlib only).

Contract (docs.verda.com/containers/batch-jobs/, read 14.11.2026):
  * GET /health must return 200 so the replica accepts a job;
  * each replica handles exactly ONE request, then the process must exit (0 = success, non-zero = failure);
  * the request reaches the container unchanged (method, path, query, body).
Usage: POST /run?county=21&scenario=mid&seed=1&n_runs=1000   |   POST /calibrate?area=YTA-POHJOIS&particles=4000
Result JSON is returned in the response (fetch via /result/<deployment>) and also written to TASAN_OUT
(e.g. a mounted /data volume). No cloud SDK, no credentials inside the container.
"""
from __future__ import annotations
import json, os, sys, threading
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse, parse_qs
from .model import run_job, Inputs
from .cli import write_result

STATE = {"exit": None}

class H(BaseHTTPRequestHandler):
    def _send(self, code, obj):
        b = json.dumps(obj, ensure_ascii=False).encode()
        self.send_response(code); self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(b))); self.end_headers(); self.wfile.write(b)

    def do_GET(self):
        if urlparse(self.path).path == "/health":
            return self._send(200, {"ok": True})
        return self._handle()

    def do_POST(self):
        return self._handle()

    def _handle(self):
        u = urlparse(self.path); q = {k: v[0] for k, v in parse_qs(u.query).items()}
        try:
            n = int(self.headers.get("Content-Length") or 0)
            if n:
                q.update(json.loads(self.rfile.read(n) or b"{}"))
            if u.path.rstrip("/").endswith("/calibrate"):
                from .calibrate import calibrate_area
                res = calibrate_area(q["area"], int(q.get("particles", 400)), int(q.get("seed", 20261114)))
                self._send(200, res); STATE["exit"] = 0
                threading.Thread(target=self.server.shutdown, daemon=True).start(); return
            res = run_job(q.get("county") or os.environ.get("TASAN_COUNTY"), q.get("scenario", os.environ.get("TASAN_SCENARIO", "baseline")),
                          int(q.get("seed", os.environ.get("TASAN_SEED", 1))), int(q.get("n_runs", os.environ.get("TASAN_N_RUNS", 1000))), Inputs())
            write_result(res, os.environ.get("TASAN_OUT", "/tmp/results"))
            self._send(200, res); STATE["exit"] = 0
        except BaseException as e:  # noqa: BLE001 - must always exit the replica
            self._send(500, {"error": str(e)}); STATE["exit"] = 1
        threading.Thread(target=self.server.shutdown, daemon=True).start()

    def log_message(self, fmt, *args):
        sys.stderr.write("tasan-twin " + (fmt % args) + "\n")

def main():
    port = int(os.environ.get("PORT", "8000"))
    srv = HTTPServer(("0.0.0.0", port), H)
    srv.serve_forever()
    sys.exit(STATE["exit"] if STATE["exit"] is not None else 1)

if __name__ == "__main__":
    main()
