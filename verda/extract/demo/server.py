#!/usr/bin/env python3
"""Local demo for POST /extract. SYNTHETIC data only.

Backend is the regex baseline (no GPU, no paid API). Optional cached-fallback
serves precomputed results when the body matches a corpus document.

  python3 server.py --port 8088 --corpus ../corpus/data --cache ../eval/results/regex_predictions.json

  curl -s http://127.0.0.1:8088/health
  curl -s -X POST http://127.0.0.1:8088/extract \\
    -H 'Content-Type: application/json' \\
    -d '{"text":"...","lang":"fi"}'
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from datetime import date, datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ALERT_DAY, EVENT_TYPES  # noqa: E402
from eval.regex_baseline import extract_document  # noqa: E402

CACHE = {"by_id": {}, "by_hash": {}, "patients": {}, "docs_note": {}}
ARGS = None
ALLOW_ORIGINS = {
    "https://petaled-trowel-90.beacon.host",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
}


def _hash(text: str) -> str:
    return hashlib.sha256(text.strip().encode("utf-8")).hexdigest()


def _note_date_from_text(text: str, fallback: str | None) -> date:
    m = re.search(r"^note_date:\s*(\d{4}-\d{2}-\d{2})\s*$", text, re.M)
    if m:
        return date.fromisoformat(m.group(1))
    if fallback:
        return date.fromisoformat(fallback)
    return date.today()


def _day_count_alert(events: list[dict], as_of: date) -> tuple[int | None, bool]:
    ref = None
    start = False
    for ev in events:
        if ev.get("type") == "referral_received" and ev.get("date"):
            try:
                d = date.fromisoformat(ev["date"])
            except ValueError:
                continue
            if ref is None or d < ref:
                ref = d
        if ev.get("type") == "treatment_start" and ev.get("date"):
            start = True
    day_count = (as_of - ref).days if ref else None
    alert = bool(day_count is not None and day_count >= ALERT_DAY and not start)
    return day_count, alert


def load_cache(corpus: Path, pred_path: Path | None) -> None:
    if not pred_path or not pred_path.is_file():
        return
    pred = json.loads(pred_path.read_text(encoding="utf-8"))
    manifest = json.loads((corpus / "manifest.json").read_text(encoding="utf-8"))
    gold = json.loads((corpus / "gold.json").read_text(encoding="utf-8"))
    paths = {d["document_id"]: d["path"] for d in manifest["documents"]}
    for did, rec in (pred.get("documents") or {}).items():
        rel = paths.get(did)
        if not rel:
            continue
        text = (corpus / rel).read_text(encoding="utf-8")
        entry = {
            "document_id": did,
            "patient_id": rec.get("patient_id"),
            "note_date": rec.get("note_date"),
            "events": rec.get("events") or [],
            "source": "cache",
        }
        CACHE["by_id"][did] = entry
        CACHE["by_hash"][_hash(text)] = entry
        CACHE["docs_note"][did] = rec.get("note_date")
    CACHE["patients"] = gold.get("patients") or {}


def extract_payload(body: dict) -> dict:
    text = body.get("text")
    if not isinstance(text, str) or not text.strip():
        return {"error": "missing_text", "detail": "JSON body must include a non-empty 'text' field"}
    lang = body.get("lang")
    as_of_raw = body.get("as_of")
    doc_id = body.get("note_id") or body.get("document_id")
    patient_id = body.get("patient_id")

    cached = None
    if ARGS.cache_mode != "off":
        if doc_id and doc_id in CACHE["by_id"]:
            cached = CACHE["by_id"][doc_id]
        elif _hash(text) in CACHE["by_hash"]:
            cached = CACHE["by_hash"][_hash(text)]
    if ARGS.cache_mode == "always" and cached is None and (doc_id or patient_id):
        # explicit id but miss
        pass

    if cached and ARGS.cache_mode != "off":
        events = list(cached["events"])
        source = "cache"
        note = date.fromisoformat(cached["note_date"]) if cached.get("note_date") else _note_date_from_text(text, as_of_raw)
        model = "regex_baseline+cache"
    else:
        note = _note_date_from_text(text, as_of_raw)
        events = extract_document(text, note)
        source = "regex_baseline"
        model = "regex_baseline"

    if as_of_raw:
        as_of = date.fromisoformat(as_of_raw)
    else:
        as_of = note
    day_count, alert = _day_count_alert(events, as_of)
    # If the caller names a cached patient, attach the patient-level clock too.
    patient_clock = None
    if patient_id and patient_id in CACHE["patients"]:
        gp = CACHE["patients"][patient_id]
        patient_clock = {
            "patient_id": patient_id,
            "day_count": gp.get("day_count"),
            "alert": gp.get("alert"),
            "clock_as_of": gp.get("clock_as_of"),
            "source": "cached_patient_gold_or_precomputed",
        }

    out_events = []
    for ev in events:
        typ = ev.get("type")
        if typ not in EVENT_TYPES:
            continue
        span = ev.get("evidence_span") or ""
        rec = {
            "type": typ,
            "date": ev.get("date"),
            "evidence_span": span,
            "confidence": ev.get("confidence", 0.45),
        }
        if ev.get("start") is not None and ev.get("end") is not None:
            rec["start"] = ev["start"]
            rec["end"] = ev["end"]
        elif span and text:
            start = text.find(span)
            if start >= 0:
                rec["start"] = start
                rec["end"] = start + len(span)
        if ev.get("date_text"):
            rec["date_text"] = ev["date_text"]
        out_events.append(rec)

    note_id = None
    if cached:
        note_id = cached.get("document_id")
    elif doc_id:
        note_id = doc_id
    return {
        "note_id": note_id,
        "events": out_events,
        "day_count": day_count,
        "alert": alert,
        "model": model,
        "refused": False,
        "source": source,
        "lang": lang,
        "as_of": as_of.isoformat(),
        "patient": patient_clock,
        "warnings": [],
    }


class Handler(BaseHTTPRequestHandler):
    def _allow_origin(self):
        origin = self.headers.get("Origin") or ""
        if origin in ALLOW_ORIGINS:
            return origin
        return ""

    def _cors(self):
        origin = self._allow_origin()
        if origin:
            self.send_header("Access-Control-Allow-Origin", origin)
            self.send_header("Vary", "Origin")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def _json(self, code: int, obj: dict) -> None:
        raw = json.dumps(obj, ensure_ascii=False).encode("utf-8")
        self.send_response(code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(raw)))
        self._cors()
        self.end_headers()
        self.wfile.write(raw)

    def log_message(self, fmt, *args):
        sys.stderr.write("%s - %s\n" % (self.address_string(), fmt % args))

    def do_OPTIONS(self):
        self.send_response(204)
        self._cors()
        self.send_header("Access-Control-Max-Age", "86400")
        self.end_headers()

    def do_GET(self):
        if self.path.split("?")[0] in ("/health", "/"):
            self._json(200, {
                "ok": True,
                "model": "regex_baseline",
                "backend": "regex",
                "cache_mode": ARGS.cache_mode,
                "cached_documents": len(CACHE["by_id"]),
                "synthetic": True,
            })
            return
        self._json(404, {"error": "not_found"})

    def do_POST(self):
        if self.path.split("?")[0] != "/extract":
            self._json(404, {"error": "not_found"})
            return
        n = int(self.headers.get("Content-Length") or 0)
        if n > 512_000:
            self._json(413, {"error": "payload_too_large"})
            return
        raw = self.rfile.read(n) if n else b"{}"
        try:
            body = json.loads(raw.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError):
            self._json(400, {"error": "invalid_json"})
            return
        if not isinstance(body, dict):
            self._json(400, {"error": "invalid_json"})
            return
        result = extract_payload(body)
        code = 400 if result.get("error") else 200
        self._json(code, result)


def main() -> int:
    global ARGS
    ap = argparse.ArgumentParser()
    ap.add_argument("--host", default="127.0.0.1")
    ap.add_argument("--port", type=int, default=8088)
    ap.add_argument("--corpus", type=Path, default=Path(__file__).resolve().parents[1] / "corpus" / "data")
    ap.add_argument("--cache", type=Path, default=Path(__file__).resolve().parents[1] / "eval" / "results" / "regex_predictions.json")
    ap.add_argument("--cache-mode", choices=("on", "off", "always"), default="on")
    ARGS = ap.parse_args()
    load_cache(ARGS.corpus, ARGS.cache if ARGS.cache_mode != "off" else None)
    httpd = ThreadingHTTPServer((ARGS.host, ARGS.port), Handler)
    print(f"extract demo on http://{ARGS.host}:{ARGS.port}  cache={ARGS.cache_mode} n={len(CACHE['by_id'])}  (SYNTHETIC)", flush=True)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nbye")
    return 0


if __name__ == "__main__":
    sys.exit(main())
