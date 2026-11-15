#!/usr/bin/env python3
"""Paraphrase a v2 subset on the local vLLM tunnel. Keep gold dates recoverable."""
from __future__ import annotations

import argparse
import json
import sys
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval.date_recover import gold_recoverable, soften  # noqa: E402

SYSTEM = """You rewrite SYNTHETIC (invented, not real patient) clinical notes.
Rules:
- Keep the SAME language as the input (Finnish, Swedish, or English).
- Preserve EVERY pathway event and EVERY resolvable date (including spelled months, ISO weeks, and relative words like eilen/yesterday). Do not add, drop, or change event dates.
- You may rephrase sentences, fix obvious OCR hyphenation, and vary clinical wording.
- Keep the SYNTHETIC header block at the top EXACTLY as given (all ===== lines and metadata).
- Output ONLY the full rewritten note (header + body). No commentary.
- This is invented training text, not a real medical record.
"""


def body_split(text: str) -> tuple[str, str]:
    if "======\n" in text:
        head, body = text.rsplit("======\n", 1)
        return head + "======\n", body
    return "", text


def post(base, model, user, timeout, max_tokens=1800):
    payload = {
        "model": model,
        "temperature": 0.3,
        "max_tokens": max_tokens,
        "messages": [
            {"role": "system", "content": SYSTEM},
            {"role": "user", "content": user + "\n\n/no_think\n"},
        ],
        "chat_template_kwargs": {"enable_thinking": False},
    }
    req = urllib.request.Request(
        base.rstrip("/") + "/chat/completions",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            data = json.loads(resp.read())
        content = ((data.get("choices") or [{}])[0].get("message") or {}).get("content") or ""
        return 200, content, time.perf_counter() - t0
    except Exception as e:
        return 0, f"{type(e).__name__}: {e}", time.perf_counter() - t0


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path(__file__).resolve().parents[1] / "corpus" / "data_v2")
    ap.add_argument("--base-url", default="http://127.0.0.1:8000/v1")
    ap.add_argument("--model", default="Qwen/Qwen3-32B-AWQ")
    ap.add_argument("--n", type=int, default=60)
    ap.add_argument("--concurrency", type=int, default=8)
    ap.add_argument("--timeout", type=int, default=180)
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parents[1] / "corpus" / "data_v2_para")
    ap.add_argument("--prefer-id", action="append", default=[])
    args = ap.parse_args()

    docs = []
    with open(args.corpus / "documents.jsonl") as f:
        for line in f:
            docs.append(json.loads(line))
    # Prefer test split, FI first, then requested ids
    prefer = set(args.prefer_id)
    def score(d):
        s = 0
        if d["document_id"] in prefer:
            s += 1000
        if d.get("split") == "test":
            s += 10
        if d["lang"] == "fi":
            s += 3
        s += len(d.get("events") or [])
        return -s
    docs.sort(key=score)
    picks = docs[: args.n]
    # force prefer ids
    have = {d["document_id"] for d in picks}
    for d in docs:
        if d["document_id"] in prefer and d["document_id"] not in have:
            picks.append(d)

    out_dir = args.out
    (out_dir / "documents").mkdir(parents=True, exist_ok=True)
    kept = []
    dropped = []

    def work(rec):
        text = (args.corpus / rec["path"]).read_text()
        head, body = body_split(text)
        user = (
            f"note_date={rec['note_date']} lang={rec['lang']} doc_type={rec['document_type']}\n"
            f"Rewrite the following SYNTHETIC note. Keep the header unchanged.\n\n{text}"
        )
        st, content, lat = post(args.base_url, args.model, user, args.timeout)
        if st != 200 or not content.strip():
            return {"ok": False, "rec": rec, "reason": f"http {st} {content[:200]}", "latency": lat}
        # strip fences
        c = content.strip()
        if c.startswith("```"):
            c = c.strip("`")
            if c.startswith("text") or c.startswith("markdown"):
                c = c.split("\n", 1)[-1]
        # If model dropped header, prepend original header
        if "SYNTHETIC DOCUMENT" not in c:
            c = (head + c.lstrip()) if head else c
        note = date.fromisoformat(rec["note_date"])
        ok, missing = gold_recoverable(c, note, rec["events"])
        return {
            "ok": ok,
            "rec": rec,
            "text": c,
            "missing": missing,
            "reason": None if ok else ("dates not recoverable: " + ",".join(missing)),
            "latency": lat,
        }

    t0 = time.perf_counter()
    with ThreadPoolExecutor(max_workers=args.concurrency) as pool:
        futs = [pool.submit(work, r) for r in picks]
        for i, fut in enumerate(as_completed(futs), 1):
            r = fut.result()
            rec = r["rec"]
            if r["ok"]:
                nid = rec["document_id"] + "-para"
                path = f"documents/{nid}.txt"
                (out_dir / path).write_text(r["text"])
                item = {
                    **{k: rec[k] for k in rec if k != "path"},
                    "document_id": nid,
                    "source_document_id": rec["document_id"],
                    "path": path,
                    "paraphrased": True,
                    "synthetic": True,
                    "n_chars": len(r["text"]),
                }
                kept.append(item)
            else:
                dropped.append({"document_id": rec["document_id"], "reason": r["reason"]})
            if i % 10 == 0 or i == len(futs):
                print(f"paraphrase {i}/{len(futs)} kept={len(kept)} dropped={len(dropped)}", flush=True)

    elapsed = time.perf_counter() - t0
    (out_dir / "documents.jsonl").write_text("\n".join(json.dumps(x, ensure_ascii=False) for x in kept) + ("\n" if kept else ""))
    gold_docs = {x["document_id"]: {"events": x["events"], "note_date": x["note_date"], "patient_id": x["patient_id"]} for x in kept}
    (out_dir / "gold_subset.json").write_text(json.dumps({"synthetic": True, "documents": gold_docs}, ensure_ascii=False, indent=2) + "\n")
    summary = {
        "synthetic": True,
        "n_attempted": len(picks),
        "n_kept": len(kept),
        "n_dropped": len(dropped),
        "elapsed_s": round(elapsed, 2),
        "kept_ids": [x["document_id"] for x in kept],
        "dropped": dropped,
    }
    (out_dir / "paraphrase_report.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n")
    print(json.dumps({k: summary[k] for k in summary if k != "dropped"}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
