#!/usr/bin/env python3
"""Send the SYNTHETIC corpus to an OpenAI-compatible endpoint (vLLM or Verda Inference).

Records per-request latency, token usage and notes/sec. Configurable concurrency.
Does not print API keys. Default is a dry connection check only if --base-url is unset
and --dry-run is passed; otherwise --base-url is required.

Example (after an SSH tunnel to a vLLM port on 127.0.0.1:8000):

  python3 extract_client.py \\
    --corpus ../corpus/data \\
    --base-url http://127.0.0.1:8000/v1 \\
    --model Qwen/Qwen3-32B-AWQ \\
    --concurrency 8 \\
    --out ../eval/results/qwen3_32b_awq_predictions.json
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import CORPUS_ID  # noqa: E402

HERE = Path(__file__).resolve().parent
PROMPT_DIR = HERE.parent / "prompt"


def _load_prompt():
    system = (PROMPT_DIR / "system.txt").read_text(encoding="utf-8")
    user_tmpl = (PROMPT_DIR / "user_template.txt").read_text(encoding="utf-8")
    schema = json.loads((PROMPT_DIR / "schema.json").read_text(encoding="utf-8"))
    return system, user_tmpl, schema


def _auth_header() -> dict:
    # Prefer a dedicated extract key; fall back to VERDA_API_KEY. Never log the value.
    key = os.environ.get("TASAN_EXTRACT_API_KEY") or os.environ.get("VERDA_API_KEY") or ""
    if not key:
        return {}
    return {"Authorization": f"Bearer {key}"}


def _post_chat(base_url: str, payload: dict, timeout: int) -> tuple[int, dict | str, float]:
    url = base_url.rstrip("/") + "/chat/completions"
    body = json.dumps(payload).encode("utf-8")
    headers = {"Content-Type": "application/json", **_auth_header()}
    req = urllib.request.Request(url, data=body, headers=headers, method="POST")
    t0 = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read()
            latency = time.perf_counter() - t0
            try:
                return resp.status, json.loads(raw), latency
            except json.JSONDecodeError:
                return resp.status, raw.decode("utf-8", "replace")[:2000], latency
    except urllib.error.HTTPError as e:
        latency = time.perf_counter() - t0
        raw = e.read().decode("utf-8", "replace")[:2000]
        try:
            return e.code, json.loads(raw), latency
        except json.JSONDecodeError:
            return e.code, raw, latency
    except Exception as e:
        latency = time.perf_counter() - t0
        return 0, f"{type(e).__name__}: {e}", latency


def _parse_events(content: str) -> list[dict]:
    if not content:
        return []
    text = content.strip()
    # strip optional markdown fences
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    data = None
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        a, b = text.find("{"), text.rfind("}")
        if a >= 0 and b > a:
            try:
                data = json.loads(text[a:b + 1])
            except json.JSONDecodeError:
                data = None
    if data is None:
        return []
    ev = None
    if isinstance(data, dict) and isinstance(data.get("events"), list):
        ev = data["events"]
    elif isinstance(data, list):
        ev = data
    elif isinstance(data, dict):
        # Fallback: flat {event_type: {date, evidence_span} | null}
        ev = []
        for typ, item in data.items():
            if typ == "events":
                continue
            if item is None:
                continue
            if isinstance(item, dict):
                rec = dict(item)
                rec["type"] = rec.get("type") or typ
                ev.append(rec)
    if not isinstance(ev, list):
        return []
    clean = []
    for item in ev:
        if not isinstance(item, dict):
            continue
        typ = item.get("type")
        if not typ:
            continue
        clean.append({
            "type": typ,
            "date": item.get("date"),
            "date_text": item.get("date_text"),
            "evidence_span": item.get("evidence_span") or "",
            "confidence": item.get("confidence") if isinstance(item.get("confidence"), (int, float)) else 0.5,
        })
    return clean


def process_one(meta: dict, text: str, args, system: str, user_tmpl: str, schema: dict) -> dict:
    user = user_tmpl.format(note_date=meta["note_date"], lang=meta.get("lang") or "unknown", text=text)
    if args.no_think_suffix and "/no_think" not in user:
        user = user.rstrip() + "\n\n/no_think\n"
    payload = {
        "model": args.model,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "chat_template_kwargs": {"enable_thinking": False},
        "extra_body": {"chat_template_kwargs": {"enable_thinking": False}},
    }
    # vLLM 0.33: OpenAI json_schema is what actually constrains to our events[].
    # guided_json + response_format=json_object lets the model emit a flat object.
    if args.guided:
        payload["response_format"] = {
            "type": "json_schema",
            "json_schema": {"name": "TasanExtractEvents", "strict": True, "schema": schema},
        }
    status, data, latency = _post_chat(args.base_url, payload, args.timeout)
    content = ""
    usage = {}
    if isinstance(data, dict):
        choices = data.get("choices") or []
        if choices:
            content = (choices[0].get("message") or {}).get("content") or ""
        usage = data.get("usage") or {}
    events = _parse_events(content) if status == 200 else []
    return {
        "document_id": meta["document_id"],
        "patient_id": meta["patient_id"],
        "note_date": meta["note_date"],
        "events": events,
        "http_status": status,
        "latency_s": round(latency, 4),
        "prompt_tokens": usage.get("prompt_tokens"),
        "completion_tokens": usage.get("completion_tokens"),
        "total_tokens": usage.get("total_tokens"),
        "ok": status == 200 and isinstance(data, dict),
        "error": None if status == 200 else (data if isinstance(data, str) else json.dumps(data, ensure_ascii=False)[:500]),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=HERE.parent / "corpus" / "data")
    ap.add_argument("--base-url", default=os.environ.get("TASAN_EXTRACT_BASE_URL", ""))
    ap.add_argument("--model", default=os.environ.get("TASAN_EXTRACT_MODEL", "Qwen/Qwen3-32B-AWQ"))
    ap.add_argument("--concurrency", type=int, default=4)
    ap.add_argument("--max-tokens", type=int, default=800)
    ap.add_argument("--temperature", type=float, default=0.0)
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--guided", action="store_true", default=True)
    ap.add_argument("--no-guided", action="store_false", dest="guided")
    ap.add_argument("--no-think-suffix", action="store_true", help="append /no_think to the user message")
    ap.add_argument("--limit", type=int, default=0, help="optional cap on documents (debug)")
    ap.add_argument("--dry-run", action="store_true", help="build payloads, send nothing")
    ap.add_argument("--out", type=Path, default=HERE.parent / "eval" / "results" / "model_predictions.json")
    args = ap.parse_args()

    system, user_tmpl, schema = _load_prompt()
    manifest = json.loads((args.corpus / "manifest.json").read_text(encoding="utf-8"))
    metas = manifest["documents"]
    if args.limit:
        metas = metas[: args.limit]

    if args.dry_run:
        print(f"dry-run: {len(metas)} documents, model={args.model}, concurrency={args.concurrency}, no requests sent")
        return 0
    if not args.base_url:
        print("error: --base-url is required unless --dry-run", file=sys.stderr)
        return 2

    t0 = time.perf_counter()
    results = []
    with ThreadPoolExecutor(max_workers=max(1, args.concurrency)) as pool:
        futs = []
        for meta in metas:
            text = (args.corpus / meta["path"]).read_text(encoding="utf-8")
            futs.append(pool.submit(process_one, meta, text, args, system, user_tmpl, schema))
        for fut in as_completed(futs):
            rec = fut.result()
            results.append(rec)
            n = len(results)
            if n % 25 == 0 or n == len(metas):
                ok = sum(1 for r in results if r["ok"])
                print(f"progress {n}/{len(metas)} ok={ok}", flush=True)

    elapsed = time.perf_counter() - t0
    results.sort(key=lambda r: r["document_id"])
    latencies = [r["latency_s"] for r in results]
    latencies_sorted = sorted(latencies)
    def pct(p):
        if not latencies_sorted:
            return None
        i = min(len(latencies_sorted) - 1, max(0, int(round(p * (len(latencies_sorted) - 1)))))
        return latencies_sorted[i]

    tokens_in = sum(r["prompt_tokens"] or 0 for r in results)
    tokens_out = sum(r["completion_tokens"] or 0 for r in results)
    summary = {
        "system": args.model,
        "synthetic": True,
        "corpus_id": CORPUS_ID,
        "base_url_host": args.base_url.split("/")[2] if "://" in args.base_url else args.base_url,
        "n_documents": len(results),
        "n_ok": sum(1 for r in results if r["ok"]),
        "elapsed_s": round(elapsed, 3),
        "notes_per_sec": round(len(results) / elapsed, 3) if elapsed else None,
        "concurrency": args.concurrency,
        "latency_s": {
            "p50": pct(0.50),
            "p95": pct(0.95),
            "mean": round(sum(latencies) / len(latencies), 4) if latencies else None,
            "max": max(latencies) if latencies else None,
        },
        "tokens": {"prompt": tokens_in, "completion": tokens_out, "total": tokens_in + tokens_out},
        "finished_at_eet": datetime.now().strftime("%Y-%m-%d %H:%M:%S EET"),
    }
    out = {
        "system": args.model,
        "synthetic": True,
        "summary": summary,
        "documents": {
            r["document_id"]: {
                "patient_id": r["patient_id"],
                "note_date": r["note_date"],
                "events": r["events"],
                "latency_s": r["latency_s"],
                "prompt_tokens": r["prompt_tokens"],
                "completion_tokens": r["completion_tokens"],
                "http_status": r["http_status"],
                "ok": r["ok"],
            }
            for r in results
        },
    }
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    metrics_path = args.out.with_name(args.out.stem + "_metrics.json")
    metrics_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    print(f"wrote {args.out} and {metrics_path}")
    return 0 if summary["n_ok"] == summary["n_documents"] else 1


if __name__ == "__main__":
    sys.exit(main())
