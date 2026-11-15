# Tasan Pathway Twin (lung cancer: referral → diagnosis → first treatment)

> **MODEL OUTPUT · assumptions shown · not a forecast.** The outputs are pathway timings and shares only: % starting treatment ≤42 days, median days, patients per year within 42 days, and day-28 alert volume. There is **no survival, mortality, "lives saved" or curative-share effect**. Validation check 4 enforces this.

This builds the model in `review/VERDA_PLAN.md` §2 and PLAN.md DECISION 4, with these deviations:
- **numpy on CPU, not JAX on GPU.** A full 22 × 6 fan-out at 2,000 simulated years per job takes 18 s on 8 local cores, so a GPU adds cost without adding speed.
- **ABC rejection, not ABC-SMC.** It uses pre-declared tolerances. Accepted particles are the posterior.

## Quick start (no Docker needed)
```bash
cd /workspace/junction-new/sim
N_RUNS=2000 ./run_all.sh          # = make all: targets → calibrate → ppc → params → 132 jobs → aggregate → validate
python3 -m twin.validate          # the go/no-go gate; exit 0 = PASS (report: build/validation_report.json)
python3 -m twin.cli run --county 21 --scenario mid --seed 1 --n-runs 1000 --out results   # one job
python3 -m twin.cli list          # county codes + scenarios
python3 -m twin.verda_dryrun      # planned Verda jobs + estimated $ (no API call)
```
Only dependency: `numpy` (requirements.txt). `make` targets mirror `run_all.sh`.

## Layout
| Path | What |
|---|---|
| `twin/build_targets.py` | reads `../data/csv/*` → `build/targets.json` (every value with file/table/URL + input SHA-256) |
| `twin/calibrate.py` | ABC calibration per collaborative area (YTA) × first-event type → `build/posterior.json`; `--curve-only` writes a structural-sensitivity variant |
| `twin/ppc.py` | posterior predictive check against Taulukko 4.5, 4.1 and the derived curve → `build/calibration_report.json` |
| `twin/model.py` | microsimulation; one "run" = one simulated year for a county |
| `twin/cli.py` | **container entrypoint**: one run = one county × scenario (`--county --scenario --seed --n-runs --out`, or env `TASAN_COUNTY/SCENARIO/SEED/N_RUNS/OUT`); writes `<out>/<scenario>/<county>.json` + `.csv`. Also `calibrate --area` for a per-area ABC job |
| `twin/server.py` | Verda batch-job HTTP mode (image default CMD): `GET /health`, then one `POST /run?county=..&scenario=..&seed=..&n_runs=..` (or `/calibrate?area=..`), then the process exits 0/1 |
| `twin/runner.py` | local runner: all 22 counties × 6 scenarios (`--via-cli` spawns the CLI per job, exactly as a container would) |
| `twin/aggregate.py` | → `results/sim_results.json` (incl. `type: model` fact cards for the analyst) + `results/sim_summary.csv` |
| `twin/params.py` | parameter provenance registry → `build/parameters.json` |
| `twin/validate.py` | the 9-check gate |
| `config/*.json` | calibration tolerances/priors, assumptions, scenarios, Verda list prices |
| `Dockerfile` | python:3.12-slim + numpy; ships built targets/posterior (no credentials, no cloud SDK) |
| `deploy/verda/` | batch-deployment template, guarded `submit_jobs.py` (dry-run default), `verda_api.py`, `smoke_instance.py` |

## Model
For each newly diagnosed lung cancer patient (cohort = Poisson(county annual volume)):
1. **First event within 6 months** is surgery / non-palliative RT / drug therapy / palliative care / death / none. The mix is Dirichlet around the Taulukko 4.5 month-6 shares of the county's collaborative area.
2. **Diagnosis → first event, in days.** A point mass at day 0 plus a lognormal, truncated at 6 months. Parameters are ABC-calibrated per area and type. Each simulated year draws one posterior particle per type.
3. **Referral → diagnosis.** This interval is **unpublished**, so it is an ASSUMPTION: a lognormal with median U(7, 35) d and log-sd U(0.4, 0.9), redrawn each simulated year. The output also reports a sensitivity table at fixed medians of 7/14/21/28/35 d.
4. **Scenarios.** Baseline and scenario use the **same simulated patients** (common random numbers), so the deltas are paired. In the intervention, patients still untreated at day 28 after referral get an alert. Their referral → treatment time is cut by the scenario's effect E, but not below day 28.

**Scenarios** (`config/scenarios.json`):
| id | effect E | source |
|---|---|---|
| baseline | none | calibrated pathway |
| zero_effect | 0 d (full intervention code path) | Battaglia 2016: navigation had no effect at 60/180 d. Always shown |
| low | 12 d | Cheema 2017, 36→24 d (reflex EGFR/ALK) |
| mid | 16 d | Chung 2025, 20→4 d (one-stop clinic) |
| high | N(24, sd 5.9) ≥ 0 | Ezer 2017, −24 d (95% CI 12–35) (rapid investigation clinic) |
| crowding_out | 16 d, plus U(0, 5) d added to non-alerted patients | Olsson 2020 gives the direction only; the magnitude is an ASSUMPTION |

All effect sizes rest on an **ASSUMPTION (effect_transfer)**: they come from *other* interventions in other countries. Study citations are in `recs/top3.md`.

## Parameter provenance
The full machine-readable registry is `build/parameters.json`: 122 entries (58 sourced, 25 calibrated, 22 derived, 15 assumption, 2 design). Check 6 fails if any model input lacks a source or an ASSUMPTION/DESIGN label.

| Input | Kind | Source |
|---|---|---|
| First-event cumulative % by month 0–6, per YTA (6 event types) | sourced | Keuhkosyöpä Suomessa 2024 (Syöpärekisteri/FICAN), **Taulukko 4.5** (PDF p.34; month 6 = Taulukko 4.6). `data/csv/lung_report2024_first_event_cumulative_by_yta.csv`. https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf |
| Q1 / median / Q3 days diagnosis → first surgery / RT / drug, per YTA | sourced (calibration target) | same report, **Taulukko 4.1** (PDF p.28). `csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv` |
| Patients per YTA (Dirichlet pseudo-counts) | sourced | **Taulukko 3.3** (PDF p.18). `csv/lung_report2024_treatment_6m_by_yta.csv` |
| Derived first-active-treatment curve + Wilson CI (secondary check) | derived | `csv/lung_derived_first_active_treatment_by_month_yta.csv` (team, from 4.5 + 3.3) |
| Timing posterior (π0, μ, σ) per YTA × type | calibrated | ABC to the two rows above; `config/calibration.json` |
| County annual volume = N(2019–2023) / 5; county → YTA mapping | derived / sourced | Keuhkosyöpä Suomessa 2019–2023 (publ. 23.4.2026), **Taulukko 11**. `csv/lung_report2026_treatment_by_wsc.csv`. https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html |
| 42-day target (referral arrival → first treatment) | sourced | THL Ohjaus 21/2016 §4.1, PDF p.14 (`data/TREATMENT_TARGETS.md`). **Marked "Vanhentunut" (outdated); no lung-specific limit** |
| Referral → diagnosis median 7–35 d, log-sd 0.4–0.9 | **ASSUMPTION** | No Finnish data (`TREATMENT_TARGETS.md` §3, `DATA_GAPS.md`). Range brackets the THL §4.1 one-week step targets |
| 1 month = 30.4375 d | **ASSUMPTION** | The report does not define months in days |
| Poisson year-to-year volume; counties inherit their YTA's timing and mix; period mismatch (timing 2018–22 vs volumes 2019–23) | **ASSUMPTION** | `config/assumptions.json` |
| Alert day 28 | **DESIGN** | Tasan design choice (`recs/top3.md` T3) |
| Scenario effects / crowding magnitude | **ASSUMPTION** (effect_transfer) | studies above |

## Calibration fit, posterior predictive check
Simulated with the job sampler: 200,000 patients per area, integrating over the posterior. Tolerances were declared before fitting: ≤1.5 pp absolute on every Taulukko 4.5 point (months 1–5 fitted; month 6 is exact by construction) and ≤7 days on every Taulukko 4.1 quartile.

| Area (YTA) | worst curve error (pp) | worst quartile error (d) | derived first-active curve inside 95% CI | 4.5-only refit shift in % ≤42 d from dx | pass |
|---|---|---|---|---|---|
| Etelä-Suomi | 1.27 | 6.0 | 2/6 months | +0.5 pp | ✅ |
| Itä-Suomi | 1.27 | 5.0 | 6/6 | −2.1 pp | ✅ |
| Länsi-Suomi | 0.87 | 4.0 | 5/6 | +0.0 pp | ✅ |
| Pohjois-Suomi | 1.37 | 6.2 | 6/6 | −0.8 pp | ✅ |
| Sisä-Suomi | 1.26 | 6.0 | 5/6 | +1.3 pp | ✅ |

Simulated vs published quartiles for surgery (Q1/median/Q3): Pohjois 0/13/43 vs 0/13.5/44; Etelä 27/42/63 vs 33/46/63.

**Known tension.** Taulukko 4.1 counts the first *treatment* (patients may have had palliative care first). Taulukko 4.5 counts the first *event* and is smoothed by the registry's multistate model. A joint fit therefore runs **slightly early versus 4.1** (simulated quartiles 1–6 d lower, mostly for drug therapy) and **low at month 1 versus 4.5** in Etelä-Suomi (−2.8 pp on the summed active curve). Refitting to 4.5 alone, with a tighter 0.5 pp tolerance, moves "% ≤42 d from diagnosis" by at most 2.1 pp. Full detail is in `build/calibration_report.json`.

## Validation, `python3 -m twin.validate` (last run: PASS, 14 Nov 2026 ~20:28 EET)
| # | check | result |
|---|---|---|
| 1 | inputs present; targets rebuilt; month-6 shares sum to 100 ± 0.3 | PASS (sums 100.0–100.2; 22 counties) |
| 2 | calibration within tolerance in all 5 areas | PASS (table above) |
| 3 | zero-effect = baseline, all 22 counties, tolerance 0.1 pp | PASS: max paired delta **0.0**; max difference vs a separately run baseline job **0.0** |
| 4 | no forbidden phrases (lives saved, deaths averted, survival, mortality, QALY, FI equivalents; 21 phrases) in 532 output files | PASS |
| 5 | same seed gives identical output; different seed gives different output | PASS |
| 6 | every parameter has a source or an ASSUMPTION/DESIGN label | PASS (122/122) |
| 7 | CLI with env vars runs one job, exit 0 | PASS |
| 8 | Verda batch HTTP contract (`/health` 200, one `POST /run`, process exits 0) | PASS |
| 9 | Docker build + run | **SKIPPED locally**: no docker/podman on this box, and the apt mirror returned HTTP 500. **Built and run on the Verda smoke-test instance instead** (Docker 29.9.2, 23 s build, 271 MB image). Two CLI jobs plus one HTTP batch call ran, the container exited 0, and the outputs were **byte-identical to the local run** (`results_verda_smoke/`, `data/SPEND.md`) |

## Headline baseline outputs (seed 1, 2,000 simulated years per job; median and 2.5–97.5% interval)
| | % ≤42 d **from referral** (assumption-dependent) | % ≤42 d from diagnosis (data-anchored) | Δ pp, mid what-if (−16 d) | Δ pp, zero effect |
|---|---|---|---|---|
| Lapland (21) | 33.3 (14.3–57.8) | 63.9 (50.8–76.7) | +17.6 (8.3–28.8) | 0.0 (0.0–0.0) |
| Helsinki (90) | 25.5 (11.2–47.5) | 58.1 (50.0–67.0) | +19.2 (12.0–27.5) | 0.0 |
| Pirkanmaa (08) | 28.9 (14.2–49.3) | 59.5 (50.9–67.3) | +18.0 (11.0–26.3) | 0.0 |

**How wide the unknown is.** In Lapland, % ≤42 d from referral is **54% if referral → diagnosis has a 7-day median, but 19% at 35 days**. The 7–35 d range is our assumption. That gap is the case for measuring the Tasan clock. Counties within one collaborative area differ only through volume, because they share the area's timing. Do **not** present county-to-county differences within an area as findings.

## Limitations
1. **Referral → diagnosis is unpublished.** It dominates the referral-anchored output, which spans roughly 10–60%. Report it as a range, never as a point.
2. **No county-level timing exists.** All counties in a collaborative area share its timing, and Taulukko 11 intent categories cannot be mapped to modality without inventing a mapping.
3. **The registry diagnosis date can equal the treatment date** (Q1 = 0 for surgery in Itä, Pohjois and Sisä). The point mass reproduces this, but short diagnosis-anchored times partly reflect how the date is recorded.
4. **Taulukko 4.1 and 4.5 cover different populations**, and 4.5 is model-smoothed (see calibration).
5. **The 42-day target** comes from the outdated THL 21/2016 generic limit.
6. **Effect sizes are what-ifs** transferred from other interventions. Patients are floored at the alert day, and every alerted patient is assumed reached.
7. **Crowding out as modelled cannot cross 42 days.** Non-alerted patients are by definition treated by day 28, and the extra delay is at most 5 d, so on "% ≤42 d" it equals the mid scenario. The real crowding risk falls on non-lung patients, which is outside this model.
8. **Period mismatch.** Timing covers patients diagnosed 2018–6/2022; volumes cover 2019–2023. Åland is excluded by the registry.
9. **Uncertainty intervals** combine parameter, assumption, effect and cohort (Poisson) variation. They are not confidence intervals of a measured quantity.

## Verda plan and credentials
**Smoke test**, approved with a $2 cap, done 14 Nov 20:30–20:34 EET: 1 × 1V100.4V spot in FIN-01, about 2 min, **≈$0.01**. Everything was deleted and verified via the API (0 instances, volumes or keys). See `data/SPEND.md` and `results_verda_smoke/smoke_log.json`. Rerun: `python3 deploy/verda/smoke_instance.py` (needs `VERDA_CLIENT_ID`/`VERDA_CLIENT_SECRET` in env; never printed).

**Proposed full run** (`python3 -m twin.verda_dryrun`; list prices from https://verda.com/pricing, read 14 Nov 2026):
| Option | Hardware | Jobs | Runtime per job | Est. $ |
|---|---|---|---|---|
| **A (recommended): Serverless Containers batch jobs** | "AMD Rome+" CPU 8 vCPU/32 GB, $0.11/h | 132 scenario jobs (22 × 6, 20,000 simulated years each) + 5 ABC jobs (one per area) | ~12 s compute (measured locally, largest county) + ~3 min spin-up/down overhead (ASSUMPTION), billed 4 min; ABC budgeted 5 min each (measured 12 s at 4,000 particles) | **$1.04 single pass; $2.28 with ×2 retries + registry**. ~76 min wall-clock at 8 concurrent |
| B: one CPU instance, loop over all jobs | CPU.8V.32G $0.096/h | same 137 jobs in one process | ~3 min total compute + boot | < $0.10 (billed in 10-min increments). **No CPU instance was available on 14 Nov 20:35 EET** |
| C: one spot GPU instance (what the smoke test used) | 1V100.4V spot $0.122/h (FIN-01) | same, looped | ~5 min | < $0.10 |
| not recommended: GPU serverless | L40S $2.22/h / H100 $5.77/h | 137 | same | $21 / $55 per pass, for no speed-up |

**Credentials and config a batch run needs beyond an inference API key** (checked against docs, 14 Nov 2026):
1. **Cloud API credentials** (Client ID + Client Secret; OAuth2 client-credentials at `POST https://api.verda.com/v1/oauth2/token`). These are needed for any API, CLI or Terraform automation (instances, deployments, SSH keys, buckets). https://docs.verda.com/welcome-to-verda/api-credentials/, https://docs.verda.com/infrastructure-as-code/terraform/authentication/ (env `VERDA_CLIENT_ID`/`VERDA_CLIENT_SECRET`). *Available in env; used only for the smoke test.*
2. **Container registry credentials** to push the image and to let the deployment pull it. For the Verda Container Registry these are a credential name `vcr-<PROJECT_ID>+<name>` plus a secret, used with `docker login vccr.io/<PROJECT_ID>`. Alternatives are a Docker Hub token, a GHCR token, or a Docker `config.json` auth. https://docs.verda.com/storage/container-registry/quickstart/, https://docs.verda.com/containers/container-registries/. *Not available.* Batch serverless jobs need this.
3. **An Inference API key**, which is also the Bearer token for `containers.verda.com` / `tasks.verda.com` (job trigger, `/status`, `/result`). The vLLM container quickstart says: "generate an authentication token, by going to Credentials → Inference API Keys". https://docs.verda.com/containers/batch-jobs/, https://docs.verda.com/containers/tutorials/deploy-with-vllm-quick/. Use a separate key from the analyst proxy.
4. **Optional:** Object Storage S3 access key + secret, separate from the Cloud API credentials, *only* if results go to a FIN-03 bucket instead of `/result`. https://docs.verda.com/storage/object-storage/quickstart/
5. **Config:** a project with a positive balance (usage is prepaid; https://docs.verda.com/welcome-to-verda/pricing-and-billing/), and a batch deployment with port 8000, health check `/health`, max concurrent jobs 8 and deadline 30 min (`deploy/verda/deployment.example.json`). All credentials are tied to the team member who created them.

Options B and C need only credential 1 (plus an ephemeral SSH key generated per run). Option A needs 1 (or the console), 2 and 3.

## Verda process (Discord-ready summary; updated 14 Nov 2026 21:45 EET)
**Tasan Pathway Twin on Verda.** This is a lung-cancer pathway microsimulation for Finland's 22 wellbeing services counties. It is calibrated to Finnish Cancer Registry timing curves and run on Verda in Finland (FIN-01).

**What we ran**
1. **Local first.** `python -m twin.validate` passes 8 checks; Docker was skipped locally (no runtime on the dev box). The checks: calibration within pre-declared tolerance in all 5 collaborative areas, zero-effect scenario = baseline exactly, no forbidden outcome wording, fixed-seed reproducibility, and every parameter sourced or labelled ASSUMPTION.
2. **Smoke test (20:30–20:34 EET).** API-provisioned `1V100.4V` spot instance in FIN-01. Built our Docker image on it (23 s), ran 2 jobs plus 1 batch-HTTP call, and got output byte-identical to local. Cost ≈ $0.01.
3. **Full run, single instance (20:37–21:10 EET).** Same instance type, chosen because no CPU instance was available in any Finnish location at the time. Ran all **132 county × scenario jobs** (22 counties × 6 scenarios × 20,000 simulated years = **2.64 M simulated county-years**) plus **5 ABC calibration jobs** (4,000 accepted particles per area and event type).
   - Timings: build 21 s; scenario jobs 1,372 s on 4 vCPU; calibration 7–21 s per area.
   - **Result: all 132 job JSON/CSV outputs and all 5 posteriors are byte-identical to our local run** with the same seeds (runtime fields excluded), so the run is reproducible across machines.
   - **Cost ≈ $0.08** (32.7 min × $0.122/h spot).
4. **Serverless batch jobs (21:37–21:42 EET): image pushed and deployment created, but job submission is blocked by our dev-box network.**
   - A temporary `1V100.4V` spot instance built the image (18 s) and pushed it to Verda Container Registry (8 s, 271 MB). The registry password went in via `--password-stdin`, and the Docker config was wiped. The instance, its volume and its key were deleted and checked by ID; the instance lived 1.4 min.
   - We registered the pull credential `tasan-sim-pull` through `POST /v1/container-registry-credentials` (type `verda`). We created the job deployment `tasan-sim-twin` through `POST /v1/job-deployments` (compute `CPU Node` size 8 = AMD Rome+, max 8 replicas, deadline 600 s). It was `ready` 6 s later.
   - **Blocker:** our dev box cannot open TLS to `tasks.verda.com` (the sandbox egress proxy drops the handshake), while `api.verda.com` and `vccr.io` work. No job reached Verda. The deployment was deleted within 6 s (404 verified), at ≈ $0 cost.
   - Next: run the submitter from a network that can reach `tasks.verda.com`, or allow that host in the box egress.

**Verda products used:** Cloud API (OAuth2 client credentials), GPU instance (spot) in FIN-01, block storage (OS volume). Container Registry (push + pull credential) and a Serverless Containers job deployment on the AMD Rome+ CPU tier (created; jobs not yet submitted, see 4). **Not used, on purpose:** GPUs for compute (the model is numpy on CPU, so a GPU adds cost without speed) and Instant Clusters (the work is embarrassingly parallel).

**Total spend so far: ≈ $0.11.** Every instance, volume and SSH key we created was deleted and checked via the API (logged in `data/SPEND.md`).

**Lessons**
- **Check availability first.** CPU instance types showed *no* availability in FIN-01/02/03 all evening, while an old V100 spot was the cheapest machine on offer. Our CPU-only container ran on it unchanged.
- **The OAuth access token expires after about 25–30 min.** Our cleanup failed with HTTP 401 on the first full run, and the instance lived 6 extra minutes until a manual delete. Refresh the token on 401 (now in `verda_api.py`).
- **The OS volume can survive instance deletion.** Pass the OS volume id once (it appears in both `os_volume_id` and `volume_ids`), then explicitly `PUT /v1/volumes {"action":"delete","is_permanent":true}` and verify `/volumes` and `/volumes/trash` are empty.
- **Shared projects:** delete only the resources your run created, by id. Never "delete all keys".
- **Old 4-vCPU V100 hosts are about 4× slower per core than a modern dev box** (41 s vs 10 s per job). For CPU work, the serverless AMD Rome+ tier ($0.11/h, 8 vCPU) is the better fit once registry credentials exist.

**Repro:** `python3 deploy/verda/run_instance.py` (needs `VERDA_CLIENT_ID`/`VERDA_CLIENT_SECRET` in env; never printed). Image digest: sha256:a90c7554… (built on the instance from this folder). Seeds: 1 for scenarios, 20261114 for calibration.

**Serverless how-to (what worked):**
- Registry credentials: create them once in the console (the API cannot create push credentials). The pull side *can* be registered via the API: `POST /v1/container-registry-credentials {"name","type":"verda","username","access_token"}`.
- Job deployment compute name is `"CPU Node"` with `size` 8/16/32 (see `GET /v1/serverless-compute-resources`), **not** `AMD Rome+` or `CPU.8V.32GC`. `deadline_seconds` must be ≥ 600.
- Scripts: `deploy/verda/push_image.py` (temporary build/push instance) and `deploy/verda/run_serverless.py` (create deployment → submit 137 jobs → collect → delete deployment in `finally`).
- Check that `https://tasks.verda.com` is reachable from your machine *before* creating the deployment.

### Run (B) final status (2026-11-14 23:20 EET): NOT COMPLETED
The image was pushed and the deployment was created, but the box's egress blocked `tasks.verda.com`, so no jobs ran. The planned retry from a temp Verda instance was never launched, because the user ended the work at 23:19. All our Verda resources are deleted and API-verified (0 instances, 0 volumes, 0 deployments, and the pull credential removed). Only the tiny image remains in the registry. (B) cost ≈ $0.02, and the final sim total is ≈ $0.11 of the $5 cap. Run (A) is the Verda result.
