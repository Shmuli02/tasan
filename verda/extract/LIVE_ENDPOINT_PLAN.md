# Tasan Extract — live endpoint plan (design only)

This is a launch plan for the judging window on Sunday ~11:00–15:00 EET (UTC+2).
**Do not create an instance tonight.** The night GPU session is train + eval + sweep only
and is API-deleted when it finishes.

All notes on the endpoint are **SYNTHETIC**. No real patient data, no Cloud API secrets
on the GPU, bind vLLM to `127.0.0.1`, terminate HTTPS on the public port.

## What we serve

- **Model:** Qwen3-8B + Tasan LoRA adapter (`tasan8b`) if LoRA matches or beats base
  Qwen3-32B-AWQ on the held-out v2 test (exact micro F1 / alert accuracy). Otherwise
  fall back to the 32B-AWQ weights already measured in phase 1.
- **SKU (preferred):** the smallest in-stock Finnish GPU that holds the chosen model
  with headroom for concurrency 8:
  - LoRA 8B (bf16 + adapter): prefer `1RTX6000ADA.10V` FIN-01/02/03 if in stock
    (48 GB, list **$1.606/h** OD / **$0.803/h** spot). Fallback `1A100.22V` FIN-01
    (**$2.386/h** OD) if Ada is out — same SKU as tonight's train session.
  - 32B-AWQ: `1A100.22V` FIN-01 (80 GB) is the measured fit.
- **Image:** `24.04.cuda13.4.docker`, 200 GB OS volume, hostname `tasan-extract-live`,
  SSH key `tasan-extract-live-ephemeral`, PAY_AS_YOU_GO, locations FIN-01/02/03 only.
- **Window:** start ~10:30 EET, tear down by 15:15 EET. Wall ~4.75 h.
- **Expected cost (4.75 h + 200 GB storage):**
  - Ada OD: 4.75 × $1.606 + 200 × $0.20/730 ≈ **$7.68**
  - Ada spot: 4.75 × $0.803 + $0.05 ≈ **$3.87** (use only if the SKU stays in stock)
  - A100 OD (8B or 32B): 4.75 × $2.386 + $0.05 ≈ **$11.38**
- Controller **always API-deletes** instance + volume + our key and verifies
  (404 on the key is success). A 5.5 h local/remote watchdog is the backstop,
  not the primary teardown. Do not leave it running after 15:15 EET.

## HTTP surface

Public HTTPS (Caddy or nginx + Let's Encrypt, or a Verda TLS terminator if one is
available) in front of the existing demo app:

- `POST /extract` — body `{ "note_id"?: string, "text": string, "lang"?: "fi"|"sv"|"en" }`.
  Response is the same JSON as `app_export.json` rows: `note_id`, `events[]`
  (`type`, `date`, `span`, `start`, `end`), `alert` (`day_count`, `triggered`).
  If the client omits `note_id`, mint a stable `SYN-LIVE-…` id and echo it back.
- `GET /health` — liveness, model name, adapter loaded or not.
- CORS allowlist (already in `demo/server.py`):
  - `https://petaled-trowel-90.beacon.host`
  - `http://localhost:5173`
  - `http://127.0.0.1:5173`
- Target: **p95 < 3 s** for a single typical note at concurrency ≤ 8.
  Phase-1 32B on A100 at conc 16 was well above that (p50 ~20 s) — the live
  box must use **8B + LoRA** if quality holds, `max_num_seqs` sized for conc 8,
  and a **cached fallback**:
  1. In-memory LRU of recent `note_id` / sha256(text) → last extract.
  2. Preload the 10 `app_export.json` showcase notes so the demo is instant
     even if the GPU is cold or vLLM is restarting.
  3. If vLLM is down, return the cache hit or HTTP 503 with a short retry hint;
     never block the frontend for more than 3 s (client-side timeout + cache).

vLLM listens on `127.0.0.1:8000` only. The public process is the demo server
(+ TLS). SSH is key-only.

Example vLLM flags for the 8B+LoRA path (paths filled after tonight's adapter
is copied off the train box):

```bash
docker run --gpus all --rm --ipc=host --network host \
  -v /root/hf:/root/.cache/huggingface \
  -v /root/lora-out:/lora \
  vllm/vllm-openai:latest \
  --model Qwen/Qwen3-8B \
  --enable-lora --lora-modules tasan8b=/lora \
  --max-lora-rank 16 \
  --dtype bfloat16 --max-model-len 4096 \
  --gpu-memory-utilization 0.90 \
  --max-num-seqs 16 \
  --host 127.0.0.1 --port 8000
```

`chat_template_kwargs.enable_thinking=false` and the `/no_think` suffix stay on,
and the client keeps `response_format=json_schema` (not `guided_json` + `json_object`).

## Exact launch command (Sunday morning)

From the box, after a fresh availability check and a new line in
`/workspace/junction-new/data/SPEND.md`:

```bash
# 1. Confirm stock (Ada first, else A100). Do not launch if neither is available.
# 2. Estimate in SPEND.md, then:
cd /workspace/junction-new/verda/extract
TASAN_VERDA_BUDGET_APPROVED=yes python3 -u serve/launch_live_endpoint.py --execute \
  --instance-type 1RTX6000ADA.10V \
  --location FIN-01 \
  --image 24.04.cuda13.4.docker \
  --volume-gb 200 \
  --watchdog-min 330 \
  --hostname tasan-extract-live
```

`launch_live_endpoint.py` is **not written tonight**. Sunday's controller should
clone the hardened patterns in `serve/phase2/launch_phase2.py`: pre-check
availability, create only `tasan-extract-live*` resources, copy the adapter +
demo + `app_export.json`, open the SSH tunnel, wait for `/health`, print a
public URL (not a raw IP in logs if it can be avoided), and **API-delete +
verify on any exit, including errors**. 404 on our key delete is success. Never
touch teammate keys (`tasan-ask-ephemeral` or otherwise).

If Ada is out Sunday morning, pass `--instance-type 1A100.22V --location FIN-01`
and record the A100 list price in the SPEND estimate first.

## Reachability / TLS note

Box egress to some Verda hosts has failed TLS in this environment. Before
Sunday, test from the box:

- `curl -I --max-time 15 https://<published-host>/health` (expect 200)
- if the box cannot complete TLS to the instance, use an SSH local-forward
  health check (`ssh -L 18000:127.0.0.1:443 …` + curl localhost) and treat
  public HTTPS as a judge/browser check, not a box-egress check.

Do not copy `VERDA_API_KEY` / client secrets onto the live GPU. Teardown is
always from the controller via the Cloud API.

## What we will pin after tonight's run

- Chosen model (8B+LoRA vs 32B) and the v2-test scores that justified it
- Measured single-note p50/p95 on the train-box sweep at conc 1 and 8
- The Sunday SKU + list price actually in stock
- The teardown verification snippet (instance + volume + our key gone)
