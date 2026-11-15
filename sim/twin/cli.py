"""One container run = one county x scenario job.

  python -m twin.cli run --county 21 --scenario mid --seed 1 --n-runs 1000 --out /results
Every flag also reads an env var (TASAN_COUNTY, TASAN_SCENARIO, TASAN_SEED, TASAN_N_RUNS, TASAN_OUT),
so a batch platform can parameterise the job without changing the command.
Writes <out>/<scenario>/<county>.json and .csv. Exit code 0 = success.
"""
from __future__ import annotations
import argparse, csv, os, sys
from pathlib import Path
from .common import dump_json
from .model import run_job, result_rows, Inputs

def write_result(res, out):
    d = Path(out) / res["job"]["scenario"]; d.mkdir(parents=True, exist_ok=True)
    stem = d / res["job"]["county"]
    dump_json(res, f"{stem}.json")
    rows = result_rows(res)
    with open(f"{stem}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    return f"{stem}.json"

def main(argv=None):
    ap = argparse.ArgumentParser(prog="tasan-twin")
    sub = ap.add_subparsers(dest="cmd", required=True)
    r = sub.add_parser("run", help="run one county x scenario job")
    r.add_argument("--county", default=os.environ.get("TASAN_COUNTY"))
    r.add_argument("--scenario", default=os.environ.get("TASAN_SCENARIO", "baseline"))
    r.add_argument("--seed", type=int, default=int(os.environ.get("TASAN_SEED", "1")))
    r.add_argument("--n-runs", type=int, default=int(os.environ.get("TASAN_N_RUNS", "1000")))
    r.add_argument("--out", default=os.environ.get("TASAN_OUT", "results"))
    c = sub.add_parser("calibrate", help="ABC calibration job for one collaborative area")
    c.add_argument("--area", default=os.environ.get("TASAN_AREA"), required=False)
    c.add_argument("--particles", type=int, default=int(os.environ.get("TASAN_PARTICLES", "400")))
    c.add_argument("--seed", type=int, default=int(os.environ.get("TASAN_SEED", "20261114")))
    c.add_argument("--out", default=os.environ.get("TASAN_OUT", "results"))
    sub.add_parser("list", help="list counties and scenarios")
    a = ap.parse_args(argv)
    if a.cmd == "calibrate":
        from .calibrate import calibrate_area
        import time
        t0 = time.time(); r = calibrate_area(a.area, a.particles, a.seed); r["runtime_seconds"] = round(time.time() - t0, 2)
        dump_json(r, Path(a.out) / "calibration" / f"{a.area}.json")
        print(f"calibrated {a.area}: " + ", ".join(f"{k}={v['n_particles']}" for k, v in r["events"].items()) + f" [{r['runtime_seconds']}s]")
        return 0
    inp = Inputs()
    if a.cmd == "list":
        for c in inp.counties.values():
            print(c["code"], c["area"], c["annual_volume"], c["name_en"])
        print("scenarios:", ", ".join(inp.scenarios))
        return 0
    if not a.county:
        ap.error("--county (or TASAN_COUNTY) is required")
    res = run_job(a.county, a.scenario, a.seed, a.n_runs, inp)
    p = write_result(res, a.out)
    b = res["baseline"]["pct_le42_from_referral"]; d = res["delta_vs_baseline"]["pct_le42_from_referral"]
    print(f"[{res['chip']}] county={res['job']['county']} scenario={a.scenario} "
          f"%<=42d from referral baseline {b['median']} ({b['p2_5']}-{b['p97_5']}), delta {d['median']} ({d['p2_5']}-{d['p97_5']}) pp -> {p} "
          f"[{res['runtime_seconds']}s]")
    return 0

if __name__ == "__main__":
    sys.exit(main())
