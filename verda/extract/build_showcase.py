#!/usr/bin/env python3
"""Build SAMPLES.md, samples.json, and app_export.json from the synthetic corpora.

Uses stable document_ids so the same notes can be regenerated after the
Qwen3-32B run (source then flips to qwen3-32b). No real patient data.
"""
from __future__ import annotations

import argparse
import json
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
from common import ALERT_DAY, EVENT_TYPES  # noqa: E402

V1 = ROOT / "corpus" / "data"
V2 = ROOT / "corpus" / "data_v2"

# 10 stable IDs shared by SAMPLES.md, samples.json, and app_export.json.
# A GPU-paraphrased sibling of SYN2-P0010-referral_letter-01 will be added
# after the paraphrase run (same gold dates, new wording).
SHOWCASE_IDS = [
    # v1 easy, FI pathway
    "SYN-P0002-referral_letter-01",
    "SYN-P0003-ct_report-02",
    "SYN-P0002-biopsy_note-02",
    "SYN-P0001-mdt_minutes-04",
    # languages
    "SYN-P0002-mdt_minutes-03",  # SV
    "SYN-P0001-discharge_summary-05",  # EN, full clock + treatment_start
    # messy / alert
    "SYN-P0087-pathology_report-02",  # typo_heavy
    "SYN-P0051-oncology_note-04",  # late_wait, day-28 alert
    # v2 held-out hard (test split); regex was not tuned on these
    "SYN2-P0010-referral_letter-01",  # written vs arrived
    "SYN2-P0014-ct_report-02",  # booked vs performed
]

TITLES = {
    "SYN-P0002-referral_letter-01": "Finnish referral (v1, easy)",
    "SYN-P0003-ct_report-02": "Finnish CT report (v1, easy)",
    "SYN-P0002-biopsy_note-02": "Finnish bronchoscopy / biopsy (v1, easy)",
    "SYN-P0001-mdt_minutes-04": "Finnish MDT minutes (v1, easy)",
    "SYN-P0002-mdt_minutes-03": "Swedish MDT minutes (v1)",
    "SYN-P0001-discharge_summary-05": "English discharge summary (v1, full pathway)",
    "SYN-P0087-pathology_report-02": "Finnish pathology with typo_heavy noise (v1)",
    "SYN-P0051-oncology_note-04": "Finnish oncology note, late wait, day-28 alert (v1)",
    "SYN2-P0010-referral_letter-01": "v2 test: written-vs-received referral (held-out phrasing)",
    "SYN2-P0014-ct_report-02": "v2 test: booked-vs-performed CT (held-out phrasing)",
}


def _load_docs(root: Path) -> dict:
    out = {}
    with open(root / "documents.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            rec["_root"] = root
            rec["text"] = (root / rec["path"]).read_text()
            out[rec["document_id"]] = rec
    return out


def _load_patients(root: Path) -> dict:
    gold = json.loads((root / "gold.json").read_text())
    pats = gold["patients"]
    if isinstance(pats, dict):
        return pats
    return {p["patient_id"]: p for p in pats}


def _load_pred(path: Path) -> dict:
    if not path.exists():
        return {}
    raw = json.loads(path.read_text())
    docs = raw.get("documents", raw)
    if isinstance(docs, list):
        return {d.get("document_id") or d.get("note_id"): d for d in docs}
    return docs


def _offsets(text: str, span: str) -> tuple[int, int]:
    if not span:
        return -1, -1
    start = text.find(span)
    if start < 0:
        # tolerate a single surrounding whitespace drift
        start = text.find(span.strip())
        span = span.strip() if start >= 0 else span
    if start < 0:
        return -1, -1
    return start, start + len(span)


def _day_count_alert(events: list[dict], as_of: date) -> tuple[int | None, bool]:
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


def _annotate(events: list[dict], text: str, default_conf: float) -> list[dict]:
    out = []
    for ev in events:
        typ = ev.get("type")
        if typ not in EVENT_TYPES:
            continue
        span = ev.get("evidence_span") or ""
        start, end = _offsets(text, span)
        rec = {
            "type": typ,
            "date": ev.get("date"),
            "evidence_span": span,
            "start": start,
            "end": end,
            "confidence": ev.get("confidence", default_conf),
        }
        out.append(rec)
    return out


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--pred-32b", type=Path, default=None,
                    help="Qwen3-32B predictions JSON (one file or a directory of them)")
    ap.add_argument("--source", default="regex_baseline", choices=["regex_baseline", "qwen3-32b"])
    ap.add_argument("--para-dir", type=Path, default=ROOT / "corpus" / "data_v2_para")
    args = ap.parse_args()

    docs = {}
    docs.update(_load_docs(V1))
    docs.update(_load_docs(V2))
    # optional paraphrases: add as extra showcase docs with stable *-para ids
    if args.para_dir.exists() and (args.para_dir / "documents.jsonl").exists():
        docs.update(_load_docs(args.para_dir))
    pats = {}
    pats.update(_load_patients(V1))
    pats.update(_load_patients(V2))
    regex = {}
    regex.update(_load_pred(ROOT / "eval" / "results" / "regex_predictions.json"))
    regex.update(_load_pred(ROOT / "eval" / "results" / "regex_predictions_v2.json"))
    model = {}
    if args.pred_32b:
        paths = []
        if args.pred_32b.is_dir():
            paths = sorted(args.pred_32b.glob("*32b*.json"))
        else:
            paths = [args.pred_32b]
        for path in paths:
            if path.name.endswith("_metrics.json"):
                continue
            model.update(_load_pred(path))
    # also merge any standard result files if present
    for path in [
        ROOT / "eval" / "results" / "qwen3_32b_v1_predictions.json",
        ROOT / "eval" / "results" / "qwen3_32b_v2_predictions.json",
        ROOT / "eval" / "results" / "qwen3_32b_para_predictions.json",
    ]:
        if path.exists():
            model.update(_load_pred(path))

    samples = []
    export = []
    missing = []
    offset_fail = []

    ids = list(SHOWCASE_IDS)
    para_id = "SYN2-P0010-referral_letter-01-para"
    if para_id in docs and para_id not in ids:
        ids.append(para_id)
        TITLES[para_id] = "GPU paraphrase of v2 test referral (same gold dates)"

    for nid in ids:
        if nid not in docs:
            missing.append(nid)
            continue
        d = docs[nid]
        text = d["text"]
        gold_ev = _annotate(d["events"], text, 1.0)
        for ev in gold_ev:
            if ev["start"] < 0:
                offset_fail.append((nid, ev["type"], ev["evidence_span"][:80]))
        pred = regex.get(nid) or {}
        regex_ev = _annotate(pred.get("events") or [], text, 0.45)
        model_raw = model.get(nid) or model.get(d.get("source_document_id") or "") or {}
        model_ev = _annotate(model_raw.get("events") or [], text, 0.7)
        # For a paraphrase, model may have been run on the new text; offsets use this text.
        note = date.fromisoformat(d["note_date"])
        day_count, alert = _day_count_alert(gold_ev, note)
        patient = pats.get(d["patient_id"], {})
        item = {
            "note_id": nid,
            "patient_id": d["patient_id"],
            "lang": d["lang"],
            "doc_type": d["document_type"],
            "note_date": d["note_date"],
            "corpus_id": d.get("corpus_id")
            or ("tasan-extract-synthetic-v2" if nid.startswith("SYN2-") else "tasan-extract-synthetic-v1"),
            "split": d.get("split"),
            "title": TITLES[nid],
            "synthetic": True,
            "text": text,
            "gold_events": gold_ev,
            "regex_events": regex_ev,
            "model_events": model_ev or None,
            "model_name": "Qwen/Qwen3-32B-AWQ" if model_ev else None,
            "day_count": day_count,
            "alert": alert,
            "patient_day_count": patient.get("day_count"),
            "patient_alert": patient.get("alert"),
            "patient_archetype": patient.get("archetype"),
            "source": args.source,
        }
        samples.append(item)
        export.append(
            {
                "note_id": nid,
                "patient_id": d["patient_id"],
                "lang": d["lang"],
                "doc_type": d["document_type"],
                "note_date": d["note_date"],
                "text": text,
                "events": model_ev if (args.source == "qwen3-32b" and model_ev) else gold_ev,
                "day_count": day_count,
                "alert": alert,
                "source": args.source if (args.source != "qwen3-32b" or model_ev) else "regex_baseline",
            }
        )

    if missing:
        raise SystemExit(f"missing showcase ids: {missing}")
    if offset_fail:
        raise SystemExit(f"evidence spans not found in text: {offset_fail}")

    (ROOT / "samples.json").write_text(json.dumps({
        "synthetic": True,
        "banner": "SYNTHETIC DOCUMENT — NOT A REAL PATIENT. All names, dates and findings are invented.",
        "n": len(samples),
        "note_ids": SHOWCASE_IDS,
        "source_now": args.source,
        "source_after_gpu": "qwen3-32b",
        "notes": samples,
    }, ensure_ascii=False, indent=2) + "\n")

    (ROOT / "app_export.json").write_text(json.dumps({
        "synthetic": True,
        "banner": "SYNTHETIC DOCUMENT — NOT A REAL PATIENT. All names, dates and findings are invented.",
        "n": len(export),
        "source": args.source,
        "note": "events are gold when source=regex_baseline, or Qwen3-32B predictions when source=qwen3-32b. note_id values are stable corpus document_ids (paraphrases use <id>-para).",
        "notes": export,
    }, ensure_ascii=False, indent=2) + "\n")

    md = _markdown(samples)
    (ROOT / "SAMPLES.md").write_text(md)
    print(f"wrote {len(samples)} notes -> SAMPLES.md, samples.json, app_export.json")
    for s in samples:
        print(
            f"  {s['note_id']} {s['lang']} {s['doc_type']} "
            f"gold={len(s['gold_events'])} regex={len(s['regex_events'])} "
            f"day={s['day_count']} alert={s['alert']}"
        )


def _body(text: str) -> str:
    if "======\n" in text:
        return text.rsplit("======\n", 1)[-1].strip()
    return text.strip()


def _event_table(events: list[dict]) -> str:
    if not events:
        return "_none_\n"
    lines = ["| type | date | start–end | confidence | evidence_span |",
             "|---|---|---|---|---|"]
    for ev in events:
        span = (ev.get("evidence_span") or "").replace("|", "\\|")
        if len(span) > 120:
            span = span[:117] + "..."
        lines.append(
            f"| `{ev['type']}` | {ev['date']} | {ev['start']}–{ev['end']} | "
            f"{ev['confidence']} | {span} |"
        )
    return "\n".join(lines) + "\n"


def _markdown(samples: list[dict]) -> str:
    parts = [
        "# Tasan Extract — SYNTHETIC showcase notes",
        "",
        "> **SYNTHETIC DOCUMENT — NOT A REAL PATIENT.**",
        "> All names, dates, findings and identifiers in this file are invented.",
        "> Do not treat any of this text as a clinical record.",
        "> Corpus IDs: `tasan-extract-synthetic-v1` (seed 20261114) and",
        "> `tasan-extract-synthetic-v2` (seed 20261142, held-out phrasing).",
        "",
        "## How this fake data was generated",
        "",
        "These notes were built by the Tasan Extract **template generators** under",
        "`verda/extract/corpus/`. No real EHR, no real person, and no copied clinical",
        "text was used. Each patient is an invented record (`SYN-P*` / `SYN2-P*`) with a",
        "Finnish/Swedish/English display name such as *Aino Synteettinen* or",
        "*Matti Mallipotilas*, a made-up date of birth, and a planned lung-cancer",
        "pathway timeline (referral → CT → biopsy → pathology → MDT → treatment",
        "decision → treatment start). The generator writes the note text and the gold",
        "event dates **together**, so the gold labels are known by construction.",
        "",
        "**v1 (easy)** uses relatively regular clinical phrasing the regex baseline",
        "was designed against (for example *ESH-lähete vastaanotettu 8.3.2026*).",
        "It still injects typographical noise, historical distractor dates (old",
        "cholecystectomy, hip replacement), and mixed-language patients.",
        "",
        "**v2 (hard, held-out)** is a second corpus with the same event types and gold",
        "dates but **wordings the regex was never tuned on**: consultation request",
        "*written* versus *logged as arrived*, imaging *booked* versus *performed*,",
        "ISO week numbers (*viikolla 34 maanantaina*), relative weekday phrases",
        "(*eilen*, *perjantaina*), dictation artifacts, and split tokens. The official",
        "regex score on v2 is from the **untuned** v1 patterns; the test split was not",
        "used to add keywords. A later GPU paraphrase pass will rewrite a v2 subset",
        "while a date-recoverability check keeps only notes whose gold dates can still",
        "be read from the new wording. A paraphrased sibling of",
        "`SYN2-P0010-referral_letter-01` will be added here after that run.",
        "",
        "Every corpus file also carries a SYNTHETIC header with `corpus_id`,",
        "`patient_id`, and `document_id`. The `text` fields in `samples.json` and",
        "`app_export.json` are the **full corpus files** (header + body) so character",
        "offsets stay stable. The excerpts below show the clinical body.",
        "",
        "Event dates in this snapshot are **gold** (with char offsets into `text`).",
        "Regex predictions are listed for comparison. After the Finnish GPU run the",
        "same `note_id`s will be filled with Qwen3-32B JSON and `app_export.json`",
        "will be regenerated with `source: \"qwen3-32b\"`.",
        "",
        f"This pack contains **{len(samples)}** notes: Finnish, Swedish and English;",
        "referral, CT, bronchoscopy, MDT, typo-heavy, a day-28 alert, and two v2",
        "held-out traps.",
        "",
        "## Index",
        "",
        "| # | note_id | lang | doc_type | day_count | alert | gold | regex |",
        "|---|---------|------|----------|-----------|-------|------|-------|",
    ]
    for i, s in enumerate(samples, 1):
        parts.append(
            f"| {i} | `{s['note_id']}` | {s['lang']} | {s['doc_type']} | "
            f"{s['day_count']} | {s['alert']} | {len(s['gold_events'])} | {len(s['regex_events'])} |"
        )
    parts += ["", "---", ""]
    for i, s in enumerate(samples, 1):
        parts += [
            f"## {i}. {s['title']}",
            "",
            f"- **note_id:** `{s['note_id']}`  ",
            f"- **patient_id:** `{s['patient_id']}`  ",
            f"- **lang / doc_type / note_date:** {s['lang']} / `{s['doc_type']}` / {s['note_date']}  ",
            f"- **corpus:** `{s['corpus_id']}`" + (f" (split: {s['split']})" if s.get("split") else "") + "  ",
            f"- **archetype:** {s.get('patient_archetype')}  ",
            f"- **day_count / alert (from this note's gold events vs note_date):** {s['day_count']} / {s['alert']}  ",
            f"- **patient-level gold clock:** day_count={s['patient_day_count']}, alert={s['patient_alert']}  ",
            f"- **SYNTHETIC:** yes",
            "",
            "### Note text (body; full file with SYNTHETIC header is in samples.json)",
            "",
            "```",
            _body(s["text"]),
            "```",
            "",
            "### Gold events",
            "",
            _event_table(s["gold_events"]),
            "",
            "### Regex baseline (untuned on v2 test)",
            "",
            _event_table(s["regex_events"]),
            "",
            "### Model JSON (Qwen3-32B)",
            "",
            (_event_table(s["model_events"]) if s.get("model_events") else "_Pending or not available for this note._"),
            "",
            "---",
            "",
        ]
    return "\n".join(parts)


if __name__ == "__main__":
    main()
