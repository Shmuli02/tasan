"""DRY RUN ONLY: print the planned Verda batch jobs and the estimated cost. Makes NO network/API call.

  python -m twin.verda_dryrun [--n-runs 20000] [--compute "AMD Rome+ (8 vCPU, 32 GB, no GPU)"] [--overhead-min 3] [--cap-usd 15]
Per-job runtime is measured locally (largest county, slowest scenario) unless --per-job-seconds is given.
"""
from __future__ import annotations
import argparse, math, time, sys
from .common import CONFIG_DIR, load_json
from .model import Inputs, run_job

def main(argv=None):
    pr = load_json(CONFIG_DIR / "verda_pricing.json")
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-runs", type=int, default=20000)
    ap.add_argument("--compute", default="AMD Rome+ (8 vCPU, 32 GB, no GPU)", choices=list(pr["serverless_compute"]))
    ap.add_argument("--spot", action="store_true")
    ap.add_argument("--overhead-min", type=float, default=3.0, help="ASSUMPTION: billed spin-up (incl. image pull) + spin-down minutes per job")
    ap.add_argument("--per-job-seconds", type=float)
    ap.add_argument("--calibration-jobs", type=int, default=5, help="one ABC job per collaborative area")
    ap.add_argument("--calibration-minutes", type=float, default=5.0, help="ABC with ~10x more particles; ~1 min measured-scale, 5 min budgeted")
    ap.add_argument("--retry-factor", type=float, default=2.0, help="budget multiplier for retries / re-runs")
    ap.add_argument("--max-concurrent", type=int, default=8)
    ap.add_argument("--cap-usd", type=float, default=15.0)
    a = ap.parse_args(argv)
    inp = Inputs()
    counties = sorted(inp.counties); scen = list(inp.scenarios)
    if a.per_job_seconds is None:
        big = max(inp.counties.values(), key=lambda c: c["annual_volume"])["code"]
        n_b = min(a.n_runs, 2000); t0 = time.time(); run_job(big, "high", 1, n_b, inp)
        per = (time.time() - t0) * a.n_runs / n_b
        how = f"measured locally: county {big} (largest), scenario 'high', {n_b} runs, scaled to {a.n_runs} (1 core)"
    else:
        per, how = a.per_job_seconds, "given"
    jobs = [f"POST https://tasks.verda.com/tasan-twin/run?county={c}&scenario={s}&seed=1&n_runs={a.n_runs}" for c in counties for s in scen]
    rate = pr["serverless_compute"][a.compute]["spot_usd_per_h" if a.spot else "usd_per_h"]
    bill_min_job = math.ceil(per / 60 + a.overhead_min)
    sim_min = len(jobs) * bill_min_job
    cal_min = a.calibration_jobs * math.ceil(a.calibration_minutes + a.overhead_min)
    usd = (sim_min + cal_min) / 60 * rate
    usd_budget = usd * a.retry_factor + 0.20  # + registry storage (<1 GiB-month)
    wall = math.ceil(len(jobs) / a.max_concurrent) * bill_min_job + math.ceil(a.calibration_jobs / a.max_concurrent) * math.ceil(a.calibration_minutes + a.overhead_min)
    print("=== Tasan Pathway Twin: Verda batch plan (DRY RUN, nothing is sent) ===")
    print(f"compute type      : Serverless Containers batch job, {a.compute}{' SPOT' if a.spot else ''} @ ${rate}/h  [{pr['source_url']}, read {pr['read_on']}]")
    print(f"deployment        : name tasan-twin, port 8000, healthcheck /health, max concurrent jobs {a.max_concurrent}, deadline 30 min")
    print(f"scenario jobs     : {len(jobs)} = {len(counties)} counties x {len(scen)} scenarios ({', '.join(scen)}), n_runs={a.n_runs}")
    print(f"calibration jobs  : {a.calibration_jobs} (one per collaborative area), budgeted {a.calibration_minutes} min each")
    print(f"runtime per job   : {per:.1f} s compute ({how}) + {a.overhead_min} min overhead ASSUMPTION -> billed {bill_min_job} min")
    print(f"billed minutes    : {sim_min} (scenarios) + {cal_min} (calibration) = {sim_min + cal_min} min = {(sim_min + cal_min)/60:.2f} h")
    print(f"estimated cost    : ${usd:.2f} single pass; ${usd_budget:.2f} budgeted (x{a.retry_factor} retries + $0.20 registry)")
    print(f"wall-clock        : ~{wall} min at {a.max_concurrent} concurrent replicas")
    for name, p in pr["serverless_compute"].items():
        if name != a.compute:
            alt = (sim_min + cal_min) / 60 * p["usd_per_h"]
            print(f"   alt {name:32s}: ${alt:.2f} single pass (code is CPU/numpy: a GPU adds cost, not speed)")
    print("first 3 job requests (not sent):"); [print("   " + j) for j in jobs[:3]]
    print(f"budget check      : {'OK' if usd_budget <= a.cap_usd else 'OVER CAP'} vs cap ${a.cap_usd:.2f}")
    return 0 if usd_budget <= a.cap_usd else 2

if __name__ == "__main__":
    sys.exit(main())
