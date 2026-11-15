#!/usr/bin/env python3
"""Score a predictions file against v1 or v2 gold, including dev/test splits."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval.evaluate import load_gold, load_pred, score_documents, score_patients, to_markdown


def subset(gold, pred, pids):
    doc_ids = [i for i, rec in gold["documents"].items() if rec["patient_id"] in pids]
    g = {
        "corpus_id": gold["corpus_id"],
        "seed": gold.get("seed"),
        "documents": {i: gold["documents"][i] for i in doc_ids},
        "patients": {pid: gold["patients"][pid] for pid in pids if pid in gold["patients"]},
    }
    p = {
        "system": pred.get("system"),
        "documents": {i: pred["documents"][i] for i in doc_ids if i in pred["documents"]},
    }
    return g, p


def pack(gold, pred, label, pred_path):
    return {
        "synthetic": True,
        "corpus_id": (gold.get("corpus_id") or "") + "/" + label,
        "seed": gold.get("seed"),
        "system": pred.get("system"),
        "predictions_file": str(pred_path),
        "n_documents": len(gold["documents"]),
        "n_patients": len(gold["patients"]),
        "exact": score_documents(gold, pred, 0),
        "plus_minus_1_day": score_documents(gold, pred, 1),
        "patient": score_patients(gold, pred),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, required=True)
    ap.add_argument("--pred", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--system-label", default="")
    args = ap.parse_args()
    gold = load_gold(args.corpus)
    pred = load_pred(args.pred)
    if args.system_label:
        pred["system"] = args.system_label
    splits_path = args.corpus / "splits.json"
    reports = {"all": pack(gold, pred, "all", args.pred)}
    if splits_path.exists():
        splits = json.loads(splits_path.read_text())
        for name in ("dev", "test"):
            if name in splits:
                g, p = subset(gold, pred, set(splits[name]))
                reports[name] = pack(g, p, name, args.pred)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(reports, indent=2) + "\n")
    lines = [f"# {pred.get('system')} on {gold.get('corpus_id')}\n",
             "SYNTHETIC corpus — no real patient data.\n"]
    for name, r in reports.items():
        m = r["exact"]["micro"]
        m1 = r["plus_minus_1_day"]["micro"]
        a = r["patient"]["alert"]
        lines.append(f"## {name} ({r['n_documents']} docs, {r['n_patients']} patients)")
        lines.append(f"- Exact micro P/R/F1: **{m['precision']:.3f} / {m['recall']:.3f} / {m['f1']:.3f}**")
        lines.append(f"- ±1 day micro F1: **{m1['f1']:.3f}**")
        lines.append(
            f"- Day-28 alert accuracy {a['accuracy']:.3f} "
            f"(P {a['precision']:.3f}, R {a['recall']:.3f}, F1 {a['f1']:.3f})"
        )
        per = r["exact"].get("per_type") or r["exact"].get("by_type") or {}
        if per:
            lines.append("- Per-type exact F1: " + ", ".join(
                f"{k}={v['f1']:.3f}" if isinstance(v, dict) else f"{k}={v}"
                for k, v in per.items()
            ))
        lines.append("")
    md = args.out.with_suffix(".md")
    md.write_text("\n".join(lines) + "\n")
    print(md.read_text())
    print("wrote", args.out, "and", md)


if __name__ == "__main__":
    main()
