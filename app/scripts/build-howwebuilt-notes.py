#!/usr/bin/env python3
"""Build an English-only How we built it showcase from the Extract corpus.

Read-only on verda/. Writes app/src/content/extract/howwebuilt_notes.json.
Uses real Qwen3-32B model_events, gold_events, day_count and alert.
"""
from __future__ import annotations

import json
import sys
from datetime import date
from pathlib import Path

APP = Path(__file__).resolve().parents[1]
ROOT = APP.parent
V1 = ROOT / "verda" / "extract" / "corpus" / "data"
V2 = ROOT / "verda" / "extract" / "corpus" / "data_v2"
PRED_V1 = ROOT / "verda" / "extract" / "eval" / "results" / "qwen3_32b_v1_predictions.json"
PRED_V2 = ROOT / "verda" / "extract" / "eval" / "results" / "qwen3_32b_v2_predictions.json"
SAMPLES = ROOT / "verda" / "extract" / "samples.json"
OUT = APP / "src" / "content" / "extract" / "howwebuilt_notes.json"

EVENT_TYPES = {
    "referral_received",
    "ct_done",
    "biopsy_done",
    "pathology_result",
    "mdt_decision",
    "treatment_decision",
    "treatment_start",
}
ALERT_DAY = 28

# Mix of note types; last item is the default opened note.
# v2 IDs are held-out hard phrasing with real 32B outputs.
SHOWCASE_IDS = [
    "SYN-P0005-referral_letter-01",
    "SYN-P0012-ct_report-01",
    "SYN-P0039-biopsy_note-03",
    "SYN-P0021-pathology_report-02",
    "SYN-P0036-mdt_minutes-05",
    "SYN-P0105-discharge_summary-06",
    "SYN2-P0014-referral_letter-01",
    "SYN2-P0062-ct_report-01",
    "SYN2-P0008-biopsy_note-02",
    "SYN2-P0054-oncology_note-04",
]
OPEN_ID = "SYN2-P0054-oncology_note-04"


def load_jsonl(path: Path) -> dict:
    out = {}
    with path.open() as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            d = json.loads(line)
            out[d["document_id"]] = d
    return out


def load_patients(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    if isinstance(raw, dict) and "patients" in raw:
        raw = raw["patients"]
    if isinstance(raw, list):
        return {p["patient_id"]: p for p in raw}
    if isinstance(raw, dict):
        return raw
    return {}


def offsets(text: str, span: str) -> tuple[int, int]:
    if not span:
        return -1, -1
    start = text.find(span)
    if start < 0:
        start = text.find(span.strip())
        span = span.strip() if start >= 0 else span
    if start < 0:
        return -1, -1
    return start, start + len(span)


def annotate(events: list, text: str, default_conf: float) -> list[dict]:
    out = []
    for ev in events:
        typ = ev.get("type")
        if typ not in EVENT_TYPES:
            continue
        span = ev.get("evidence_span") or ""
        start, end = offsets(text, span)
        out.append(
            {
                "type": typ,
                "date": ev.get("date"),
                "evidence_span": span,
                "start": start,
                "end": end,
                "confidence": ev.get("confidence", default_conf),
            }
        )
    return out


def day_count_alert(events: list, as_of: date) -> tuple[int | None, bool]:
    ref = start = None
    for ev in events:
        typ, ds = ev.get("type"), ev.get("date")
        if typ == "referral_received" and ds:
            ref = date.fromisoformat(ds)
        if typ == "treatment_start" and ds:
            start = date.fromisoformat(ds)
    day_count = (as_of - ref).days if ref else None
    alert = bool(day_count is not None and day_count >= ALERT_DAY and start is None)
    return day_count, alert


def assert_highlights(note_id: str, text: str, events: list[dict], label: str) -> None:
    for ev in events:
        s, e = ev["start"], ev["end"]
        if s is None or e is None or s < 0 or e < 0:
            # Allowed: span not verbatim in text (UI skips these).
            continue
        got = text[s:e]
        if got != ev["evidence_span"]:
            # tolerate only a strip() rematch used to locate the span
            if got != (ev["evidence_span"] or "").strip():
                raise SystemExit(
                    f"ASSERT FAIL {note_id} {label} {ev['type']}: "
                    f"text[{s}:{e}]={got!r} != evidence_span={ev['evidence_span']!r}"
                )


def main() -> None:
    v1_docs = load_jsonl(V1 / "documents.jsonl")
    v2_docs = load_jsonl(V2 / "documents.jsonl")
    v1_gold = json.loads((V1 / "gold.json").read_text())["documents"]
    v2_gold = json.loads((V2 / "gold.json").read_text())["documents"]
    v1_pred = json.loads(PRED_V1.read_text())
    v2_pred = json.loads(PRED_V2.read_text())
    v1_pats = load_patients(V1 / "patients.json")
    v2_pats = load_patients(V2 / "patients.json")
    existing = json.loads(SAMPLES.read_text()) if SAMPLES.exists() else {}

    notes = []
    fallback = 0
    langs = set()
    diffs = []

    for nid in SHOWCASE_IDS:
        if nid.startswith("SYN2-"):
            meta, gold_docs, pred_pack, pats, root = v2_docs, v2_gold, v2_pred, v2_pats, V2
        else:
            meta, gold_docs, pred_pack, pats, root = v1_docs, v1_gold, v1_pred, v1_pats, V1
        if nid not in meta:
            raise SystemExit(f"missing document metadata: {nid}")
        d = meta[nid]
        if d.get("lang") != "en":
            raise SystemExit(f"{nid} is lang={d.get('lang')}, expected en")
        text_path = root / d["path"]
        if not text_path.exists():
            text_path = root / "documents" / f"{nid}.txt"
        text = text_path.read_text()
        pred_doc = (pred_pack.get("documents") or {}).get(nid)
        if not pred_doc or not pred_doc.get("ok") or not pred_doc.get("events"):
            raise SystemExit(f"{nid} has no successful model predictions")
        gold_ev = annotate((gold_docs.get(nid) or {}).get("events") or d.get("events") or [], text, 1.0)
        model_ev = annotate(pred_doc["events"], text, 0.7)
        if not gold_ev:
            raise SystemExit(f"{nid} has no gold events")
        for ev in gold_ev:
            if ev["start"] < 0:
                raise SystemExit(f"{nid} gold {ev['type']} span not in text: {ev['evidence_span']!r}")
        assert_highlights(nid, text, gold_ev, "gold")
        assert_highlights(nid, text, model_ev, "model")
        note_date = date.fromisoformat(d["note_date"])
        day_count, alert = day_count_alert(gold_ev, note_date)
        patient = pats.get(d["patient_id"], {})
        for ev in model_ev:
            g = next((x["date"] for x in gold_ev if x["type"] == ev["type"]), None)
            if g and ev.get("date") and g != ev.get("date"):
                diffs.append(f"{nid} {ev['type']}: model {ev['date']} vs gold {g}")
        notes.append(
            {
                "note_id": nid,
                "patient_id": d["patient_id"],
                "lang": "en",
                "doc_type": d["document_type"],
                "note_date": d["note_date"],
                "corpus_id": d.get("corpus_id")
                or ("tasan-extract-synthetic-v2" if nid.startswith("SYN2-") else "tasan-extract-synthetic-v1"),
                "split": d.get("split"),
                "synthetic": True,
                "text": text,
                "gold_events": gold_ev,
                "model_events": model_ev,
                "model_name": pred_pack.get("system") or pred_pack.get("summary", {}).get("system") or "Qwen/Qwen3-32B-AWQ",
                "day_count": day_count,
                "alert": alert,
                "patient_day_count": patient.get("day_count"),
                "patient_alert": patient.get("alert"),
                "patient_archetype": patient.get("archetype"),
                "source": "qwen3-32b",
                "translation": None,
            }
        )
        langs.add("en")

    if any(n["lang"] != "en" for n in notes):
        raise SystemExit("non-English note slipped in")
    if len(notes) != 10:
        raise SystemExit(f"expected 10 notes, got {len(notes)}")
    if notes[-1]["note_id"] != OPEN_ID:
        raise SystemExit("open note must be last in the list")

    pack = {
        "synthetic": True,
        "banner": "SYNTHETIC · NOT A REAL PATIENT",
        "n": 10,
        "note_ids": [n["note_id"] for n in notes],
        "open_note_id": OPEN_ID,
        "language": "en",
        "fallback_translated": fallback,
        "source_now": existing.get("source_now") or "qwen3-32b",
        "source_after_gpu": existing.get("source_after_gpu") or "qwen3-32b",
        "notes": notes,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(pack, indent=2, ensure_ascii=False) + "\n")
    print(f"wrote {OUT} ({OUT.stat().st_size} bytes)")
    print(f"fallback_translated={fallback}")
    print(f"open {OPEN_ID} day_count={notes[-1]['day_count']} alert={notes[-1]['alert']} model_events={len(notes[-1]['model_events'])}")
    print("notes:")
    for n in notes:
        n_miss = sum(1 for e in n["model_events"] if e["start"] < 0)
        print(
            f"  {n['note_id']} {n['doc_type']} split={n.get('split')} "
            f"day={n['day_count']} alert={n['alert']} "
            f"model={len(n['model_events'])} miss={n_miss} arch={n.get('patient_archetype')}"
        )
    if diffs:
        print("differs from gold:")
        for line in diffs:
            print(" ", line)
    else:
        print("no model/gold date disagreements in this set")


if __name__ == "__main__":
    main()
