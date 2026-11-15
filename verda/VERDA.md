# Tasan on Verda — process document (Junction 2026 Compute Track)

*JN Verda Lead. Written 14 Nov 2026, evening, Europe/Helsinki (EET, UTC+2); updated after measuring stopped at 23:12, from `data/SPEND.md` §10–14.*
*This is the process write-up for the Verda Compute Track (Ambition, Fit, Working prototype, Path to scale; 25% each). It covers all three components. Every figure below is taken from project files; none is newly measured in this pass. No Verda resource was created for this document, and no paid API call was made.*

**SYNTHETIC DOCUMENTATION FOR EXTRACT.** Tasan Extract is evaluated only on invented clinical notes. No real patient text, name or date was used.

**Scope as of this document.** The user stopped all measuring at **23:12 EET**. LoRA and the concurrency 1/8/32/64 sweep are **not completed**. A live GPU `/extract` endpoint is **not** up; the app uses the cached `app_export.json` pack. Verified via API at **23:13: 0 instances, 0 volumes**. No further Verda resources should be created.

Related files: `data/SPEND.md` (instance actuals, including §10–14), `verda/EXTRACT_PLAN.md` (plan), `verda/extract/RESULTS.md` (measured Extract scores), `verda/extract/eval/results/phase2/LORA_STATUS.md`, `sim/README.md` (Pathway Twin), `app/server/SPEND.md` and `app/server/TRICK_SUITE.md` (Ask Tasan).

---

## 1. What we built, in one page

Tasan is a lung-cancer pathway clock for Finland's 22 wellbeing services counties. Public registries do not publish referral→diagnosis times or 6-week compliance, so the clock has to be filled from clinical notes, and a county-scale "what if we alert at day 28?" question has to be simulated. We used Verda in Finnish data centres for three parts:

| Component | Role | Verda product actually used | Status |
|---|---|---|---|
| **Tasan Extract** | Open-weight LLM on a GPU in Finland extracts pathway event dates from **SYNTHETIC** Finnish / Swedish / English notes and derives the day-28 alert | GPU instance: `1A100.22V` on-demand in **FIN-01** ($2.386/h), vLLM serving `Qwen/Qwen3-32B-AWQ`. Two aborted `1RTXPRO6000.30V.CC` on-demand boots in FIN-03 while the A100 was out of stock | Measured eval done. Instance and volume deleted 22:35 EET and verified. Cached 10-note pack in `verda/extract/app_export.json` (`source: qwen3-32b`) |
| **Pathway Twin** | County-level microsimulation (referral → diagnosis → first treatment), calibrated to Finnish Cancer Registry curves | GPU *instance used as a CPU box*: `1V100.4V` **spot** in **FIN-01** ($0.122/h), because no CPU instance type was in stock. Serverless Containers job deployment on AMD Rome+ CPU was created, then deleted, after job submit failed | Full 132+5 job run done; outputs byte-identical to local. Serverless jobs never started |
| **Ask Tasan** | Grounded AI analyst in the Tasan app (cited answers, refusals, draft briefs) | **Verda Inference API** (`kimi-k3-1-pro`, EU / **Germany**, not Finland). The API key is held by a **Beacon Worker** proxy, not a Verda CPU, because `CPU.4V.16G`-class instances were out of stock | Wired in the live app at https://petaled-trowel-90.beacon.host/ with a local-facts fallback |

All three Cloud GPU locations in the catalogue (`GET /v1/locations`) are in Finland: FIN-01, FIN-02, FIN-03. There is no non-Finnish instance location. Inference, separately, lists `datacenters: [{country_code: "DE"}]`.

---

## 2. Tasan Extract

### 2.1 Why compute

The product gap is that pathway timestamps (referral, CT, biopsy, pathology, MDT, treatment decision, treatment start) are buried in free-text clinical notes. Those notes are health data and must not be sent to a third-party model API. "EU-hosted" is not the same as "in Finland": Verda Inference runs in Germany. A weekend-scale claim also needs a measured comparison — precision/recall, notes/s, latency, and cost per 1,000 notes — on a 32B multilingual instruct model with structured JSON output, against a regex baseline, on hundreds of gold-labelled notes. That is a GPU job, not a laptop demo.

The corpus is entirely synthetic (v1 seed `20261114`, 600 documents / 120 patients, about 75% Finnish / 15% Swedish / 10% English; v2 seed `20261142`, same size, held-out phrasing, 40/80 dev/test split). Gold labels are generated with the notes. No real EHR text.

### 2.2 Which Verda product, and why

- **GPU instance in FIN-01**, not the Inference API, so weights and notes stay on a box in Finland.
- **`1A100.22V` on-demand** (1× A100 SXM4 80 GB, $2.386/h): the only 80 GB SKU that was in stock for the successful launch, enough for Qwen3-32B-AWQ + batching. On-demand rather than spot ($1.193/h) so a mid-eval eviction would not break the latency/throughput measurement.
- Image `24.04.cuda13.4.docker`, 200 GB OS volume, vLLM bound to `127.0.0.1`, SSH tunnel only. No public endpoint was opened.
- **Not used:** H100 (out of stock and $5.241/h); 8-GPU confidential-computing types in FIN-03 ($38.79–$101.3/h — the scale-path mention for real patient data, not this demo); V100 16 GB (cannot hold 32B AWQ); Instant Clusters.
- Plan B, declared before launch because the A100 was briefly out of stock: `1RTXPRO6000.30V.CC` on-demand in FIN-03 ($2.893/h). Those two boots were aborted (see §2.6).

### 2.3 What ran (Europe/Helsinki)

| When (EET, 14 Nov 2026) | What |
|---|---|
| 20:42–20:44 | Read-only discovery (`GET` locations, types, availability, inference catalogue). Cost $0. Plan in `verda/EXTRACT_PLAN.md`. |
| ~20:55 | Local corpus, regex baseline, eval harness, demo server, launch script. Cost $0. |
| 20:59:50–21:01:52 | Abort 1: `1RTXPRO6000.30V.CC` on-demand, FIN-03, instance `cedfe23e…`, ~2.0 min. SSH dispatch timeout; `finally` deleted. |
| 21:03:45–21:05:21 | Abort 2: same type, instance `1ac3365d…`, ~1.6 min. Same failure mode. |
| 21:06:41 | A100 created: instance `e60ea3d7-a593-4c34-b208-64cfec0eb8c4`, hostname `tasan-extract`, `1A100.22V` on-demand, FIN-01, $2.386/h, image `24.04.cuda13.4.docker`, 200 GB volume `3300c6fa…`. Running 21:07:31. |
| 21:13:16 | vLLM ready with Qwen3-32B-AWQ (thinking off, OpenAI `json_schema`). 5.7 min after boot. |
| 21:15 / 21:16 | 2-doc smoke (concurrency 1) and 16-doc probe (concurrency 8). |
| 21:18:43–21:32:07 | v1 extract, 600 notes, concurrency 16, all HTTP 200, 803.8 s, 0.746 notes/s, p50 18.2 s / p95 40.7 s. |
| 21:32:07–21:47:03 | v2 extract, 600 notes, concurrency 16, all HTTP 200, 896.3 s, 0.669 notes/s, p50 20.5 s / p95 45.8 s. |
| 21:47–22:35 | **Idle.** Extracts had finished; the box sat up for ≈ 48 min. Our mistake. |
| 22:35:03 | API delete of the eval A100 (`PUT /instances` action=delete, `delete_permanently=true`, volume included). HTTP 204. |
| 22:43:04–22:50:39 | Phase 2 first launch (`data/SPEND.md` §10): `1A100.22V` **on-demand**, FIN-01, instance `d81e14db…`, hostname `tasan-extract-p2`, 200 GB volume `f386cf99…`. LoRA train failed early at the docker train step (likely `pip install peft trl datasets accelerate` in the vLLM image / PEP 668 / TRL API). No results tarball. Controller deleted instance, volume and our key; verified 22:50:42 (lists empty). Life **7.58 min**, ≈ **$0.31** life-based / ≈ $0.40 increment-grossed. |
| 22:56:19–23:03:47 | Phase 2 retry (`data/SPEND.md` §12): `1A100.22V` **spot**, FIN-01, **$1.193/h**, instance `715c7100…`, volume `ae53d27d…`. Loaded 481 SYNTHETIC SFT rows, Qwen3-8B, PEFT LoRA applied (43,646,976 trainable params, 0.5301%). **Crashed before the first optimizer step** on `transformers` 5.20.2: `TrainingArguments.__init__() got an unexpected keyword argument 'warmup_ratio'`. No adapter, no 8B/LoRA eval, no sweep. Logs in `verda/extract/eval/results/phase2/` (`LORA_STATUS.md`). Deleted and verified 23:03:50 (lists still empty at 23:10:03). Life **7.47 min** (≈ 7.5 min), ≈ **$0.16** life-based / ≈ $0.21 increment-grossed. |
| 23:11 | Sweep-only estimate written (`data/SPEND.md` §13). **No create call.** |
| 23:12 | User stopped all measuring. The sweep instance was never created (`data/SPEND.md` §14). |
| 23:13 | **Verified via API: 0 instances, 0 volumes.** Only the SSH key `tasan-ask-ephemeral` (Ask Tasan, not ours) remains. |

**LoRA: not completed.** **Concurrency 1/8/32/64 sweep: not completed** (never launched). There is no 8B or LoRA quality score and no sweep throughput figure. Measured Extract numbers below are unchanged from the first A100 eval (concurrency 16 only).

### 2.4 Results

From `verda/extract/RESULTS.md` (micro exact P/R/F1 unless noted). Underlying JSON is in `verda/extract/eval/results/`.

| System | Split | Docs | Exact P / R / F1 | ±1 day F1 | Day-28 alert accuracy |
|---|---|---:|---|---:|---|
| Regex (v1-tuned) | v1 all | 600 | 0.976 / 0.944 / **0.960** | — | 0.975 (see regex report) |
| **Qwen3-32B-AWQ** | v1 all | 600 | 0.955 / 0.953 / **0.954** | **0.964** | **0.983** (P 1.000 / R 0.938 / F1 0.968) |
| Regex (untuned) | v2 test | 401 | 0.000 / 0.000 / **0.000** | 0.000 | 0.812 (P 0 / R 0) |
| **Qwen3-32B-AWQ** | v2 all | 600 | 0.765 / 0.720 / **0.742** | **0.763** | **0.958** |
| **Qwen3-32B-AWQ** | v2 test (held-out) | 401 | 0.765 / 0.715 / **0.739** | **0.761** | **0.963** |

The v1 corpus is too close to the regex templates, which is why v2 exists. On v2, gold dates are still recoverable by a careful human; the regex fails because of held-out keywords and date formats it was never taught.

Throughput was measured only at concurrency 16 (the 1/8/32/64 sweep is **not completed**):

| Corpus | Notes/s | Latency p50 / p95 (s) | $ / 1,000 notes at $2.386/h |
|---|---:|---|---:|
| v1 | 0.746 | 18.2 / 40.7 | **$0.89** |
| v2 | 0.669 | 20.5 / 45.8 | **$0.99** |

Showcase notes (synthetic, clearly labelled) are in `verda/extract/SAMPLES.md`. The Builder pack `verda/extract/app_export.json` holds the same 10 stable `note_id`s with 32B events, evidence spans, `day_count` and `alert`.

### 2.5 Cost and deletion

Preferred actuals (life minutes, unused 10-minute increment refunded). §8 figures are unchanged; §10 and §12 add the two phase-2 attempts. Final total from `data/SPEND.md` §14.

| Line | Preferred | If 10-min increments were kept in full |
|---|---:|---:|
| RTX abort 1 | $0.10 | $0.48 |
| RTX abort 2 | $0.08 | $0.48 |
| Eval A100 instance (88.49 min = 1.475 h × $2.386) | $3.52 | $3.58 |
| Eval A100 200 GB storage | $0.08 | $0.08 |
| §8 subtotal (eval run) | ≈ $3.77 | ≈ $4.62 |
| Phase 2 first abort, on-demand A100, 7.58 min (§10) | $0.31 | $0.40 |
| Phase 2 LoRA retry, spot A100, 7.47 min (§12) | $0.16 | $0.21 |
| **Final Extract total** | **≈ $4.24** | **≈ $5.23** |

Of the eval A100 bill, ≈ 48 min idle after 21:47 is ≈ **$1.91**. A shorter coordinator note on the §8 run quoted ≈ $4.5 (the increment-grossed range for that run only). That is not the final Extract total.

**Deletion, verified.** The eval A100 was API-deleted at 22:35:03 EET (`data/SPEND.md` §8.2). The two phase-2 boxes were deleted by the controller `finally` path at 22:50:39 and 23:03:47, each with volume and our key, and verified empty of our IDs. **Final check, 23:13 EET (`data/SPEND.md` §14): 0 instances, 0 volumes.** The remaining project key `tasan-ask-ephemeral` was left untouched throughout. The eval launcher’s own post-delete verify at 22:36 hit HTTP 401 (expired OAuth token); the coordinator API check is the successful verification for that box.

### 2.6 Failures and lessons (Extract)

- **Aborted RTX boots.** While the A100 was out of stock, two Plan B `1RTXPRO6000.30V.CC` launches died when an SSH dispatch timeout raised out of the launcher. Resources were deleted in `finally`. The SSH helper was then hardened so a timeout no longer aborts cleanup.
- **Idle A100 ≈ 48 min.** The 32B evals finished at 21:47; the instance was only deleted at 22:35. That idle window is about $1.91 we should not have spent. Delete as soon as the measured work is copied off.
- **OAuth token expiry on cleanup.** The launcher’s post-delete verify at 22:36 returned 401, the same class of failure as the Twin run (see §3.6). Refresh the token on 401; do not treat a failed verify as “still running” without a fresh token.
- **SSH-key mix-up (shared project).** A teammate’s manual cleanup at 21:10 deleted *all* SSH keys, including `tasan-extract-ephemeral`. The already-running A100 kept accepting the key that was already on the box. Scripts must delete only their own key by id. See §5.
- **LoRA, not completed.** A first on-demand A100 (7.58 min, ≈ $0.31) failed at the train step with no packed logs. The retry on a **7.47-min spot A100** (≈ **$0.16**) loaded Qwen3-8B and applied LoRA, then crashed before the first optimizer step on `transformers` 5.20.2 (`warmup_ratio` no longer accepted on `TrainingArguments`). No adapter and no scored 8B/LoRA result. See `verda/extract/eval/results/phase2/LORA_STATUS.md`. It was not retried (a scored result was more than ~30 min away).
- **Concurrency 1/8/32/64 sweep, not completed.** A sweep-only estimate was written at 23:11 (`data/SPEND.md` §13; those expected costs are **estimates only** and were not incurred). The user stopped measuring at 23:12; the sweep instance was never created.

---

## 3. Pathway Twin

*Built and operated by JN Data Analyst. Summarised here from `sim/README.md` and `data/SPEND.md`. This track did not modify `sim/` or the Twin instances.*

### 3.1 Why compute

The Twin is a lung-cancer pathway microsimulation for all 22 wellbeing services counties: 132 scenario jobs (22 × 6 scenarios, 20,000 simulated years each) plus 5 ABC calibration jobs (4,000 accepted particles per collaborative area). That is 2.64 million simulated county-years, calibrated to Finnish Cancer Registry timing curves (Taulukko 4.1 / 4.5). It is the scale a laptop can run once, but Verda is how we show the same image running in a Finnish data centre, byte-identical to local, and how we tried the serverless path that a county rollout would use.

The model is numpy on CPU. A GPU does not speed it up; we said so in the plan and still ended up on a V100 only because **no CPU instance type was available** in FIN-01/02/03.

### 3.2 Which Verda product, and why

- **Chosen for the work that ran:** a `1V100.4V` **spot** instance in FIN-01 ($0.122/h) as a cheap 4 vCPU box. The GPU was unused. Image `24.04.cuda12.9-v100.docker`, 50 GB OS volume, Docker build of `sim/Dockerfile` on the box.
- **Preferred, and attempted:** Serverless Containers batch jobs on AMD Rome+ `CPU.8V.32GC` ($0.11/h per replica), plus Verda Container Registry. Better fit for embarrassingly parallel CPU work once jobs can be submitted.
- **Not used, on purpose:** GPU serverless (L40S / H100 would have been $21 / $55 per pass for no speed-up); Instant Clusters.

### 3.3 What ran (Europe/Helsinki, 14 Nov 2026)

| When (EET) | What |
|---|---|
| 20:30:30–20:34 | **Smoke test.** `1V100.4V` spot, FIN-01, instance `c3a6358a…`. Docker 29.9.2 built the image in 23 s (271 MB). 2 jobs (Lapland × baseline 3.7 s, Lapland × zero_effect 3.2 s, 2,000 simulated years) + 1 HTTP `POST /run`. Outputs byte-identical to local (runtime field excluded). Deleted; API at ~20:34: 0 instances, 0 volumes, 0 trash, 0 SSH keys. |
| 20:37:33–21:10:16 | **Run (A), full single-instance.** `1V100.4V` spot, FIN-01, instance `d01e730d…`. Docker build 21 s. **132 scenario jobs in 1,372 s** (mean 41.5 s/job, 4 workers) + **5 calibration jobs, 7–21 s each**. Results copied to `sim/results_verda/` at 21:04:49. |
| 21:37–21:42 | **Run (B), serverless.** Temporary `1V100.4V` spot `4375e56c…` (1.4 min) built (18 s) and pushed (8 s) `tasan-sim-twin:0.1.0` (271 MB) to `vccr.io`. Job deployment `tasan-sim-twin` (CPU Node size 8, max 8 replicas, deadline 600 s) became `ready` in 6 s. **All 137 job submissions failed before reaching Verda** (TLS to `tasks.verda.com`). Deployment deleted 21:41:46; GET 404 at 21:41:47. No replica ran. |

### 3.4 Results

- Validation gate: PASS (local, 14 Nov ~20:28 EET), 8/8 checks on the box; Docker check ran on the Verda smoke instance instead (no Docker on the dev box).
- Full run: all 132 job JSON/CSV outputs and all 5 posteriors are **byte-identical** to the local run with the same seeds (runtime fields excluded). Seeds: 1 for scenarios, 20261114 for calibration.
- In-container aggregate step crashed (it globbed calibration JSONs). Only the in-container summary was affected; it was fixed and re-aggregated locally.
- Serverless: image push and deployment create succeeded; **zero jobs executed**.

Headline model outputs and limitations stay in `sim/README.md`. They are simulation outputs with labelled assumptions, not forecasts, and they do not claim lives saved.

### 3.5 Cost and deletion

| Line | Cost | Deletion |
|---|---:|---|
| Smoke | **≈ $0.01** (at most $0.02): ≈2.2 min × $0.122/h, 50 GB for ≈3.5 min | First delete call failed (404, OS volume passed twice). Fixed by hand: instance discontinued 20:32:34, volume deleted permanently ~20:33, key deleted 20:32:34. API ~20:34: nothing left |
| Run (A) | Instance life 32.7 min × $0.122/h = **$0.067** (40-min increment $0.081). Storage ≈ $0.001. **Total ≈ $0.07–0.08** | Automated cleanup at 21:04:49 failed with **HTTP 401** (OAuth access token expired after ~27 min). Manual delete 21:10:16; volume 21:10:17. API 21:10:24: none of *this run’s* instances, volumes or keys remain |
| Run (B) | Push instance ≈ **$0.02** + registry storage **< $0.01**. Deployment cost ≈ $0 (no replicas) | Push instance, volume and key deleted and checked by ID. Deployment 404. |
| **Twin total** | **≈ $0.11** of the $5 sim cap | See lessons below for leftovers |

As of the 21:43 EET spend note, the registry image `tasan-sim-twin:0.1.0` and pull credential `tasan-sim-pull` were **left on purpose** for a retry (≈ $0.0001/h for the image). This document does not re-query the live API.

### 3.6 Failures and lessons (Twin)

- **Token-expiry cleanup failure.** The OAuth access token expired after about 25–30 min. Cleanup of run (A) got HTTP 401 at 21:04:49 and the instance lived ~6 extra minutes until a manual delete. `verda_api.py` now refreshes the token on 401.
- **SSH-key mix-up.** In that manual cleanup, *all* project SSH keys were deleted, including `tasan-extract-ephemeral` belonging to the Extract A100. The Extract instance and disk were not touched. Scripts now delete only their own key by id. Never “delete all keys” in a shared project.
- **TLS egress block to `tasks.verda.com`.** The dev box’s network egress fails the TLS handshake to `tasks.verda.com` (resolves to the sandbox proxy 198.18.0.1; repeatable `TLS alert, decode error`). `api.verda.com` and `vccr.io` work. No serverless job was queued. Check that `https://tasks.verda.com` is reachable *before* creating a deployment.
- **Registry push credentials** cannot be created through the documented API (console-first). The first serverless attempt was blocked on that; the second used a console-created credential and got as far as submit.
- **OS volume can survive instance deletion.** Pass the volume id once (it appears in both `os_volume_id` and `volume_ids`), then explicitly delete permanently and verify `/volumes` and `/volumes/trash`.
- **Check availability first.** No CPU instance was in stock all evening; an old V100 spot was the cheapest machine on offer. The 4 vCPU V100 host was about 4× slower per core than the dev box (41 s vs ~10 s per job). The serverless AMD Rome+ tier is the better CPU fit once job submit works.
- Tag resources with a name prefix (`tasan-sim-`, `tasan-extract-`) and never delete another agent’s box.

---

## 4. Ask Tasan

### 4.1 Why compute, which product, and what actually shipped

Ask Tasan is the in-app analyst: questions about the sourced fact pack (81 facts), with citations, refusals (lives saved, treatment choice, 6-week compliance where no public statistic exists), and draft pilot briefs. The Verda product that fits this is the **Inference API** — “serve open-weight models in your app with zero setup” — not a self-hosted GPU. The catalogue for this project had `kimi-k3-1-pro` enabled (standard tier; $2.00 / $0.20 / $10.00 per 1M input / cache / output). It runs in **Germany**, not Finland. Wording in the app is “EU-hosted inference · Verda”. Do not describe it as Finland-hosted.

The API key must not go in client code or the repo. The planned host for `app/server/proxy.mjs` was a Verda on-demand `CPU.4V.16G` / `CPU-TURIN.4V.16G` in FIN-01/02/03. **Those types returned no capacity** on 14 Nov 2026 (a probe create of `CPU.4V.16G` in FIN-01 came back 503). The cheapest in-stock GPU would have been an A100 at $2.386/h, which was out of scope for this proxy and would have breached the $25 Ask cap if left up through judging. So the portable proxy was deployed as a **Beacon Worker**:

- Proxy: https://petaled-trowel-90-ask.worker.beacon.host
- Public app: https://petaled-trowel-90.beacon.host/
- Model: `kimi-k3-1-pro` via `https://inference.verda.com/v1`
- `VERDA_API_KEY` is a Worker secret only (name listed; value never stored in git, logs or the client)
- CORS locked to the public app and localhost
- Instance ID: none. Verda Cloud VM spend: **$0.00**

### 4.2 Is it actually wired up?

**Yes — not only planned.** Evidence in the app, not just the plan:

- `app/src/lib/askLlm.ts` calls `POST {proxy}/ask` when `VITE_TASAN_PROXY_URL` is set. `app/src/components/AskPanel.tsx` streams that path, then tags a valid answer with `EU-hosted inference · Verda`. Action, why, and several refusal classes short-circuit to the deterministic local pack (`app/src/lib/askLocal.ts`) so both paths agree.
- `app/.env.local` and `app/.env.production.local` set `VITE_TASAN_PROXY_URL` to the Worker URL above (the URL is a public origin, not a credential). The 21:46 EET production bundle `app/dist/assets/index-miU57519.js` contains that host and the Verda tag. The offline single-file build also embeds the URL; `?ask=offline` or `?llm=0` forces the local pack.
- A trick suite ran at **21:34:55 EET** (`app/server/TRICK_SUITE.md`): 18 prompts, 18 live LLM calls to `kimi-k3-1-pro`, plus the local path. English refusals (lives saved, treatment choice) passed on the LLM path; several other LLM answers were rejected by the client validator (sentence without a fact id, unverified numbers, or a brief that was not schema-valid JSON) and would fall back to the local pack. Local routing was tightened at 21:38; the LLM path was not re-run after that.

There is no separate 30-question eval report in the tree. The documented live check is this 18-prompt suite. Early STATUS notes (20:52 EET) that described Ask Tasan as “EXAMPLE / bundled facts only” are **out of date**.

### 4.3 Cost

From `app/server/SPEND.md` (updated 21:34 EET). These figures are **not** in `data/SPEND.md`.

| Item | Figure |
|---|---|
| Verda Cloud CPU instance | **$0.00** |
| Inference tokens (smoke tests + 18-prompt trick suite + earlier empty-content probes; about 26 chat-completion calls) | **≈ $1.50–$3.00** (central estimate under $2, $3 ceiling for hidden thinking tokens on pre-patch probes) |
| **Ask Tasan running total** | **≈ $2–$3**, under a $25 cap |

Exact usage was to be confirmed in the Verda console; that file does not store keys or raw usage payloads. This process doc did not re-read the console.

---

## 5. Shared-project incidents (cross-cutting)

These affected more than one component and should be told once, honestly.

1. **Token-expiry cleanup (Twin run A, 21:04 EET; Extract launcher verify, 22:36 EET).** The Cloud API OAuth access token expires after roughly 25–30 minutes. A long run that deletes in `finally` with the original token will 401, and the resource can keep billing. Refresh on 401; if the controller dies, delete by hand and verify with a fresh token.
2. **SSH-key mix-up (21:10 EET).** Manual cleanup of the Twin instance deleted every SSH key in the project, including Extract’s `tasan-extract-ephemeral`. The Extract A100 was not deleted. A key already installed on a running VM usually keeps working; the owner’s later key-delete will 404 (and should treat that as success). Delete only your own IDs.
3. **Idle spend.** The Extract A100 was left up ≈ 48 min after the eval finished. Shut down as soon as results are off the box. `shutdown -h` on the guest may not stop billing; the Cloud API delete is what ends the charge.
4. **Name prefixes.** Extract resources are named `tasan-extract*`; Twin uses `tasan-sim-*` / `tasan-full`. Do not delete a resource you did not create.

---

## 6. Judging criteria

### 6.1 Ambition (25%) — how much did compute let you do that you otherwise couldn't?

A regex can score 0.96 F1 on tidy template notes and **0.00** on held-out messy Finnish phrasing (spelled months, ISO weeks, planned-versus-done traps). The thing a laptop cannot honestly claim is a **32B open-weight model, served in a Finnish data centre, measured on 1,200 synthetic notes**, with exact-date F1 **0.74** and day-28 alert accuracy **0.96** on that hard set, plus a unit cost. The Twin then runs the same 22-county, 2.64-million-county-year fan-out on Verda and matches the local bits. Ask Tasan is the smaller third leg — an EU-hosted open-weight analyst with a key that never ships to the browser — but it is wired, not a mock.

What we are **not** claiming: a completed LoRA or 8B comparison, a 1/8/32/64 concurrency sweep, or a standing live GPU. LoRA was started on a spot A100 and crashed before the first training step; the sweep was never launched. The ambition is the sovereign extractor and the measured clock (exact F1 **0.74** / alert accuracy **0.96** on v2, **$0.89–$0.99** per 1,000 notes, **0.67–0.75** notes/s at concurrency 16).

### 6.2 Fit (25%) — did you pick the right Verda services and use them well?

| Need | Product chosen | Why that one |
|---|---|---|
| 32B weights + notes stay in Finland | GPU instance in FIN-01 (A100 80 GB) | Inference is Germany; only instance locations are Finnish; 80 GB fits 32B AWQ comfortably |
| 132 CPU simulation jobs | V100 *spot* as a CPU box, after checking that every CPU type was out | Cheapest in-stock machine; GPU unused on purpose |
| Scale path for the Twin | Serverless Containers + Container Registry (attempted) | Right product for embarrassingly parallel CPU work; blocked by box egress, not by a wrong SKU |
| In-app analyst | Inference API + key-holding proxy | The product Verda lists for serving open-weight models in an application; CPU instance for the proxy was out, so the same proxy file ran as a Worker |
| Not used | Instant Clusters, H100, 8-GPU CC, GPU serverless for the Twin | Wrong size, price, or no speed-up |

We also used the Cloud API as intended: availability checks before create, estimates written before launch, Pay-as-you-go 10-minute billing with unused increment refunded, and API deletion (not only `shutdown -h`). We used it imperfectly in the ways §5 records.

### 6.3 Working prototype (25%) — does it run, and is the process documented?

- **Extract:** eval artefacts in `verda/extract/eval/results/` (predictions, metrics, reports, charts). The Tasan Live app can show 10 synthetic notes offline from `app_export.json` (`source: qwen3-32b`). A local `POST /extract` demo server runs with no GPU (`verda/extract/demo/server.py`; see `verda/extract/README.md`). The GPU itself is deleted.
- **Twin:** `sim/results_verda/` holds the full run; `python3 -m twin.validate` passed; smoke and full outputs matched local.
- **Ask Tasan:** live path in the deployed app, Worker proxy, 18-prompt suite recorded. Fallback is the local fact pack, including in the offline build.
- **Process:** this file, `data/SPEND.md`, `sim/README.md`, `verda/extract/RESULTS.md`, `app/server/SPEND.md`. Discord summary is a **draft only** (`verda/DISCORD_DRAFT.md`) and has not been posted.

### 6.4 Path to scale (25%) — is there a credible way from demo to real users?

See §7.

---

## 7. Path to scale

All figures in this section that are measurements come from the A100 concurrency-16 run. Volume and notes-per-patient are labelled assumptions.

**Patients / year.** **2,994** new lung and tracheal cancers per year in Finland, the 2020–2024 average from the Finnish Cancer Registry (1,780 men + 1,214 women). Source cited in `verda/extract/RESULTS.md`: the Registry lung/trachea fact sheet and *Cancer in Finland 2024*. Preliminary 2024 count is similar (1,717 + 1,175 = 2,892).

**Notes / patient.** **5** pathway documents, equal to the mean length of our SYNTHETIC corpora (600 docs / 120 patients). This is an **assumption for costing**, not a published clinical figure.

**Volume.** 2,994 × 5 = **14,970 notes / year** nationwide (about 15k).

**Unit cost, measured.** $0.89 / 1,000 notes on v1-like text and **$0.99 / 1,000** on v2-like text, at the A100 on-demand list price of $2.386/h and concurrency 16.

**Implied nationwide / year (extraction GPU only):**

| Serving assumption | Unit cost | Nationwide / year |
|---|---:|---:|
| 32B on A100, conc 16, v2-like notes | $0.99 / 1k | **≈ $15** |
| Same, v1-like notes | $0.89 / 1k | **≈ $13** |

These are GPU list-price sketches for extraction only: no engineer time, no high availability, no idle, no labelling, no integration. They use the **measured** concurrency-16 32B unit costs. An 8B or LoRA figure would replace the 32B row if that work had completed; LoRA and the concurrency sweep are **not completed**, and no such figure is estimated here.

**Per-county deployment, data stays in Finland.** Every Verda GPU location in the API is in Finland (FIN-01 / FIN-02 / FIN-03). A wellbeing services county can pin the same vLLM image to a Finnish site so notes and weights never leave the country. For real (non-synthetic) patient data, the honest next step is a confidential-computing SKU in FIN-03 — those types exist, and we did **not** use them this weekend because they would have exhausted the demo cap in minutes. Inference in Germany is the wrong place for the notes; it remains acceptable for Ask Tasan’s already-public fact pack.

**Labelling.** Gold for the demo is synthetic and generated with the text. A real deployment needs a county-owned annotation set (pathway events + evidence spans) before any production F1 number is claimed. The v2 regex collapse is the argument for investing in that set: keyword rules will not survive real dictated Finnish notes.

**Twin and Ask, at scale.** The Twin’s natural scale path is the serverless CPU tier we almost used (137 jobs, estimated about $1 a pass once `tasks.verda.com` is reachable). Ask Tasan stays on the Inference API, still EU-hosted, with the key on a server the county controls — ideally a Verda CPU in Finland when that type is in stock.

---

## 8. How to reproduce (no new Verda spend required)

Do **not** run the launch scripts with `--execute`. The user stopped all measuring at 23:12. Scope is frozen: no new instances, no LoRA retry, no sweep, no paid Inference calls from this document. Credentials (`VERDA_CLIENT_ID` / `VERDA_CLIENT_SECRET` / `VERDA_API_KEY`) stay in the environment and must never be printed or copied into the repo.

### 8.1 Extract, local ($0)

From `verda/extract/`:

```bash
python3 corpus/generate.py --seed 20261114 --out corpus/data
python3 corpus/generate_v2.py --seed 20261142 --out corpus/data_v2
python3 eval/regex_baseline.py --corpus corpus/data --out eval/results/regex_predictions.json
python3 eval/evaluate.py --corpus corpus/data --pred eval/results/regex_predictions.json --out eval/results/regex_report
python3 eval/regex_baseline.py --corpus corpus/data_v2 --out eval/results/regex_predictions_v2.json
python3 eval/evaluate.py --corpus corpus/data_v2 --pred eval/results/regex_predictions_v2.json --out eval/results/regex_report_v2
python3 build_showcase.py
python3 demo/server.py --port 8088
# curl -s http://127.0.0.1:8088/health
# curl -s -X POST http://127.0.0.1:8088/extract -H 'Content-Type: application/json' -d '{"note_id":"SYN-P0002-referral_letter-01","text":"..."}'
```

Published 32B scores are already in `eval/results/qwen3_32b_v1_report.json` and `qwen3_32b_v2_report.json`. Re-scoring without a GPU:

```bash
python3 eval/evaluate.py --corpus corpus/data --pred eval/results/qwen3_32b_v1_predictions.json --out /tmp/qwen_v1
python3 eval/evaluate.py --corpus corpus/data_v2 --pred eval/results/qwen3_32b_v2_predictions.json --out /tmp/qwen_v2
```

The historical GPU launch (do not re-run) was `serve/launch_extract_instance.py --execute` with `TASAN_VERDA_BUDGET_APPROVED=yes`. Dry-run without that flag creates nothing.

### 8.2 Pathway Twin, local ($0)

From `sim/`:

```bash
N_RUNS=2000 ./run_all.sh
python3 -m twin.validate
python3 -m twin.cli list
```

Verda results to inspect: `sim/results_verda/`, `sim/results_verda_smoke/`, `sim/results_verda_serverless/`. Historical launchers (need env credentials, never printed): `python3 deploy/verda/smoke_instance.py`, `python3 deploy/verda/run_instance.py`. Do not start them for this document.

### 8.3 Ask Tasan

The live app is at https://petaled-trowel-90.beacon.host/. Force the local pack with `?ask=offline`. The proxy source is `app/server/proxy.mjs`. The recorded suite is `app/server/TRICK_SUITE.md` / `trick_suite.ts`. Do not fire a new live suite from this document (it would be a paid Inference call).

---

## 9. Total Verda spend

Component rows are copied from the spend logs. The team total is the **sum of those sourced rows**, not a number found in a single file. Project-balance snapshots in `data/SPEND.md` ($221.04, $219.51, $218.02) include other agents’ resources and are **not** used as a spend total.

| Component | Preferred actual (life, unused 10-min increment refunded) | Increment-grossed alternative | Source |
|---|---:|---:|---|
| Twin smoke | ≈ $0.01 (at most $0.02) | — | `data/SPEND.md` §2 |
| Twin run (A) | ≈ $0.07–0.08 | $0.081 | `data/SPEND.md` (section “4. Run (A), actual” — later in the file than the Extract-planning §4) |
| Twin run (B) serverless | ≈ $0.02 + registry < $0.01 | — | `data/SPEND.md` §7 |
| **Twin subtotal** | **≈ $0.11** | — | `data/SPEND.md` §7, `sim/README.md` |
| Extract RTX aborts | $0.17 | $0.96 | `data/SPEND.md` §8.1 |
| Extract eval A100 (incl. ≈ 48 min idle) | $3.60 | $3.66 | `data/SPEND.md` §8.2 |
| Extract §8 subtotal (eval run) | ≈ $3.77 | ≈ $4.62 | `data/SPEND.md` §8.3 |
| Extract phase 2 first abort (on-demand A100, 7.58 min) | $0.31 | $0.40 | `data/SPEND.md` §10 |
| Extract phase 2 LoRA retry (spot A100, 7.47 min) | $0.16 | $0.21 | `data/SPEND.md` §12 |
| **Extract final subtotal** | **≈ $4.24** | **≈ $5.23** | `data/SPEND.md` §14 |
| Ask Tasan Cloud VM | $0.00 | — | `app/server/SPEND.md` |
| Ask Tasan Inference API | ≈ $2–$3 | — | `app/server/SPEND.md` |
| **Ask Tasan subtotal** | **≈ $2–$3** | — | `app/server/SPEND.md` |
| **Team total (sum of the above)** | **≈ $6.35–$7.35** | **≈ $7.34–$8.34** using Extract $5.23 | Sum of sourced subtotals ($0.11 + $4.24 + $2–$3; or $0.11 + $5.23 + $2–$3) |

Team target was about $50, hard cap $100. Extract’s later $50 cap was not exhausted. Measuring stopped at 23:12; the §13 sweep estimate was **not incurred**. **Verified via API at 23:13 EET: 0 instances, 0 volumes** (`data/SPEND.md` §14). The Twin registry image and pull credential may still exist (left for a retry as of 21:43 EET). Ask Tasan continues to accrue Inference tokens only when someone uses the live analyst; there is no GPU left billing for it.
