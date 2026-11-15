# VERDA_PLAN: Tasan on the Verda Compute Track
*Win strategist, Sat 14 Nov 2026, about 20:40 Helsinki time (EET). It sits under PLAN.md DECISION 3. It must not slow the AZ pitch: anything here that is not working by **Sun 08:00** is dropped from the AZ demo. Feature freeze is 11:00.*
*Verda facts below come only from docs.verda.com (pages "last updated" 2.–13.11.2026), verda.com/pricing and verda.com/blog/junction-2026, all read 14 Nov 2026. Prices are list USD on-demand unless marked. Junction credits cover them.*

---

## 0. TL;DR
- **Feature:** the **Tasan Pathway Twin**. It is a GPU Monte Carlo microsimulation of the lung-cancer pathway for all **22 wellbeing services counties**. It is calibrated by likelihood-free fitting (ABC) to the published registry timing curves. It runs as **Verda Serverless Containers batch jobs** (one job per county × scenario × seed block) and writes to **Verda Object Storage (FIN-03, Finland)**. It produces two things:
  1. **An uncertainty interval for the headline people number**, plus a quantified answer to "how many Lapland patients start treatment within 6 weeks of referral?". The answer: *we can't know within X–Y percentage points, because referral→diagnosis time is unpublished. That spread is the case for the Tasan clock.*
  2. **Scenario runs with and without the Tasan day-28 alert and nurse navigator.** The output is "% starting ≤42 days from referral" (the Goal 3 indicator) with intervals. **It never outputs lives saved or curative share.**
- **Plus the grounded analyst on Verda Inference.** It uses the `deepseek-4-1-flash-1017` open-weight model (MIT licence), which runs in Verda's EU datacentre (**Germany**). Prompts are not stored and not used for training. We add a **batch red-team eval**: thousands of adversarial judge-style questions in FI/EN/SV, scored by our citation validator, which gives a published "grounding scorecard".
- **Cost:** about **$60–150 in credits** for the whole build (§3).
- **Honest odds on this track: a podium candidate, not the favourite.** Robotics and RL teams will burn far more GPU. Our case is the **Fit** and **Path to scale** criteria: health data, Finland and EU hosting, a real county pilot.

## 1. Verified Verda products (docs only) and what we use
| Product (exact name in docs) | Verified capability | Use in Tasan |
|---|---|---|
| **Serverless Containers → Batch jobs** | Every request to `https://tasks.verda.com/<DEPLOYMENT_NAME>/...` triggers a job. **Each job gets its own replica**, which is destroyed when the process exits (exit 0 = success). Calls are always async (status and result endpoints). "Max concurrent jobs" and "Deadline" are configurable. Recommended for jobs over 3 min. Scales to 0. Per-minute billing while a replica works | **The Pathway Twin fan-out.** 22 counties × 6 scenarios × N seed blocks, each a job. Right tool: embarrassingly parallel and bursty, with no idle GPUs |
| **Serverless Containers** (continuous) | Queue-based autoscaling, scale-to-zero, any registry, a 500 GiB scratch disk shared across replicas at `/data`, SFS mounts, logs and metrics, a Python SDK. NVIDIA driver R580 | Scale path only: county-hosted, self-served open-weight model (vLLM image, Verda tutorial) |
| **Inference** (preview) | OpenAI-compatible API at `https://inference.verda.com/v1` (`/chat/completions`, `/responses`, `/models`). **No embeddings endpoint (returns 404).** Per-token billing. Prompts and responses are **not stored** (in-memory cache cleared within 2 h), **not used for training**, and **not shared with the model provider**. Each model page lists its country | **Grounded analyst + brief drafter + red-team eval.** No embeddings is fine: the fact pack (about 60 cards) fits in context, so no RAG is needed |
| Inference models (docs, 13.11.2026) | **Kimi K3.1 Pro** (`kimi-k3-1-pro`, Moonshot AI, 1M context, tool calling / JSON mode / reasoning, default reasoning `max`, runs in **Germany**). **DeepSeek V4.1 Flash 1017** (`deepseek-4-1-flash-1017`, **MIT licence**, 1M context, JSON mode / tool calling, default reasoning `none`, runs in **Germany**). The pricing page lists **GLM 5.3 as "coming soon"** | **DeepSeek V4.1 Flash 1017 for live answers** (fast by default, cheap, MIT). Kimi K3.1 Pro with `reasoning_effort: low` optional for the 22 pre-generated briefs |
| **CPU instances** | Dedicated cores, e.g. `CPU.4V.16G` at $0.048/h | **Server proxy** (holds the inference key, runs the validator, serves cached answers) and the job orchestrator / aggregator |
| **GPU instances** | 1× up to 8×. e.g. RTX A6000 48 GB $0.888/h, H100 SXM5 80 GB $5.241/h (spot $2.621/h). Spot instances can be discontinued at any time | One dev box for 2–3 h to profile the JAX kernel before containerising (optional; a laptop CPU also works for dev) |
| **Object Storage** (Beta) | S3-compatible. **Location FIN-03 (Finland)**, endpoint `https://objects.eu-north-3.verda.storage`, region `eu-north-3`, presigned URLs. Beta quota applies | Calibration targets in, simulation results out, red-team logs, published artefacts for the process summary |
| **Container registry** | OCI image storage, $0.20/GiB-month | Hosts the `tasan-sim` image |
| **Instant Clusters** | Multi-node, InfiniBand, Slurm or Kubernetes, up to 144 GPUs self-service | **Not used.** Overkill for an embarrassingly parallel job; saying so earns Fit points |
| Confidential computing | B200 / RTX PRO 6000 / B300 "CC" GPUs and AMD CC CPUs; "data and model staying encrypted in memory, in transit, and at rest" | Scale path for patient-level county data (§6) |
| Locations | **FIN-01, FIN-02, FIN-03: Helsinki, Finland**, renewable energy, PUE 1.2–1.3. GDPR, ISO 27001 datacentres. Certifications in the FAQ: SOC 2 Type II, C5, ISO 27001/27017/27018/27701 | The sovereignty story. **Be precise: the Inference models run in Germany (EU), not Finland.** Object Storage is FIN-03. Container GPU-pool locations are **not documented**, so pick and check the location in the console at deploy time |

**Not verified, do not claim:** the "NVIDIA Nemotron endpoint" mentioned on the challenge page does not appear in the Inference model docs (13.11.2026). Ask at Verda booth 6 before using it. We have no exact credit amount per team. Rate-limit tiers are unknown until the key is live (read the `x-ratelimit-*` headers).

## 2. The feature: Tasan Pathway Twin (what, why, how honest)
**Question it answers.** Goal 3 says "patients start treatment within target times" (strategy p.5). No county publishes this. We can bound it. The registry publishes the diagnosis→first-treatment curves (2024 report, Taulukko 4.1 medians/IQR and Taulukko 4.5 cumulative first events by month, 5 collaborative areas, already in `data/csv/lung_report2024_*.csv`) and county volumes (Taulukko 11). The **referral→diagnosis** leg is unpublished. The Twin propagates every source of uncertainty to give "% ≤42 days from referral" per county, with and without the Tasan alert and navigator.

**Model.**
- **Per-patient stages:** referral arrival → diagnosis (**ASSUMPTION**: an unpublished interval, given a wide prior range and labelled on screen) → treatment-type branch (shares from Taulukko 4.5 per collaborative area) → diagnosis→treatment delay (gamma/lognormal mixture with a point mass at day 0, reproducing the published Q1 = 0).
- **Calibration:** ABC-SMC per collaborative area against the published medians, IQRs and monthly cumulative curves. Accept only parameter sets that reproduce them within the published rounding. A posterior predictive check is shown.
- **County layer:** counties inherit their collaborative area's posterior. **Labelled:** the registry has no county-level timing, so counties differ only in volume and treatment mix. This is a stated limitation and another argument for T3.
- **Tasan scenarios:**
  - (0) baseline
  - (1) day-28 alert + navigator, **zero effect** (always shown, since navigation evidence is mixed: Battaglia 2016 found no effect at 60/180 d)
  - (2–4) low / mid / high delay reduction for alerted patients, with ranges taken only from the sourced studies already in `recs/top3.md`: Ezer 2017 −24 d (95% CI 12–35), Chung 2025 20→4 d, Cheema 2017 36→24 d
  - (5) crowding-out sensitivity: non-pathway delay increases, per Olsson 2020, magnitude labelled as an ASSUMPTION
- **Headline uncertainty (cheap, same job):** a Beta-binomial posterior on each county's curative count from Taulukko 11, with the national 27.0% held as a fixed benchmark. Quick check run tonight (seed 1, Jeffreys prior): **≈66 per year (95% interval 52–80); Lapland ≈12 per year (8–16).** The Data Analyst must re-run and own this before it is spoken (DECISION 3). It covers sampling uncertainty only, not case-mix or recording.

**Compute (why Verda, honestly).** A toy version runs on a laptop. What Verda makes possible tonight:
- ABC-SMC with about 10⁶–10⁷ particles × 10⁴ simulated patients per particle per area (about 10¹⁰–10¹¹ patient-pathways).
- A full probabilistic sensitivity analysis over the unpublished referral→diagnosis leg.
- 22 counties × 6 scenarios × seed blocks.
- Re-running everything in minutes whenever the registry refreshes.

The implementation is JAX (`jax.random` + `vmap`) on one GPU per job, each job about 5–15 min, with a **Deadline of 30 min** and **Max concurrent jobs 8–16** (subject to quota). **Do not claim** "impossible on a laptop". The honest claim is "full-uncertainty calibration for all 22 counties, re-runnable on every data release, in minutes instead of overnight".

**Honesty guardrails (non-negotiable).**
1. Every model input is either (a) a published number with a table/page citation, or (b) an **ASSUMPTION** with a range, shown next to the output.
2. Outputs are limited to time-to-treatment and "% ≤42 days". **No lives saved, no survival, no curative-share effect.** No published link from days to curative share is in our sources.
3. The zero-effect scenario is always plotted.
4. Every output card carries the chip "MODEL OUTPUT · assumptions shown · not a forecast".
5. The 42 days is THL 21/2016 (marked outdated). Use the one-line caveat.
6. Fixed seeds; code, image digest and parameter files are published with the summary.
7. If calibration fails the posterior predictive check, **the Twin does not go on the AZ stage**. Only the Beta-binomial interval does.
8. Sim outputs enter the analyst's fact pack only as `type: model` cards. The analyst must say "modelled" when citing them.

## 3. Rough cost (list prices; covered by Junction credits)
| Item | Basis | Estimate |
|---|---|---|
| Batch jobs, calibration + scenarios | Serverless Containers H100 80 GB $5.77/h (spot $2.88). About 8–15 GPU-h including retries (or L40S at $2.22/h if the kernel fits) | **$45–90** (spot: about half) |
| Dev GPU instance (optional) | RTX A6000 $0.888/h × 3 h | about $3 |
| Proxy / orchestrator | CPU.4V.16G $0.048/h × 24 h | about $1.2 |
| Live analyst + cached answers | DeepSeek V4.1 Flash 1017: $0.15/M input, $0.006/M cache read, $0.60/M output. About 300 calls × 20k in / 1k out | about $1–2 |
| Red-team eval | 3,000 questions × 20k cached-prefix in + 600 out | about $2–5 |
| 22 county briefs × FI/EN | Kimi K3.1 Pro $2.00 in / $10.00 out per M, `reasoning_effort: low`, about 44 × (20k in + 3k out) | about $3–5 |
| Object Storage, registry | Tiny (MBs to a few GB). Object Storage Beta price is shown in the console | under $1 |
| **Total** | | **about $60–150** |

## 4. Architecture
```
 data/csv (sourced) ──build_targets.py──► targets.json ─┐
 data/hero.json, recs/top3.json ──build_facts.py──► facts.json ─┤──► Verda Object Storage (FIN-03, s3 eu-north-3)
                                                          │
 tasan-sim image (JAX, CUDA) ─► Verda Container registry ─► Serverless Containers BATCH JOB "tasan-sim"
      orchestrator (CPU instance) ── POST tasks.verda.com/tasan-sim/run?area=..&county=..&scenario=..&seeds=..
      each job: pull targets → simulate → write results/{run_id}/*.parquet to Object Storage → exit 0
      orchestrator polls /status, /result → aggregate.py → sim_results.json (+ posterior checks, plots)
                                                          │
 App (static, beacon.host) ◄── proxy on Verda CPU instance (key server-side, validator, cache)
                                  └─► Verda Inference https://inference.verda.com/v1 (deepseek-4-1-flash-1017; kimi-k3-1-pro for briefs)
 Red-team: redteam.py on CPU instance → 3k questions → validator → grounding_scorecard.json → Object Storage + summary
```
- Respect the rate-limit headers: use a semaphore and retry on 429 per `Retry-After`.
- Keep `max_tokens` realistic, because it reserves tokens-per-minute.
- The inference API key and Object Storage secret live **only** in proxy env vars. Check the built JS for leaks before every deploy.

## 5. Build plan (about 14 h; DA = Data Analyst, B = Builder)
The Builder is also carrying WIN_PLAN M3/M4 (one screen + analyst). **The proxy and analyst are shared work, so they count for both tracks.** The Twin is owned by DA.
| Time (EET) | DA | B |
|---|---|---|
| Sat 20:45–21:30 | Re-verify the people number + Beta-binomial interval (DECISION 3 gate). Write `build_targets.py` (Taulukko 4.1, 4.5 cumulative by month, 11 volumes) | Redeem credits (Junction Platform → Hackerpacks → Verda). Create the project. Enable `deepseek-4-1-flash-1017`. Inference key into proxy env. First test call |
| 21:30–00:00 | JAX microsim on CPU locally, 1 area. Reproduce the published median/IQR/monthly curve | Proxy on a CPU instance (CPU.4V.16G): `/ask`, `/brief`, validator, cache. `facts.json` v1 with DA |
| Sun 00:00–01:30 | Dockerfile (jax[cuda] + boto3 + FastAPI with `GET /health`, `POST /run`, exit after response). Push to the Container registry | Create the batch-job deployment (Deadline 30 min, Max concurrent 8). Smoke-test 1 job → Object Storage |
| 01:30–03:00 | Launch the ABC calibration fan-out (5 areas × seed blocks). Write `aggregate.py` and the posterior predictive plots | One-screen front (WIN_PLAN M4) |
| 03:00–05:00 | Sleep (jobs run; scale-to-zero after) | Sleep |
| 05:00–07:00 | Posterior check pass/fail. Scenario fan-out (22 counties × 6). `sim_results.json` + model fact cards | Pre-generate cached answers (3 chips + 10 questions) and 22 briefs |
| 07:00–08:30 | **Honesty review with Pitch** (guardrails 1–8). Go/no-go for the Twin on the AZ stage | Red-team batch (3k questions, FI/EN/SV, including traps: drugs, survival, unsourced counties) → `grounding_scorecard.json` |
| 08:30–10:00 | Write the process summary (§8) with screenshots: job list, Object Storage, plots | App: "Modelled with uncertainty" drawer card + "Runs on Verda (EU)" footer. Freeze candidate |
| 10:00–11:00 | Post the summary link to the Verda Discord channel **and** submit on the Junction Platform (the Verda blog says "submit via the official Junction Platform"; the challenge page says Discord. Do both) | Final deploy, leak check, offline cache test. **Freeze 11:00** |

**Minimum viable fallback (in order):**
1. If batch jobs misbehave, run the same image on **one GPU instance** (spot H100 or RTX A6000) with a loop over jobs. That is still Verda and still documented.
2. If calibration fails the check, ship only the **Beta-binomial interval** (as an Object Storage artefact from a single batch job), plus the **grounded analyst on Verda Inference**, plus the **red-team scorecard**. Say why on the Verda track: "we refused to publish a model that didn't reproduce the registry".
3. If Inference rate limits or an outage hit, serve cached answers (pre-generated on Verda; validator-checked).

## 6. Path to scale (demo → real users)
1. **All counties now:** the Twin already covers 22 counties. The analyst and brief drafter work for all 22.
2. **The pilot county (Lapland, 90 days):** T3 extracts the four THL 21/2016 time points. **The Twin is recalibrated on the county's own referral→treatment dates**, replacing the labelled ASSUMPTION with measured data. The output becomes a weekly early warning (projected % ≤42 days for the next month).
3. **County-hosted deployment for patient-level data:** the same container images run on infrastructure the county controls:
   - Verda Serverless Containers or an instance pinned to a **Finnish location (FIN-01/02/03)**, with an open-weight model self-served via vLLM (Verda's vLLM and GPT-OSS-120B tutorials) instead of the shared API
   - **Confidential computing** GPUs/CPUs where data must stay encrypted in use
   - or on-premises on the county's own servers
   - Aggregates only leave the county
4. **All cancers:** the stage structure is cancer-agnostic (the THL 21/2016 time points apply to all cancers). Add colorectal, breast and prostate as the registry publishes curves. The roadmap sets cancer-specific target times for 2026–2028 (3.1.2, p.57); swap in each target as it is set.
5. **Live feeds:** a scheduled batch job re-runs on each Cancer Registry / THL release (Sotkanet, THL eshjono cubes are API-accessible today). Later, it plugs into the national quality-register data the strategy plans (Goal 3.2) and into FICAN/THL peer review (roadmap 3.2.2, p.60).
6. **Cost at scale:** batch jobs scale to zero. A weekly re-run for 22 counties is on the order of a few GPU-hours. Inference is per token. This is a running cost a county can absorb (state this as a design claim, not a quote).

## 7. Score against the Verda criteria (honest, 0–5)
| Criterion (25% each) | Score if the plan lands | Why / risk |
|---|---|---|
| Ambition | **3** (4 if the full ABC + red-team scorecard both land) | Real full-uncertainty calibration and a 3k-question eval, but modest GPU-hours next to robotics and RL teams. Don't oversell |
| Fit | **4–5** | Batch jobs for an embarrassingly parallel fan-out; Inference for open weights with no data retention; Object Storage in FIN-03; CPU instance for the backend; Instant Clusters deliberately **not** used (explain why) |
| Working prototype | **4** | Runs end to end with job IDs, logs, artefacts and a public summary. Risk: calibration not converging by 07:00 → fallback 2 still scores 3 |
| Path to scale | **4–5** | A named county pilot, a county-hosted / FIN-pinned / confidential-computing route, all cancers, live feeds. This is the strongest card |
| **Overall** | **about 75–90%** | Podium-credible. 1st requires the Ambition story to land in the summary |

## 8. Discord process summary (outline; one public page, e.g. a README or the app's /verda page, link posted to Verda's Discord channel)
1. **One-liner:** "Tasan: equal lung-cancer care across Finland's 22 wellbeing services counties, with Finnish public health data processed on European compute."
2. **Problem and why compute:** Goal 3's "treatment within target times" is unmeasured. We quantify how much we don't know, and what a day-28 alert plus nurse navigator could change, with full uncertainty.
3. **Verda products used and why:** the table from §1, with the deliberate non-use of Instant Clusters.
4. **Architecture diagram** (§4) + screenshots: the batch-job deployment, the job list and status, Object Storage buckets (FIN-03), Inference usage.
5. **Process timeline:** what we tried, what failed (honestly), what we fixed. Include the job counts and GPU-minutes actually used, **from the console, not estimated**.
6. **Results:** the posterior predictive check plot; the people number with interval; "% ≤42 days" per county under scenarios, always including zero effect; the grounding scorecard (questions asked, % answered with citations, % correctly refused, unsourced numbers caught by the validator).
7. **Honesty box:** guardrails 1–8, the assumptions list, the model run location (Inference = Germany/EU; Object Storage = Finland), public aggregate data only.
8. **Path to scale** (§6) + cost per weekly re-run (measured).
9. **Repro:** image digest, seeds, parameter files, how to run one job (`curl -X POST https://tasks.verda.com/tasan-sim/run?...`).
10. **Team, links:** live app, repo, AZ challenge.

## 9. Risks
- **Scope creep endangers the AZ pitch.** It is the main prize. The Twin is a drawer card plus a Q&A answer, never the front screen. Hard go/no-go at 07:00–08:30.
- **The model is attacked as made-up.** Guardrails, the zero-effect line, the published posterior check, and "the spread *is* the finding".
- **Sovereignty overclaim.** Say "EU-hosted inference (Germany), Finnish storage". Never say "everything in Finland".
- **Preview and Beta products** (Inference preview, Object Storage Beta) may change or rate-limit. Use cached fallbacks.
- **Quota or capacity:** a model may show "Out of capacity" for new projects. Enable both models tonight.
- **Spot interruption:** use on-demand for the final scenario runs.
