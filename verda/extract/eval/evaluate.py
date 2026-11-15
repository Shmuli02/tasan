#!/usr/bin/env python3
"""Evaluate extraction predictions against SYNTHETIC gold.

Document-level: per-event-type precision / recall / F1 for exact ISO date match
and for a +/-1 day tolerance.

Patient-level: merge events with 'latest document wins' (same rule as gold),
then score day-28 alert accuracy / precision / recall, plus day_count MAE
when both sides have a referral.
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import ALERT_DAY, EVENT_TYPES  # noqa: E402


def load_gold(corpus: Path) -> dict:
    return json.loads((corpus / "gold.json").read_text(encoding="utf-8"))


def load_pred(path: Path) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    if "documents" not in data:
        raise SystemExit(f"predictions file {path} must have a 'documents' map")
    return data


def _events_by_type(events: list[dict]) -> dict[str, list[date]]:
    out: dict[str, list[date]] = defaultdict(list)
    for ev in events:
        try:
            out[ev["type"]].append(date.fromisoformat(ev["date"]))
        except (KeyError, ValueError, TypeError):
            continue
    return out


def score_documents(gold: dict, pred: dict, slack: int) -> dict:
    """Micro P/R/F1 per type and overall. One gold/pred date list per doc per type.

    A predicted date is TP if some unmatched gold date of the same type is within
    `slack` days. Extra preds are FP; unmatched gold is FN.
    """
    per = {t: {"tp": 0, "fp": 0, "fn": 0} for t in EVENT_TYPES}
    for doc_id, grec in gold["documents"].items():
        g = _events_by_type(grec.get("events") or [])
        prec = pred.get("documents", {}).get(doc_id, {})
        p = _events_by_type(prec.get("events") or [])
        for t in EVENT_TYPES:
            gold_dates = list(g.get(t, []))
            pred_dates = list(p.get(t, []))
            used = [False] * len(gold_dates)
            for pd in pred_dates:
                hit = None
                for i, gd in enumerate(gold_dates):
                    if not used[i] and abs((pd - gd).days) <= slack:
                        hit = i
                        break
                if hit is not None:
                    used[hit] = True
                    per[t]["tp"] += 1
                else:
                    per[t]["fp"] += 1
            per[t]["fn"] += sum(1 for u in used if not u)
    return _finalise(per)


def _prf(tp, fp, fn) -> dict:
    prec = tp / (tp + fp) if (tp + fp) else 0.0
    rec = tp / (tp + fn) if (tp + fn) else 0.0
    f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn,
        "precision": round(prec, 4),
        "recall": round(rec, 4),
        "f1": round(f1, 4),
        "support": tp + fn,
    }


def _finalise(per: dict) -> dict:
    types = {t: _prf(v["tp"], v["fp"], v["fn"]) for t, v in per.items()}
    tp = sum(v["tp"] for v in per.values())
    fp = sum(v["fp"] for v in per.values())
    fn = sum(v["fn"] for v in per.values())
    macro = {
        "precision": round(sum(types[t]["precision"] for t in EVENT_TYPES) / len(EVENT_TYPES), 4),
        "recall": round(sum(types[t]["recall"] for t in EVENT_TYPES) / len(EVENT_TYPES), 4),
        "f1": round(sum(types[t]["f1"] for t in EVENT_TYPES) / len(EVENT_TYPES), 4),
    }
    return {"per_type": types, "micro": _prf(tp, fp, fn), "macro": macro}


def merge_patient(doc_ids: list[str], docs_gold_or_pred: dict, note_dates: dict) -> dict:
    latest = {}
    ordered = sorted(doc_ids, key=lambda i: note_dates.get(i, "9999-01-01"))
    for did in ordered:
        rec = docs_gold_or_pred.get(did) or {}
        for ev in rec.get("events") or []:
            if ev.get("type") in EVENT_TYPES and ev.get("date"):
                try:
                    date.fromisoformat(ev["date"])
                except ValueError:
                    continue
                latest[ev["type"]] = ev["date"]
    notes = [note_dates[i] for i in doc_ids if i in note_dates]
    clock = max(notes) if notes else None
    ref = latest.get("referral_received")
    start = latest.get("treatment_start")
    day_count = None
    if ref and clock:
        day_count = (date.fromisoformat(clock) - date.fromisoformat(ref)).days
    alert = bool(day_count is not None and day_count >= ALERT_DAY and start is None)
    return {"merged": latest, "clock_as_of": clock, "day_count": day_count, "alert": alert}


def score_patients(gold: dict, pred: dict) -> dict:
    note_dates = {i: rec["note_date"] for i, rec in gold["documents"].items()}
    # also include pred-only notes if needed
    for i, rec in pred.get("documents", {}).items():
        if i not in note_dates and rec.get("note_date"):
            note_dates[i] = rec["note_date"]

    tp = fp = fn = tn = 0
    day_abs = []
    n_ref_both = 0
    for pid, gp in gold["patients"].items():
        doc_ids = gp["document_ids"]
        g = {
            "day_count": gp["day_count"],
            "alert": gp["alert"],
            "referral": gp.get("referral_date"),
        }
        p = merge_patient(doc_ids, pred.get("documents") or {}, note_dates)
        if g["alert"] and p["alert"]:
            tp += 1
        elif (not g["alert"]) and p["alert"]:
            fp += 1
        elif g["alert"] and (not p["alert"]):
            fn += 1
        else:
            tn += 1
        if g["day_count"] is not None and p["day_count"] is not None:
            day_abs.append(abs(g["day_count"] - p["day_count"]))
            n_ref_both += 1
    total = tp + fp + fn + tn
    acc = (tp + tn) / total if total else 0.0
    prf = _prf(tp, fp, fn)
    return {
        "n_patients": total,
        "alert": {
            **prf,
            "tn": tn,
            "accuracy": round(acc, 4),
            "rule": f"day_count >= {ALERT_DAY} and no treatment_start; merge=latest_document_wins",
        },
        "day_count_mae": round(sum(day_abs) / len(day_abs), 3) if day_abs else None,
        "day_count_compared": n_ref_both,
    }


def to_markdown(report: dict) -> str:
    lines = [
        f"# Extraction eval — {report.get('system', 'unknown')}",
        "",
        f"- Corpus: `{report['corpus_id']}` (SYNTHETIC, seed {report['seed']})",
        f"- Documents: {report['n_documents']}, patients: {report['n_patients']}",
        f"- Predictions: `{report['predictions_file']}`",
        "",
        "## Document-level event extraction",
        "",
        "### Exact date match",
        "",
        "| type | precision | recall | F1 | support | TP | FP | FN |",
        "|---|---:|---:|---:|---:|---:|---:|---:|",
    ]
    def rows(block):
        out = []
        for t, s in block["per_type"].items():
            out.append(f"| {t} | {s['precision']:.3f} | {s['recall']:.3f} | {s['f1']:.3f} | {s['support']} | {s['tp']} | {s['fp']} | {s['fn']} |")
        m = block["micro"]
        mac = block["macro"]
        out.append(f"| **micro** | {m['precision']:.3f} | {m['recall']:.3f} | {m['f1']:.3f} | {m['support']} | {m['tp']} | {m['fp']} | {m['fn']} |")
        out.append(f"| **macro** | {mac['precision']:.3f} | {mac['recall']:.3f} | {mac['f1']:.3f} |  |  |  |  |")
        return out
    lines.extend(rows(report["exact"]))
    lines += ["", "### Date match within ±1 day", "",
              "| type | precision | recall | F1 | support | TP | FP | FN |",
              "|---|---:|---:|---:|---:|---:|---:|---:|"]
    lines.extend(rows(report["plus_minus_1_day"]))
    a = report["patient"]["alert"]
    lines += [
        "",
        "## Patient-level day-28 alert",
        "",
        f"- Accuracy: **{a['accuracy']:.3f}** ({a['tp'] + a['tn']}/{report['patient']['n_patients']})",
        f"- Precision: {a['precision']:.3f}, recall: {a['recall']:.3f}, F1: {a['f1']:.3f}",
        f"- Confusion: TP={a['tp']} FP={a['fp']} FN={a['fn']} TN={a['tn']}",
        f"- day_count MAE (patients with referral on both sides): {report['patient']['day_count_mae']} "
        f"(n={report['patient']['day_count_compared']})",
        f"- Rule: {a['rule']}",
        "",
        "_All labels are from the synthetic gold corpus. No real patient data._",
        "",
    ]
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path(__file__).resolve().parents[1] / "corpus" / "data")
    ap.add_argument("--pred", type=Path, required=True)
    ap.add_argument("--out", type=Path, default=None, help="prefix; writes .json and .md")
    args = ap.parse_args()
    gold = load_gold(args.corpus)
    pred = load_pred(args.pred)
    report = {
        "synthetic": True,
        "corpus_id": gold.get("corpus_id"),
        "seed": gold.get("seed"),
        "system": pred.get("system") or args.pred.stem,
        "predictions_file": str(args.pred),
        "n_documents": len(gold["documents"]),
        "n_patients": len(gold["patients"]),
        "exact": score_documents(gold, pred, slack=0),
        "plus_minus_1_day": score_documents(gold, pred, slack=1),
        "patient": score_patients(gold, pred),
    }
    md = to_markdown(report)
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.with_suffix(".json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        args.out.with_suffix(".md").write_text(md, encoding="utf-8")
        print(f"wrote {args.out.with_suffix('.json')} and {args.out.with_suffix('.md')}")
    print(md)
    return 0


if __name__ == "__main__":
    sys.exit(main())
