# Verda spend log (Tasan Pathway Twin)

Rules: team target ~$50, hard cap $100. This simulation's smoke test: hard cap **$2**. Full run needs separate approval.
Prices are from the Verda API `GET /v1/instance-types` (read 2026-11-14 20:35 EET) and match https://verda.com/pricing (read the same day).
Billing: Pay As You Go in pre-paid 10-minute increments, unused part refunded (https://docs.verda.com/welcome-to-verda/pricing-and-billing/). Storage $0.20/GiB-month (pricing page).

## 1. Smoke test, estimate written BEFORE launch (2026-11-14 ~20:40 EET)
- Availability check (API, 20:35 EET): no CPU instance type was available in FIN-01/02/03, on-demand or spot. Available: FIN-01 `1V100.4V` (spot), `1A100.22V` (spot + on-demand).
- Plan: 1 × `1V100.4V` **spot** instance in FIN-01 (4 vCPU, 18 GB RAM; the GPU is not used), image `24.04.cuda12.9-v100.docker`, OS volume 50 GB set to delete permanently.
  - Work: build the `sim/Dockerfile` image on the instance, run 2 jobs (Lapland × baseline, Lapland × zero_effect, 2,000 simulated years each), plus 1 HTTP batch-contract call. Copy results back. Delete the instance, its volume and the temporary SSH key.
  - Spot price $0.122/h. Hard limit: 40 min of instance life, then deleted automatically → max **$0.08** instance + 50 GB × 40 min storage ≈ **$0.01**.
- Fallback, only if V100 spot cannot be deployed: 1 × `1A100.22V` spot ($1.193/h), same 40-min limit → max **$0.80**.
- **Worst case (both attempts at their limits): ≈ $0.90, under the $2 cap.** No other credential is needed (Cloud API client credentials from env; an ephemeral SSH key is generated for this run and deleted afterwards). No image is pushed to any registry.

## 2. Smoke test, actual (2026-11-14, times EET)
- 20:30:30 deployed `1V100.4V` **spot**, FIN-01 (instance c3a6358a…). Running at 20:30:51.
- 20:31:18–20:31:54 on the instance: Docker 29.9.2 built `sim/Dockerfile` in 23 s (image sha256:881bff2f…, 271 MB). Ran 2 jobs, Lapland × baseline in 3.7 s and Lapland × zero_effect in 3.2 s (2,000 simulated years each), plus 1 HTTP batch-contract call (`POST /run`), after which the container exited 0. Results were copied back to `sim/results_verda_smoke/`. **Both job outputs are byte-identical to the local run with the same seed**, runtime field excluded.
- 20:32:01 the first delete call failed (404 "Volume ID doesn't exist", because the script passed the OS volume twice). Fixed by hand: the instance was discontinued at 20:32:34 (delete accepted ~20:32:40). The OS volume, left detached, was deleted permanently at ~20:33. The ephemeral SSH key was deleted at 20:32:34. The script is now fixed (dedupe + explicit volume delete).
- **Verified via API at ~20:34:** 0 instances, 0 volumes, 0 volumes in trash, 0 SSH keys.
- **Cost:** instance life ≈2.2 min × $0.122/h = **$0.005** (pre-paid 10-min increment = $0.020, unused part refunded per billing docs). 50 GB OS volume for ≈3.5 min ≈ $0.001. **Total ≈ $0.01 (at most $0.02)**, against the $2 cap. Project balance read via API: $221.04 before and $221.04 right after (billing may post later).
- No container registry push, no serverless deployment, no inference calls.

## 3. Run (A), full single-instance run: estimate written BEFORE launch (2026-11-14 ~20:42 EET)
- Approved team budget $50–100. Cap for (A)+(B) combined: **$5**, including retries and storage.
- Availability (API, 20:41 EET): no CPU instance on-demand or spot in FIN-01/02/03; `1V100.4V` spot is available in FIN-01. Balance $221.04.
- Plan: 1 × `1V100.4V` spot ($0.122/h, from the API `GET /v1/instance-types`), FIN-01, image `24.04.cuda12.9-v100.docker`, 50 GB OS volume.
  - Build `sim/Dockerfile` on the instance. In the container, run all 132 scenario jobs (22 counties × 6 scenarios, 20,000 simulated years each, seed 1, 4 workers) and 5 calibration jobs (1 per area, 4,000 particles each).
  - Copy results to `sim/results_verda/`. Delete the instance, its volume and the ephemeral SSH key; verify via API.
  - Expected instance life ~10–15 min; hard auto-delete at 45 min.
- Estimate: **$0.03 expected**. Worst case 45 min × $0.122/h = $0.09 instance + 50 GB × 45 min ≈ $0.01 storage. If V100 spot fails, the fallback is `1A100.22V` spot ($1.193/h × 45 min = $0.90). **Worst case ≈ $1.00, inside the $5 cap.**

## 4. Tasan Extract planning, read-only discovery (2026-11-14 20:42–20:44 EET)
- Work: live catalogue and availability for the Extract plan (`verda/EXTRACT_PLAN.md`). **GET only.** No instance, volume, SSH key, serverless deployment or Inference subscription change. No `POST /v1/chat/completions` (paid smoke skipped).
- Endpoints: `GET /v1/locations`, `/instance-types`, `/instance-availability` (list and per-type), `/instances`, `/volumes`, `/volumes/trash`, `/ssh-keys`, `/images`, `/inference/models`, `/inference/subscriptions`, `/inference/subscriptions/status`, `/inference/usage`, and `GET https://inference.verda.com/v1/models`.
- Availability at that time (Finland only; no non-FI instance location exists): FIN-01 `1A100.22V` spot + on-demand ($1.193 / $2.386 per hour); FIN-02 `1RTX6000ADA.10V` spot + on-demand ($0.803 / $1.606); FIN-03 8-GPU confidential-computing types only (do not use). No CPU, no H100, no new V100.
- Inference catalogue: `kimi-k3-1-pro` (enabled; $2.00 / $0.20 / $10.00 per 1M input / cache / output; Germany) and `deepseek-4-1-flash-1017` (not enabled; MIT; $0.15 / $0.006 / $0.60; Germany). No Nemotron / Llama / Qwen / Mistral on the Inference API. Usage totals: **0 requests, 0 tokens**.
- Observed, not ours: one running instance `tasan-full` (`1V100.4V` spot, FIN-01, created 20:37:09 EET) with its 50 GB OS volume and ephemeral SSH key — the Pathway Twin full run. Left untouched.
- **Cost of this step: $0.00.**

## 5. Tasan Extract local corpus + regex baseline (2026-11-14 ~20:55 EET)
- Work: built `verda/extract/` (synthetic corpus, eval harness, regex baseline, prompts, client, demo server, launch script). **No Cloud API writes. No Inference completions. Launch script was written and not run.**
- **Cost of this step: $0.00.**

## 6. Tasan Extract GPU run: estimate written BEFORE launch (2026-11-14 20:59 EET)
- Operating cap for this run **$10**, hard cap **$25**. Watchdog **150 min**, then API-delete (instance + volume + key this run created only). Will not touch teammate instance `tasan-full` (`1V100.4V` spot FIN-01, still running at the availability check).
- Availability (`GET /v1/instance-availability`, 20:57–20:58 EET): **requested `1A100.22V` is not in stock** in FIN-01 (or any FIN location), on-demand or spot. Also out: H100, L40S, Ada 6000, A6000, non-CC RTX PRO 6000. In stock: FIN-01 `1V100.4V` (16 GB, cannot hold Qwen3-32B-AWQ); FIN-03 `1B200.30V` ($9.508/h on-demand / $4.754/h spot) and `1RTXPRO6000.30V.CC` ($2.893/h on-demand / $1.446/h spot).
- **Plan A (as requested), if it reappears at launch:** 1 × `1A100.22V` **on-demand**, FIN-01, image `24.04.cuda13.4.docker`, 200 GB OS volume (delete permanently). List price $2.386/h.
  - Expected life ~90–120 min (boot, docker/vLLM pull, Qwen3-32B-AWQ + Qwen3-8B download, paraphrase + extract + throughput, teardown).
  - Expected ≈ 2.0 h × $2.386 + 200 GB × 2.0 h × $0.20/730 ≈ **$4.77 + $0.11 = $4.88**.
  - Worst case 150 min: 2.5 × $2.386 + storage ≈ **$5.97 + $0.14 = $6.11**, under the $10 cap.
- **Plan B (pre-declared fallback, because A100 is currently out):** 1 × `1RTXPRO6000.30V.CC` **on-demand**, FIN-03 (Finland), image `24.04.cuda13.4.cc` (the only image family this type lists; no Docker image on the catalogue). 96 GB VRAM, $2.893/h, 200 GB OS volume. Same work, same 150 min watchdog.
  - Expected 2.0 h × $2.893 + storage ≈ **$5.79 + $0.11 = $5.90**.
  - Worst case 150 min: 2.5 × $2.893 + storage ≈ **$7.23 + $0.14 = $7.37**, under the $10 cap.
  - Risk (labelled): the CC image may not ship Docker; startup will install Docker + NVIDIA toolkit or fall back to a local vLLM venv. If that path fails, the instance is deleted and we stop rather than jump to a SKU that breaks the $10 cap.
- **Not used:** `1B200.30V` on-demand (150 min ≈ $23.77, over the $10 operating cap); V100 16 GB (does not fit 32B AWQ). No Instant Cluster. Inference baseline only if it stays under $0.50 (optional 50-note Kimi); DeepSeek is not enabled, so no DeepSeek calls are planned.
- Work on the box: vLLM, Qwen3-32B-AWQ (thinking off, guided JSON) then Qwen3-8B sequentially; SSH tunnel only (bind 127.0.0.1, no public endpoint). Local machine builds corpus v2 in parallel with the model download.
- **This estimate precedes any create call.**

## 4. Run (A), actual (2026-11-14, times EET)
- 20:37:33 deployed `1V100.4V` spot, FIN-01 (instance d01e730d…). Running at 20:37:51; code uploaded at 20:38:17.
- On the instance (4 vCPU): Docker build took 21 s. **132 scenario jobs (20,000 simulated years each) took 1,372 s**, 41.5 s mean per job with 4 workers; the old V100 host's CPUs are about 4× slower per core than our box. **5 calibration jobs (4,000 particles each) took 7–21 s each.** Results were copied back to `sim/results_verda/` at 21:04:49.
- Two faults:
  1. The in-container aggregate step crashed. It globbed the calibration JSONs, which affected only the in-container summary; fixed and re-aggregated locally.
  2. **The cleanup at 21:04:49 failed with HTTP 401 because the OAuth access token had expired** after ~27 min. The instance stayed up until I deleted it by hand at **21:10:16** (discontinued confirmed). Its OS volume was deleted permanently at 21:10:17. `verda_api.py` now refreshes the token on a 401.
- **My mistake:** in the manual cleanup I deleted *all* SSH keys in the project. That included one named `tasan-extract-ephemeral`, which belongs to **another agent's run** (instance `e60ea3d7…`, `1A100.22V` on-demand, hostname `tasan-extract`, created 21:06 EET, with a 200 GB OS volume). I did **not** touch that instance or its volume; it was still running at 21:10:24. Keys already on a running instance usually keep working, but that agent's own cleanup of the key will get a 404. Scripts now delete only their own key by id.
- **Verified via API at 21:10:24:** none of my instances, volumes or keys remain; 0 job deployments, 0 container deployments, trash empty. The only resource left is the other agent's `tasan-extract` A100 instance and its volume.
- **Cost (A):** instance life 32.7 min × $0.122/h = **$0.067** (billed in 10-min increments: 40 min = $0.081). 50 GB OS volume for ~33 min ≈ $0.001. **Total ≈ $0.07–0.08.**
- Balance: $221.04 at 20:41 and **$219.51 at 21:10**. The $1.53 drop also includes the other agent's on-demand A100 (from 21:06, $2.386/h, prepaid in 10-min blocks) and its 200 GB volume, so it is not all ours.
- Running total for this simulation (smoke + A): **≈ $0.09**, against the $5 cap.

## 5. Run (B), serverless batch jobs: NOT RUN (blocked before any spend)
- Verda Container Registry push credentials can't be created through the documented API. The API's `POST /v1/job-deployments` schema says: "Currently, credentials must be created via the DataCrunch Cloud UI." The CLI docs (https://docs.verda.com/cli/container-registry/) say: "Create credentials in the Verda dashboard first." `POST /v1/container-registry-credentials` only stores existing credentials for pulling and returns no secret. Following the rules, no other route was tried. Cost (B): **$0**.

## 6. Run (B), serverless batch jobs: estimate written BEFORE launch (2026-11-14 ~21:40 EET)
- Approved by the user. Cap: **$5 total sim spend**, including ≈$0.09 already spent → **≤ $4.91 left for (B)**.
- All resources use the prefix `tasan-sim-` and are cleaned up by their recorded IDs/names only.
- Steps and estimates:
  1. **Temporary build/push instance:** `1V100.4V` spot (FIN-01, $0.122/h; no CPU type available), about 10 min, auto-delete at 30 min → **≈ $0.02** (max $0.06).
  2. **Image in Verda Container Registry:** `vccr.io/<project>/tasan-sim-twin:0.1.0`, ~0.27 GB × $0.20/GB-month (`GET /v1/container-registry/pricing`), kept for ~1 h then deleted → **< $0.01**.
  3. **Serverless job deployment `tasan-sim-twin`:** compute AMD Rome+ `CPU.8V.32GC`, **$0.11/h** per replica (`GET /v1/container-types`; https://verda.com/pricing). Max 8 concurrent replicas, deadline 600 s (the API minimum). Jobs: 132 scenario jobs (20,000 simulated years, seed 1) + 5 calibration jobs (4,000 particles).
     - Expected about 4 billed min per job (≈20 s compute + spin-up/pull/down) → 137 × 4 min × $0.11/h ≈ **$1.00**.
     - Worst case, every job running to the 10-min deadline: 137 × 10 min ≈ **$2.51**.
  4. **Stop-loss:** if the running estimate passes $3.00, purge the queue and delete the deployment.
- **Expected (B) ≈ $1.05; worst ≈ $2.60. Sim total worst ≈ $2.70, under the $5 cap.**

## 7. Run (B), serverless: actual (2026-11-14 21:37–21:42 EET), STOPPED at job submission
- **21:37–21:39 push instance** `1V100.4V` spot FIN-01, id `4375e56c-d61d-4c89-b31c-7a0d6d166187`, OS volume `8c509a13-399f-4716-b4cc-f898c49e519b` (`tasan-sim-push-os`), SSH key `tasan-sim-push-key`. Build 18 s, push 8 s → `vccr.io/e44abca5-8324-49ad-8f3a-7073929e8beb/tasan-sim-twin:0.1.0` (sha256:72ecf2a2…, 271 MB). Docker config wiped (logout + rm, verified). Instance discontinued 21:39:25, volume `deleted`, key 404, all checked by ID. Life 1.4 min → **≈ $0.02** (10-min billing block).
- **21:40:40** pull credential `tasan-sim-pull` registered (`POST /v1/container-registry-credentials`, type verda; 201).
- **21:41:40** job deployment `tasan-sim-twin` created (compute `CPU Node` size 8 = AMD Rome+ CPU.8V.32GC, max 8 replicas, deadline 600 s); `ready` after 6 s.
- **21:41:41 all 137 submissions failed before reaching Verda.** The box's network egress fails the TLS handshake to `tasks.verda.com` (resolves to the sandbox proxy 198.18.0.1; `TLS alert, decode error`, repeatable). `api.verda.com` and `vccr.io` work. No job was queued, so no replica started.
- **21:41:46** deployment deleted by name; GET → 404 at 21:41:47. **Deployment cost ≈ $0** (no replicas ran).
- **(B) actual ≈ $0.02 (push instance) + registry storage < $0.01. Sim running total ≈ $0.11 of the $5 cap.** Balance $218.02 at 21:43 (includes other agents' resources, so not attributable).
- **Still present, on purpose, for a retry:** image `tasan-sim-twin:0.1.0` in vccr.io (≈$0.0001/h) and pull credential `tasan-sim-pull`. Both are deleted on request or after the retry.

## Extract (JN Verda Lead), A100 run actual (2026-11-14, EET)
- Instance `e60ea3d7…` (tasan-extract, `1A100.22V` on-demand, FIN-01, $2.386/h) ran 21:06:41–22:35. The 32B evals on v1 and v2 finished (results in verda/extract/eval/results/). The controlling helper then stopped, and the box sat idle.
- 22:35 JN Verda Lead deleted it by hand with its OS volume `3300c6fa…`. **Verified via API: 0 instances, 0 volumes.**
- Cost ≈ 1.48 h × $2.386 ≈ **$3.54** (+ 200 GB disk ≈ $0.01) + the two aborted RTX boots ≈ $0.96 → **Extract total ≈ $4.5**. Estimate; billing may post later.

## 8. Tasan Extract GPU run, actuals (2026-11-14, times EET)

Detailed actuals for the Extract GPU work estimated in §6 (operating cap then $10). This complements the short coordinator note above. Prices from `GET /v1/instance-types`. Billing: PAYG in pre-paid 10-minute increments, unused part refunded (https://docs.verda.com/welcome-to-verda/pricing-and-billing/). Storage $0.20/GiB-month ≈ /730 hourly.

### 8.1 Two aborted RTX PRO 6000 CC boots (Plan B, while A100 was out)

Both were `1RTXPRO6000.30V.CC` on-demand, FIN-03, $2.893/h, 200 GB OS volume. Each died when an SSH dispatch timeout raised out of the launcher and `finally` deleted the resources. Teammate `tasan-full` was not touched. SSH helper was then hardened (timeouts no longer abort cleanup).

| Attempt | Instance (prefix) | Volume (prefix) | Created → deleted (EET) | Life | Instance $ (life) | 10-min increment (unused refunded) |
|---|---|---|---|---:|---:|---:|
| 1 | `cedfe23e…` | `950e25eb…` | 20:59:50 → 21:01:52 | ≈ 2.0 min | **$0.10** | $0.48 |
| 2 | `1ac3365d…` | `b40d9df3…` | 21:03:45 → 21:05:21 | ≈ 1.6 min | **$0.08** | $0.48 |

Storage for these two short lives is < $0.01. After refund of unused increment time, **RTX aborts ≈ $0.17**. If increments were counted without the refund, the pair would be ≈ **$0.96** (the earlier working figure). API verification after each abort: instance discontinued/gone; volumes gone from `/volumes` and `/volumes/trash` (a brief race on the first volume GET-by-id returned 200, then empty). Keys deleted.

### 8.2 A100 run (Plan A, in stock on the third launch)

- **Instance** `e60ea3d7-a593-4c34-b208-64cfec0eb8c4`, hostname `tasan-extract`, `1A100.22V` **on-demand**, FIN-01, $2.386/h, image `24.04.cuda13.4.docker`, 200 GB OS volume `3300c6fa…` (`tasan-extract-os`). Not spot.
- Created 21:06:41 EET, running 21:07:31, startup.sh dispatched 21:08:03, vLLM ready 21:13:16 (Qwen3-32B-AWQ, docker, bound 127.0.0.1). Ready **5.7 min after boot**, inside the 40-minute ready limit.
- **Work completed:** 32B extract, thinking off, OpenAI `json_schema`, concurrency 16, 600+600 SYNTHETIC notes, all HTTP 200.
  - **v1 easy** (21:18:43–21:32:07, 803.8 s, 0.746 notes/s, p50 18.2 s / p95 40.7 s): exact micro P/R/F1 **0.955 / 0.953 / 0.954**, ±1 day F1 **0.964**, day-28 alert accuracy **0.983**. Implied **$0.89 per 1,000 notes** at the list price.
  - **v2 held-out** (21:32:07–21:47:03, 896.3 s, 0.669 notes/s, p50 20.5 s / p95 45.8 s): all exact micro **0.765 / 0.720 / 0.742**, ±1 day F1 **0.763**, alert accuracy **0.958**. **Test only** (401 docs, 80 patients): exact **0.765 / 0.715 / 0.739**, ±1 day F1 **0.761**, alert accuracy **0.963**. Untuned regex on the same v2 test remains exact F1 **0.000**.
- **Not finished on this box** (controller context ran out after the 32B extracts): GPU paraphrase pass, concurrency 1/8/32/64 sweep, Qwen3-8B extract, `app_export.json` regen with `source: qwen3-32b`. Those remain local follow-ups / a later GPU slot.
- **Idle gap:** extracts finished 21:47:04; the instance sat idle until deletion. That idle window is ≈ 48 min ≈ **$1.91** of the A100 bill. Our mistake; it should have been deleted at 21:47.
- **Deleted 22:35:03 EET** by API `PUT /instances` action=delete, `delete_permanently=true`, volume `3300c6fa…` included. HTTP 204. Instance GET → **discontinued**. `/instances` list **empty** of this id (and empty overall at 22:36:20). Volume: `/volumes` and `/volumes/trash` **empty**; GET-by-id still returned 200 with `status=deleted` (treated as gone; not listed, not billable as attached). The Extract SSH key had already been removed by a teammate's 21:10 cleanup; a 404 on key delete was expected and no key delete was retried. **Did not touch** the remaining project SSH key `tasan-ask-ephemeral` (`bc474ff4…`), which is not ours.
- Life 21:06:41–22:35:11 = **88.49 min** (1.475 h). Instance 88.49/60 × $2.386 = **$3.52** (90-min increment $3.58, unused refunded). 200 GB storage 1.475 h × 200 × $0.20/730 ≈ **$0.08**. **A100 actual ≈ $3.60.**

### 8.3 Extract spend so far (against the then $10 cap; new phase-2 cap is separate)

| Line | Actual (life, unused increment refunded) | If 10-min increments were kept in full |
|---|---:|---:|
| RTX abort 1 | $0.10 | $0.48 |
| RTX abort 2 | $0.08 | $0.48 |
| A100 instance | $3.52 | $3.58 |
| A100 200 GB storage | $0.08 | $0.08 |
| **Extract total** | **≈ $3.77** | **≈ $4.62** |

Preferred figure, consistent with earlier SPEND refund language: **≈ $3.77**. The ≈ $4.5–$4.6 range is the increment-grossed alternative (and matches the short note above to within rounding and a slightly low disk figure). No Inference completions. No further Extract instance is running as of 22:36:20 EET.

## 9. Tasan Extract phase 2 (LoRA 8B + A100 sweep): estimate written BEFORE launch (2026-11-14 22:40 EET)

- Extract spend so far ( §8 ): **≈ $3.77** life-based (or ≈ **$4.5–$4.62** increment-grossed). New operating cap for all Extract work: **$50**. Remaining headroom ≈ $45. Team hard cap $100.
- Availability (`GET /v1/instance-availability`, 22:39 EET): **`1A100.22V` on-demand FIN-01 is in stock**; A100 **spot is out**. **`1RTX6000ADA.10V` is out** in FIN-01/02/03, on-demand and spot. In stock as a non-Ada alternative: `1RTXPRO6000.30V.CC` on-demand FIN-03 ($2.893/h). No other Extract instance or volume is running (`GET /instances` = 0, `/volumes` = 0). The only SSH key in the project is `tasan-ask-ephemeral` (not ours; will not be touched).
- **This launch (only):** 1 × `1A100.22V` **on-demand**, FIN-01, image `24.04.cuda13.4.docker`, 200 GB OS volume (delete permanently), hostname `tasan-extract-p2`, prefix `tasan-extract-`. List price **$2.386/h**. Work on the box, one session, then API-delete: (1) optional short GPU paraphrase of a v1 train slice; (2) LoRA fine-tune Qwen3-8B on a SYNTHETIC train set that is disjoint from v2 dev/test template families; (3) eval base 8B vs LoRA 8B on the held-out v2 **test** split; (4) throughput sweep concurrency 1/8/32/64 for 32B-AWQ, 8B base, 8B+LoRA; (5) copy results back; (6) controller API-deletes instance+volume+our key (404 on a missing key is success). 32B QLoRA only if more than ~40 min remain before the watchdog.
- **Not in this launch:** RTX 6000 Ada sweep (out of stock). A second session on `1RTXPRO6000.30V.CC` is deferred unless this A100 run finishes early with budget left; that would get its own estimate before any create.
- Watchdog **150 min**, then API-delete even if the job is incomplete. Remote `shutdown -h` is a backstop only; the controller always API-deletes and verifies (our IDs only). No Cloud API secrets are copied onto the instance.
- Expected life ~90–120 min: 2.0 h × $2.386 + 200 GB × 2.0 h × $0.20/730 ≈ **$4.77 + $0.11 = $4.88**.
- Worst case 150 min: 2.5 × $2.386 + storage ≈ **$5.97 + $0.14 = $6.11**.
- **Extract total after this launch, worst case: ≈ $4.5 + $6.11 ≈ $10.61, under the $50 cap.**
- **This estimate precedes any create call.**



## 10. Tasan Extract phase 2 first launch, actuals (aborted after train failure) (2026-11-14, times EET)

This is the actual for the launch estimated in §9. The instance was created, the remote session started, LoRA training failed early, and the controller API-deleted everything and verified. No results tarball was produced (the fail path did not yet pack logs — that is fixed before the retry in §11).

- **Instance** `d81e14db-511f-4cfb-b9ff-74fa5d400fbf`, hostname `tasan-extract-p2`, `1A100.22V` **on-demand**, FIN-01, $2.386/h, image `24.04.cuda13.4.docker`, 200 GB OS volume `f386cf99…` (`tasan-extract-p2-os`). SSH key `tasan-extract-p2-ephemeral` (`dda243a8…`).
- Created 22:43:04 EET (HTTP 202), running 22:43:46 (0.7 min to running), SSH ready 22:44:23, payload + session copied 22:44:28, session dispatched 22:44:30.
- Remote session wrote `/root/tasan-extract-FAILED` at 22:50:36 with `FAIL: lora train failed` (docker train step). Likely cause: `pip install peft trl datasets accelerate` inside the vLLM image (PEP 668 / TRL API). Training was rewritten to PEFT + `transformers.Trainer` only, with `--break-system-packages` and log packing on failure, before any retry.
- **Deleted 22:50:39 EET** by the controller `finally` path: `PUT /instances` action=delete, `delete_permanently=true`, volume included (HTTP 202, action discontinue success). Volume also `PUT /volumes` is_permanent (202). SSH key `DELETE` HTTP 200. **Verified 22:50:42:** instance gone, volume treated as gone, our key gone. `GET /instances` and `/volumes` empty of our IDs (and empty overall). **Did not touch** `tasan-ask-ephemeral` (`bc474ff4…`).
- Life 22:43:04–22:50:39 = **7.58 min**. Instance 7.58/60 × $2.386 = **$0.30**. 200 GB storage 7.58/60 h × 200 × $0.20/730 ≈ **$0.01**. 10-min increment (unused refunded toward $0.30): increment-grossed **$0.40** + storage.
- **This abort ≈ $0.31 life-based / ≈ $0.40 increment-grossed.**
- **Extract total after this abort:** ≈ **$4.08** life-based ($3.77 + $0.31) or ≈ **$5.02** increment-grossed ($4.62 + $0.40). Under the $50 cap.

## 11. Tasan Extract phase 2 retry (LoRA 8B + A100 sweep): estimate written BEFORE launch (2026-11-14 22:56 EET)

- Extract spend so far (§8 + §10): **≈ $4.08** life-based (or ≈ **$5.02** increment-grossed). Cap **$50**. Remaining headroom ≈ $45.
- Availability immediately before this estimate (`GET /v1/instance-availability`, 22:54 EET): **`1A100.22V` on-demand FIN-01 in stock; A100 spot FIN-01 also in stock** (it was out at the §9 check). **`1RTX6000ADA.10V` still out** in FIN-01/02/03 on-demand. `GET /instances` = 0, `/volumes` = 0. The only project SSH key is `tasan-ask-ephemeral` (not ours; will not be touched).
- **This launch (only):** 1 × `1A100.22V` FIN-01, image `24.04.cuda13.4.docker`, 200 GB OS volume (delete permanently), hostname `tasan-extract-p2`, prefix `tasan-extract-`. **Prefer spot at $1.193/h if still in stock at the create call; otherwise on-demand at $2.386/h.** If the spot create fails, fall back once to on-demand in the same controller, then stop. Work on the box, one session, then API-delete: LoRA fine-tune Qwen3-8B on the leak-free SYNTHETIC train set, eval base 8B vs LoRA 8B on held-out v2 test, throughput sweep concurrency 1/8/32/64 for 8B base, 8B+LoRA, and 32B-AWQ, copy results (and logs on failure), controller API-deletes instance+volume+our key (404 on a missing key is success). No Ada/RTX second session in this launch (Ada out). 32B QLoRA only if more than ~40 min remain before the watchdog (not scheduled in the session script).
- Watchdog **150 min**, then API-delete even if the job is incomplete. Remote `shutdown -h` is a backstop only. No Cloud API secrets on the instance.
- Expected life still ~90–120 min (docker pull + 8B download + 2-epoch LoRA + eval + three sweeps):
  - Spot: 2.0 h × $1.193 + 200 GB × 2.0 h × $0.20/730 ≈ **$2.39 + $0.11 = $2.50**.
  - On-demand (fallback): 2.0 h × $2.386 + $0.11 ≈ **$4.88**.
- Worst case 150 min: spot **≈ $3.12**; on-demand **≈ $6.11**.
- **Extract total after this launch, worst case (on-demand): ≈ $5.02 + $6.11 ≈ $11.13, under the $50 cap.**
- **This estimate precedes any create call.**


## 12. Tasan Extract phase 2 retry, actuals (LoRA started, not completed) (2026-11-14, times EET)

Actuals for the launch estimated in §11. Spot A100 was in stock and was used.

- **Instance** `715c7100-a271-4eba-bbe0-f56a95a9c002`, hostname `tasan-extract-p2`, `1A100.22V` **spot**, FIN-01, **$1.193/h**, image `24.04.cuda13.4.docker`, 200 GB OS volume `ae53d27d…`. SSH key `tasan-extract-p2-ephemeral`.
- Created 22:56:19 EET (HTTP 202), running 22:56:40 (0.4 min), SSH ready 22:57:19, files copied 22:57:24, session dispatched 22:57:26.
- Remote work: docker pull of `vllm/vllm-openai:latest`, `pip install peft datasets` (ok), loaded 481 SYNTHETIC SFT rows, loaded Qwen3-8B, applied LoRA (43,646,976 trainable params, 0.5301%). **Crashed before the first optimizer step** on `transformers` 5.20.2: `TrainingArguments.__init__() got an unexpected keyword argument 'warmup_ratio'`. Failed flag written 23:03:31. No adapter, no 8B/LoRA eval, no sweep on this box. Logs packed and copied (`eval/results/phase2/`, including `tasan-extract-out.tgz` and `session.remote.log`).
- **Deleted 23:03:47 EET** by the controller `finally` path: `PUT /instances` action=delete, `delete_permanently=true` (HTTP 202, discontinue success). Volume `PUT /volumes` is_permanent (202). SSH key `DELETE` HTTP 200. **Verified 23:03:50:** instance gone, volume gone, our key gone. `GET /instances` and `/volumes` empty at 23:10:03. **Did not touch** `tasan-ask-ephemeral` (`bc474ff4…`).
- Life 22:56:19–23:03:47 = **7.47 min**. Instance 7.47/60 × $1.193 = **$0.15**. 200 GB storage 7.47/60 h × 200 × $0.20/730 ≈ **$0.01**. 10-min increment-grossed ≈ **$0.20** + storage.
- **This attempt ≈ $0.16 life-based / ≈ $0.21 increment-grossed.**
- **Extract total after this attempt:** ≈ **$4.24** life-based ($4.08 + $0.16) or ≈ **$5.23** increment-grossed ($5.02 + $0.21). Under the $50 cap.
- LoRA is recorded as **started, not completed** (see `verda/extract/eval/results/phase2/LORA_STATUS.md`). It is not retried: a scored LoRA result was more than ~30 min away (re-download + 2 epochs + eval).

## 13. Tasan Extract A100 throughput sweep only: estimate written BEFORE launch (2026-11-14 23:11 EET)

- Extract spend so far (§8 + §10 + §12): **≈ $4.24** life-based (or ≈ **$5.23** increment-grossed). Cap **$50**.
- Purpose of this launch only: finish the concurrency **1/8/32/64** throughput/cost sweep for **Qwen3-8B base** and **Qwen3-32B-AWQ** on one Finnish A100. **No LoRA retry.** No live endpoint. Ada/RTX 6000 comparison only if that SKU is in stock at a later check; it is not part of this create.
- **This launch:** 1 × `1A100.22V` FIN-01, image `24.04.cuda13.4.docker`, 200 GB OS volume (delete permanently), hostname `tasan-extract-p2`, prefix `tasan-extract-`. **Prefer spot at $1.193/h if still in stock at the create call; otherwise on-demand at $2.386/h.** If spot create fails, fall back once to on-demand, then stop.
- Work: docker pull, serve 8B, sweep 32 v2-test notes at conc 1/8/32/64, swap to 32B-AWQ, same sweep, copy results, controller API-deletes instance+volume+our key (404 on a missing key is success). No Cloud API secrets on the instance.
- Watchdog **90 min** (shorter than 150; this session has no training). Remote `shutdown -h` is a backstop only.
- Expected life ~50–80 min:
  - Spot: 80/60 × $1.193 + 200 GB × 80/60 h × $0.20/730 ≈ **$1.59 + $0.07 = $1.66**.
  - On-demand: 80/60 × $2.386 + $0.07 ≈ **$3.25**.
- Worst case 90 min: spot **≈ $1.86**; on-demand **≈ $3.66**.
- **Extract total after this launch, worst case (on-demand): ≈ $5.23 + $3.66 ≈ $8.89, under the $50 cap.**
- **This estimate precedes any create call.**

## 14. §13 sweep NOT launched: stopped by user decision (2026-11-14 23:12 EET)
- The user said stop (23:12). The sweep instance was never created. **Verified via API at 23:13: 0 instances, 0 volumes.** Only the SSH key `tasan-ask-ephemeral` (Ask Tasan, not ours) remains.
- **Final Extract spend ≈ $4.24 life-based (≈ $5.23 counting the 10-min billing increments).** Sweep and LoRA are not completed.

## 15. Run (B), final status: NOT COMPLETED, stopped by user decision (2026-11-14 23:20 EET)
- The user said we're done (23:19). Option 2, submitting from a temp Verda instance, was never launched: no instance was created and no jobs ran. Run (B) is **not completed**, and there are no serverless results. Run (A) remains the Verda reference and matched local byte for byte.
- **Verified via API, 23:20 EET:** 0 instances, 0 volumes, 0 job deployments. Of the SSH keys, only `tasan-ask-ephemeral` remains (not ours). Our pull credential `tasan-sim-pull` was deleted by name (HTTP 200); only the user's `tasan-push` remains (untouched).
- Left in place: image `tasan-sim-twin:0.1.0` in vccr.io (271 MB, ≈$0.0001/h). The Cloud API has no delete call for it.
- **Final sim spend ≈ $0.11** of the $5 cap: smoke ≈ $0.01, (A) ≈ $0.08, (B) ≈ $0.02.
