# How we built it — numbers for the Builder

Compact figures for the Tasan “How we built it” page. Every value is copied from a project file. Prefer the rounded figures as published in `verda/extract/RESULTS.md` and `data/SPEND.md`; the JSON companion (`HOW_WE_BUILT_NUMBERS.json`) also stores more precise eval digits where the raw report has them.

Times are Europe/Helsinki (EET, UTC+2) on 14 Nov 2026. All Extract notes are **SYNTHETIC**. The measured 32B eval numbers are unchanged. **LoRA** and the **concurrency 1/8/32/64 sweep** are **not completed**. Measuring stopped at 23:12. Any figure that is not a completed measurement is labelled as an estimate.

## Tasan Extract

| Item | Value | Source |
|---|---|---|
| Model | Qwen3-32B-AWQ (`Qwen/Qwen3-32B-AWQ`), thinking off, OpenAI `json_schema` | `verda/extract/RESULTS.md`; `verda/extract/eval/results/qwen3_32b_v1_predictions_metrics.json` |
| Serving | vLLM on a Verda GPU instance, bound to 127.0.0.1 | `verda/extract/RESULTS.md`; `data/SPEND.md` §8.2 |
| GPU / instance type (measured eval) | 1× A100 SXM4 80 GB, `1A100.22V` on-demand | `verda/extract/RESULTS.md`; `data/SPEND.md` §8.2 |
| Location | FIN-01 (Finland). All Verda GPU regions in the catalogue are FIN-01/02/03 | `verda/extract/RESULTS.md`; `verda/EXTRACT_PLAN.md` §2.1 |
| List price (eval A100) | $2.386 / hour | `data/SPEND.md` §8.2; `verda/extract/RESULTS.md` |
| Eval instance id (prefix) | `e60ea3d7…` (`tasan-extract`), 21:06:41–22:35 EET | `data/SPEND.md` §8.2 |
| Corpus | 600 + 600 SYNTHETIC notes, 120 patients each; v1 seed 20261114, v2 seed 20261142 (199 dev / 401 test docs) | `verda/extract/RESULTS.md`; `verda/extract/corpus/README.md`; `verda/extract/corpus/data/stats.json`; `corpus/data_v2/stats.json` |
| Languages (v1 / v2) | ≈ 74.5% / 74.8% Finnish, 15.7% / 15.2% Swedish, 9.8% / 10% English | `verda/extract/corpus/data/stats.json`; `corpus/data_v2/stats.json`; `corpus/README.md` |
| Exact F1, 32B, v1 all (600) | **0.954** (P 0.955 / R 0.953; JSON 0.9539) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v1_report.json` |
| Exact F1, regex, v1 all | **0.960** (P 0.976 / R 0.944; JSON 0.9597) | `verda/extract/RESULTS.md`; `eval/results/regex_report.json` |
| Exact F1, 32B, v2 all (600) | **0.742** (P 0.765 / R 0.720; JSON 0.7417) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v2_report.json` |
| Exact F1, 32B, v2 test (401, held-out) | **0.739** (P 0.765 / R 0.715; JSON 0.7392) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v2_report.json` |
| Exact F1, regex untuned, v2 test | **0.000** | `verda/extract/RESULTS.md`; `eval/results/regex_report_v2.json` |
| ±1 day F1, 32B, v1 all / v2 all / v2 test | 0.964 / 0.763 / 0.761 | `verda/extract/RESULTS.md` |
| Day-28 alert accuracy, 32B, v1 all | **0.983** (P 1.000 / R 0.938 / F1 0.968; JSON acc 0.9833) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v1_report.json` |
| Day-28 alert accuracy, 32B, v2 all | **0.958** (P 0.913 / R 0.875 / F1 0.894; JSON acc 0.9583) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v2_report.json` |
| Day-28 alert accuracy, 32B, v2 test | **0.963** (P 0.875 / R 0.933 / F1 0.903; JSON acc 0.9625) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v2_report.json` |
| Day-28 alert accuracy, regex untuned, v2 test | 0.812 (P 0 / R 0; most patients are not alerts) | `verda/extract/RESULTS.md`; `eval/results/regex_report_v2.json` |
| Throughput, 32B, concurrency 16, v1 | **0.746 notes/s**, latency p50 **18.2 s** / p95 **40.7 s** (803.8 s wall) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v1_predictions_metrics.json` |
| Throughput, 32B, concurrency 16, v2 | **0.669 notes/s**, latency p50 **20.5 s** / p95 **45.8 s** (896.3 s wall) | `verda/extract/RESULTS.md`; `eval/results/qwen3_32b_v2_predictions_metrics.json` |
| Cost per 1,000 notes (list price) | **$0.89** (v1) / **$0.99** (v2) | `verda/extract/RESULTS.md` |
| Nationwide yearly sketch | 2,994 new lung+tracheal cases/yr (Finnish Cancer Registry 2020–2024 average) × **5 notes/patient (assumption)** = 14,970 notes/yr ≈ **$15/yr** at $0.99/1k (or ≈ **$13/yr** at $0.89/1k) | `verda/extract/RESULTS.md` |
| Extract spend, eval run only (§8) | ≈ $3.77 preferred (RTX aborts $0.17 + eval A100 $3.60 including ≈ 48 min idle). Increment-grossed alternative ≈ $4.62; a short note also says ≈ $4.5 | `data/SPEND.md` §8.3; `verda/extract/RESULTS.md` |
| Phase 2 first abort | `d81e14db…`, `1A100.22V` on-demand, FIN-01, 22:43:04–22:50:39 (7.58 min). Train failed early. ≈ **$0.31** / ≈ $0.40 increment-grossed. **LoRA not completed** | `data/SPEND.md` §10; `verda/extract/eval/results/phase2/LORA_STATUS.md` |
| Phase 2 LoRA retry | `715c7100…`, `1A100.22V` **spot** ($1.193/h), FIN-01, 22:56:19–23:03:47 (**7.47 min**, ≈ 7.5 min). Crashed before the first optimizer step (`transformers` 5.20.2, `warmup_ratio`). No adapter, no 8B/LoRA score. ≈ **$0.16** / ≈ $0.21 increment-grossed. **LoRA not completed** | `data/SPEND.md` §12; `verda/extract/eval/results/phase2/LORA_STATUS.md` |
| Concurrency 1/8/32/64 sweep | **Not completed.** Estimate written at 23:11 (not incurred). User stopped measuring at 23:12; instance never created | `data/SPEND.md` §13–14 |
| Extract spend (final) | **≈ $4.24** life-based (≈ **$5.23** increment-grossed) | `data/SPEND.md` §14 |
| Deletion | Eval A100 deleted 22:35:03; phase-2 boxes deleted 22:50:39 and 23:03:47. **Final API check 23:13: 0 instances, 0 volumes** | `data/SPEND.md` §8.2, §10, §12, §14 |
| Live GPU endpoint | **Not running.** Offline pack: `verda/extract/app_export.json`, 10 notes, `source: qwen3-32b` | `verda/extract/app_export.json`; `verda/extract/README.md` |
| Showcase | 10 labelled synthetic notes | `verda/extract/SAMPLES.md` |

Headline measured figures to keep on the page: exact F1 **0.74** on v2, day-28 alert accuracy **0.96**, **$0.89–$0.99** per 1,000 notes, **0.67–0.75** notes/s at concurrency 16.

## Pathway Twin

| Item | Value | Source |
|---|---|---|
| Hardware | `1V100.4V` **spot**, FIN-01, $0.122/h (GPU unused; no CPU type in stock). Image `24.04.cuda12.9-v100.docker` | `data/SPEND.md` (smoke actual and “4. Run (A), actual”); `sim/README.md` |
| Smoke (20:30–20:34 EET) | 2 jobs (Lapland baseline 3.7 s, zero_effect 3.2 s, 2,000 years each) + 1 HTTP `POST /run`; Docker build 23 s, 271 MB; byte-identical to local; ≈ **$0.01** | `data/SPEND.md` §2; `sim/README.md` |
| Full run (A) (20:37:33–21:10:16 EET) | **132** scenario jobs (22 counties × 6 scenarios × **20,000** simulated years = **2.64 M** county-years) + **5** ABC jobs (4,000 particles). Docker build **21 s**. Scenario wall **1,372 s**, mean **41.5 s/job**, 4 workers. Calibration **7–21 s** each. Byte-identical to local | `data/SPEND.md` (section “4. Run (A), actual”); `sim/README.md`; `sim/results_verda/run_log.json` |
| Run (A) instance life / cost | 32.7 min; **≈ $0.07–0.08** | `data/SPEND.md` §4 |
| Serverless (B) (21:37–21:42 EET) | Image pushed (build 18 s, push 8 s); deployment created and deleted; **0 jobs ran** (TLS to `tasks.verda.com`). Push instance 1.4 min, ≈ **$0.02** | `data/SPEND.md` §7; `sim/README.md` |
| Twin total spend | **≈ $0.11** | `data/SPEND.md` §7; `sim/README.md` |
| Validation | PASS, 14 Nov ~20:28 EET (Docker check ran on the smoke instance) | `sim/README.md` |

## Ask Tasan

| Item | Value | Source |
|---|---|---|
| Status | **Wired in the live app**, not only planned. Local fact-pack fallback remains | `app/src/components/AskPanel.tsx`; `app/src/lib/askLlm.ts`; `app/server/README.md` |
| Model | `kimi-k3-1-pro` on the Verda Inference API | `app/server/SPEND.md`; `app/server/README.md`; `verda/EXTRACT_PLAN.md` §2.4 |
| Where inference runs | EU / **Germany** — do not call this Finland-hosted. App badge: “EU-hosted inference · Verda” | `app/server/SPEND.md`; `app/src/lib/askLlm.ts`; `verda/EXTRACT_PLAN.md` §2.4 |
| Proxy | Beacon Worker https://petaled-trowel-90-ask.worker.beacon.host (Verda CPU.4V.16G-class was out of stock; instance spend $0.00) | `app/server/SPEND.md`; `app/server/README.md` |
| Public app | https://petaled-trowel-90.beacon.host/ | `app/PUBLIC_URL.txt`; `app/server/SPEND.md` |
| Eval recorded | 18-prompt trick suite at 21:34:55 EET, 18 live LLM calls (plus local path). Not a 30-question report | `app/server/TRICK_SUITE.md` |
| Ask spend | Instance **$0.00**; inference **≈ $2–$3** (about 26 chat-completion calls) | `app/server/SPEND.md` |

## Team spend (sum of sourced subtotals)

| Item | Value | Source |
|---|---|---|
| Twin + Extract preferred | ≈ $0.11 + ≈ $4.24 = ≈ **$4.35** | `data/SPEND.md` §7, §14 |
| Plus Ask Tasan inference | ≈ **$6.35–$7.35** | those rows + `app/server/SPEND.md` |
| Extract increment-grossed alternative, plus Twin and Ask | ≈ **$7.34–$8.34** | `data/SPEND.md` §14 + §7 + `app/server/SPEND.md` |

Machine-readable copy: `verda/HOW_WE_BUILT_NUMBERS.json`.
