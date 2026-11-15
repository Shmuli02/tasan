# Tasan Extract (local package)

Sovereign, open-weight extraction of lung-pathway event dates from **SYNTHETIC** Finnish / Swedish / English notes, for the Tasan day-28 clock. See `../EXTRACT_PLAN.md` for the original plan and `RESULTS.md` for the measured 32B scores.

**No real patient data.** GPU instances are created only by `serve/launch_extract_instance.py --execute` with `TASAN_VERDA_BUDGET_APPROVED=yes`. **Do not run that now:** the measured A100 eval is finished, the instance was deleted at 22:35 EET on 14 Nov 2026, and scope is frozen (no LoRA, no sweep, no new Verda resources). Cleanup is scoped to IDs that script creates; never touch a teammate instance.

## Layout

| Path | What |
|---|---|
| `corpus/generate.py` | v1 template generator (seed `20261114`, IDs `SYN-P*`) |
| `corpus/data/` | v1: 600 documents, 120 patients, gold, stats |
| `corpus/generate_v2.py` | v2 held-out phrasing (seed `20261142`, IDs `SYN2-P*`) |
| `corpus/data_v2/` | v2: 600 documents, 120 patients, 40/80 dev/test split |
| `eval/regex_baseline.py` | Non-LLM floor extractor (tuned on v1 only) |
| `eval/evaluate.py` | P/R/F1 (exact and ±1 day) + patient-level alert scores |
| `eval/results/regex_report*` | v1 regex scores |
| `eval/results/regex_report_v2*` | **Untuned** v2 regex scores (dev vs test; test not used to add keywords) |
| `eval/results/qwen3_32b_v1_*` / `qwen3_32b_v2_*` | Qwen3-32B-AWQ predictions + reports from the FIN-01 A100 run |
| `RESULTS.md` | Headline scores, throughput, unit cost, nationwide sketch, spend |
| `prompt/` | System prompt + `schema.json` for vLLM guided decoding (Qwen3 thinking off) |
| `client/extract_client.py` | Concurrent OpenAI-compatible client (used against the tunneled vLLM during the GPU run) |
| `serve/` | Launch script + `startup.sh` (historical; do not `--execute` while scope is frozen) |
| `demo/server.py` | **Offline** local `POST /extract` (regex + cache). No GPU, no paid API. See below. |
| `SAMPLES.md` / `samples.json` | Judge-facing SYNTHETIC showcase (same 10 `note_id`s) |
| `app_export.json` | Builder pack: 10 notes, events + char offsets, `day_count`, `alert`, `source: qwen3-32b` (32B predictions from the A100 run) |
| `build_showcase.py` | Rebuilds the three showcase files from the corpora |

## Offline demo server (no GPU)

The live A100 was deleted after the eval. Judges and the Tasan Live app do **not** need a running GPU: the app bundles `app_export.json` as a static cache. For a local HTTP API that accepts `POST /extract` without Verda, run the demo server on this package. It never calls a model endpoint. It serves:

1. A **cache hit** when the request `note_id` / `document_id` or the SHA-256 of `text` matches a precomputed file (default: v1 regex predictions). Response `source` is `cache`, `model` is `regex_baseline+cache`.
2. Otherwise a **live regex** extract on the pasted text. Response `source` / `model` is `regex_baseline`.

It does not, by default, replay the 32B predictions (those live in `app_export.json` for the app). You can point `--cache` at a 32B predictions file if you want cached 32B events for corpus texts that match.

```bash
# from verda/extract/  ($0, no credentials, binds 127.0.0.1)
python3 demo/server.py --port 8088

# defaults: --host 127.0.0.1 --corpus corpus/data \
#           --cache eval/results/regex_predictions.json --cache-mode on

curl -s http://127.0.0.1:8088/health
# {"ok": true, "model": "regex_baseline", "backend": "regex", "cache_mode": "on", ... "synthetic": true}

curl -s -X POST http://127.0.0.1:8088/extract \
  -H 'Content-Type: application/json' \
  -d '{"note_id":"SYN-P0002-referral_letter-01","text":"...","lang":"fi"}'
```

Use a showcase `note_id` (for example `SYN-P0002-referral_letter-01`) and the full note `text` from `SAMPLES.md` / `app_export.json` if you want a cache hit on id or hash.

`GET /health` and `GET /` return status. `POST /extract` expects JSON with a non-empty `text`, and optionally `note_id` / `document_id`, `patient_id`, `lang`, `as_of`. The response includes `note_id`, `events` (type, date, `evidence_span`, `start` / `end` character offsets when known), `day_count`, `alert`, `model`, `source`, `as_of`. CORS is allowlisted for `https://petaled-trowel-90.beacon.host`, `http://localhost:5173` and `http://127.0.0.1:5173`.

Flags: `--cache-mode on|off|always` (default `on`); `--host` / `--port` (default `127.0.0.1:8088`). Keep the default host unless you intentionally need another interface.

Optional: score the saved 32B predictions again, still offline:

```bash
python3 eval/evaluate.py --corpus corpus/data --pred eval/results/qwen3_32b_v1_predictions.json --out /tmp/qwen_v1
python3 eval/evaluate.py --corpus corpus/data_v2 --pred eval/results/qwen3_32b_v2_predictions.json --out /tmp/qwen_v2
```

## Other local commands ($0)

```bash
python3 corpus/generate.py --seed 20261114 --out corpus/data
python3 corpus/generate_v2.py --seed 20261142 --out corpus/data_v2
python3 eval/regex_baseline.py --corpus corpus/data --out eval/results/regex_predictions.json
python3 eval/evaluate.py --corpus corpus/data --pred eval/results/regex_predictions.json --out eval/results/regex_report
python3 eval/regex_baseline.py --corpus corpus/data_v2 --out eval/results/regex_predictions_v2.json
python3 eval/evaluate.py --corpus corpus/data_v2 --pred eval/results/regex_predictions_v2.json --out eval/results/regex_report_v2
python3 build_showcase.py
```

## Regex floor (untuned) and 32B headline

- **v1 easy:** see `eval/results/regex_report.md` (exact F1 0.960). The corpus was later judged too template-like, which is why v2 exists.
- **v2 held-out, no keyword changes:** exact micro F1 is **0.000** on both dev (199 docs) and test (401 docs). Day-28 alert accuracy is ~0.80 only because most patients are not alerts (precision/recall 0).
- **Qwen3-32B-AWQ** on the same v2 test split: exact F1 **0.739**, alert accuracy **0.963**. Full table, throughput (0.669–0.746 notes/s at concurrency 16) and **$0.89–$0.99 per 1,000 notes** are in `RESULTS.md`.

## Showcase notes

`SAMPLES.md`, `samples.json` and `app_export.json` share these stable IDs:

`SYN-P0002-referral_letter-01`, `SYN-P0003-ct_report-02`, `SYN-P0002-biopsy_note-02`, `SYN-P0001-mdt_minutes-04`, `SYN-P0002-mdt_minutes-03`, `SYN-P0001-discharge_summary-05`, `SYN-P0087-pathology_report-02`, `SYN-P0051-oncology_note-04`, `SYN2-P0010-referral_letter-01`, `SYN2-P0014-ct_report-02`.

`app_export.json` is already regenerated with `source: "qwen3-32b"`. A GPU-paraphrased sibling of `SYN2-P0010-referral_letter-01` was planned and then dropped with the rest of phase 2.
