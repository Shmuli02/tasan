"""Local runner: every county x scenario as an independent job (same code path as one container run).

  python -m twin.runner --n-runs 1000 --seed 1 --out results [--workers 8] [--via-cli]
--via-cli spawns `python -m twin.cli run ...` per job, i.e. exactly what one container does.
"""
from __future__ import annotations
import argparse, subprocess, sys, time
from concurrent.futures import ProcessPoolExecutor, as_completed
from .model import Inputs, run_job
from .cli import write_result

def _job(args):
    county, scenario, seed, n_runs, out, via_cli = args
    t0 = time.time()
    if via_cli:
        subprocess.run([sys.executable, "-m", "twin.cli", "run", "--county", county, "--scenario", scenario,
                        "--seed", str(seed), "--n-runs", str(n_runs), "--out", out], check=True, capture_output=True)
    else:
        write_result(run_job(county, scenario, seed, n_runs), out)
    return county, scenario, time.time() - t0

def main(argv=None):
    ap = argparse.ArgumentParser()
    ap.add_argument("--n-runs", type=int, default=1000); ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--out", default="results"); ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--scenario", action="append"); ap.add_argument("--county", action="append")
    ap.add_argument("--via-cli", action="store_true")
    a = ap.parse_args(argv)
    inp = Inputs()
    counties = a.county or sorted(inp.counties); scenarios = a.scenario or list(inp.scenarios)
    jobs = [(c, s, a.seed, a.n_runs, a.out, a.via_cli) for c in counties for s in scenarios]
    t0 = time.time(); times = []
    with ProcessPoolExecutor(max_workers=a.workers) as ex:
        for f in as_completed([ex.submit(_job, j) for j in jobs]):
            c, s, dt = f.result(); times.append(dt)
    wall = time.time() - t0
    print(f"{len(jobs)} jobs ({len(counties)} counties x {len(scenarios)} scenarios), n_runs={a.n_runs}: "
          f"wall {wall:.1f}s, per-job mean {sum(times)/len(times):.2f}s max {max(times):.2f}s, workers={a.workers}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
