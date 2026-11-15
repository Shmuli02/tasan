#!/usr/bin/env python3
"""Notes/sec and p50/p95 at concurrency 1/8/32/64 on a fixed synthetic subset."""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CLIENT = HERE.parent / "client" / "extract_client.py"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=HERE.parent / "corpus" / "data")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--model", default="Qwen/Qwen3-32B-AWQ")
    ap.add_argument("--limit", type=int, default=32)
    ap.add_argument("--conc", default="1,8,32,64")
    ap.add_argument("--tag", default="32b")
    ap.add_argument("--price", type=float, default=2.386, help="USD/hour list price")
    args = ap.parse_args()
    rows = []
    for c in [int(x) for x in args.conc.split(",")]:
        out = HERE / "results" / f"throughput_{args.tag}_c{c}.json"
        cmd = [
            sys.executable, "-u", str(CLIENT),
            "--corpus", str(args.corpus),
            "--base-url", args.base_url,
            "--model", args.model,
            "--concurrency", str(c),
            "--limit", str(args.limit),
            "--max-tokens", "1200",
            "--timeout", "240",
            "--no-think-suffix",
            "--out", str(out),
        ]
        print("RUN", " ".join(cmd), flush=True)
        r = subprocess.run(cmd)
        if r.returncode not in (0, 1):
            print("sweep failed at conc", c, "rc", r.returncode)
        metrics = json.loads(out.with_name(out.stem + "_metrics.json").read_text())
        nps = metrics.get("notes_per_sec") or 0
        usd_per_1k = None
        if nps:
            usd_per_1k = round(args.price / (nps * 3600) * 1000, 3)
        rows.append({
            "model": args.model,
            "concurrency": c,
            "n": metrics.get("n_documents"),
            "n_ok": metrics.get("n_ok"),
            "elapsed_s": metrics.get("elapsed_s"),
            "notes_per_sec": nps,
            "latency_s": metrics.get("latency_s"),
            "usd_per_1000_notes": usd_per_1k,
            "price_usd_per_h": args.price,
        })
        print(json.dumps(rows[-1], indent=2), flush=True)
    summary = {"synthetic": True, "price_usd_per_h": args.price, "rows": rows}
    dest = HERE / "results" / f"throughput_{args.tag}_sweep.json"
    dest.write_text(json.dumps(summary, indent=2) + "\n")
    print("wrote", dest)


if __name__ == "__main__":
    main()
