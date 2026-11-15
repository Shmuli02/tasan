#!/usr/bin/env python3
"""Submit the Tasan Twin fan-out to a Verda batch-job deployment.  DEFAULT = DRY RUN (prints requests, sends nothing).

Sending requires ALL of:  --execute  AND  env TASAN_VERDA_BUDGET_APPROVED=yes  AND  env VERDA_INFERENCE_API_KEY.
Do not run with --execute until the user has approved a Verda credit budget (team cap: ~$50 target, $100 hard cap;
this simulation is planned at < $15 - see `python -m twin.verda_dryrun`).
Each job uses X-Inference-Id = tasan-<county>-<scenario>-s<seed> so re-submitting is idempotent (409 if in progress).
"""
import argparse, json, os, sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from twin.model import Inputs  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--deployment", default="tasan-twin"); ap.add_argument("--seed", type=int, default=1)
ap.add_argument("--n-runs", type=int, default=20000); ap.add_argument("--execute", action="store_true")
ap.add_argument("--out", default="results_verda")
a = ap.parse_args()
inp = Inputs()
jobs = [(c, s) for c in sorted(inp.counties) for s in inp.scenarios]
base = f"https://tasks.verda.com/{a.deployment}"
send = a.execute and os.environ.get("TASAN_VERDA_BUDGET_APPROVED") == "yes" and os.environ.get("VERDA_INFERENCE_API_KEY")
if a.execute and not send:
    sys.exit("refusing: --execute needs TASAN_VERDA_BUDGET_APPROVED=yes and VERDA_INFERENCE_API_KEY (budget approval first)")
if not send:
    for c, s in jobs:
        print(f"DRY RUN  POST {base}/run?county={c}&scenario={s}&seed={a.seed}&n_runs={a.n_runs}  X-Inference-Id: tasan-{c}-{s}-s{a.seed}")
    print(f"{len(jobs)} jobs listed, none sent."); sys.exit(0)

import urllib.request  # only imported on the approved path
key = os.environ["VERDA_INFERENCE_API_KEY"]
def req(method, url, jid):
    r = urllib.request.Request(url, method=method, data=b"" if method == "POST" else None,
                               headers={"Authorization": f"Bearer {key}", "X-Inference-Id": jid})
    with urllib.request.urlopen(r, timeout=60) as f:
        return f.status, f.read()
ids = []
for c, s in jobs:
    jid = f"tasan-{c}-{s}-s{a.seed}"
    st, body = req("POST", f"{base}/run?county={c}&scenario={s}&seed={a.seed}&n_runs={a.n_runs}", jid)
    ids.append((jid, c, s)); print("submitted", jid, st)
out = Path(a.out); pending = set(i[0] for i in ids)
while pending:
    time.sleep(20)
    for jid, c, s in ids:
        if jid not in pending:
            continue
        st, body = req("GET", f"https://tasks.verda.com/status/{a.deployment}", jid)
        status = json.loads(body).get("Status")
        # NOTE: terminal status names are not listed in the docs (only "Queue" is shown) - verify on the first smoke job.
        if status in ("Completed", "Succeeded", "Success", "Done"):
            _, res = req("GET", f"https://tasks.verda.com/result/{a.deployment}", jid)
            (out / s).mkdir(parents=True, exist_ok=True); (out / s / f"{c}.json").write_bytes(res); pending.discard(jid)
        elif status in ("Failed", "Error"):
            print("FAILED", jid); pending.discard(jid)
print("done; aggregate with: python -m twin.aggregate --results", a.out)
