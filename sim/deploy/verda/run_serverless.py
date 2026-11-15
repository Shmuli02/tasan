#!/usr/bin/env python3
"""Run (B): Verda Serverless Containers BATCH JOBS on CPU (compute "CPU Node" size 8 = CPU.8V.32GC "AMD Rome+", $0.11/h).
Creates job deployment tasan-sim-twin (pull credential tasan-sim-pull, created separately), submits 132 /run + 5 /calibrate
jobs to https://tasks.verda.com/tasan-sim-twin with Bearer VERDA_API_KEY, collects /result, then DELETES the deployment
(by its exact name) in `finally`. Secrets are read from env only and never printed/logged/written.
Stop-loss: wall clock MAX_WALL_MIN (worst-case cost = 8 replicas x MAX_WALL_MIN x $0.11/h)."""
import json, os, sys, time, urllib.request, urllib.error
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
HERE = Path(__file__).resolve().parent; SIM = HERE.parents[1]
sys.path.insert(0, str(HERE)); sys.path.insert(0, str(SIM))
from verda_api import call
from twin.model import Inputs
from twin.cli import write_result
from twin.common import dump_json, AREAS

NAME = "tasan-sim-twin"; CRED = "tasan-sim-pull"
PROJECT = os.environ["VERDA_REGISTRY_USERNAME"].split("+")[0][len("vcr-"):]
IMAGE = f"vccr.io/{PROJECT}/tasan-sim-twin:0.1.0"
OUT = SIM / "results_verda_serverless"; MAX_WALL_MIN = 60; SEED, NRUNS = 1, 20000; PARTICLES, CSEED = 4000, 20261114
LOG = {"events": []}
def log(msg, **kw):
    e = {"t": time.strftime("%H:%M:%S"), "msg": msg, **kw}; LOG["events"].append(e); print(json.dumps(e), flush=True)

KEY = os.environ["VERDA_API_KEY"]
def task(method, url, jid, timeout=60):
    r = urllib.request.Request(url, method=method, data=b"" if method == "POST" else None,
                               headers={"Authorization": f"Bearer {KEY}", "X-Inference-Id": jid})
    try:
        with urllib.request.urlopen(r, timeout=timeout) as f:
            return f.status, f.read()
    except urllib.error.HTTPError as e:
        return e.code, e.read()[:2000]
    except Exception as e:  # network
        return -1, str(e).encode()

def main():
    inp = Inputs()
    jobs = [("cal", a, None) for a in AREAS] + [("run", c, s) for c in sorted(inp.counties) for s in inp.scenarios]
    def jid(j): return f"tasan-sim-cal-{j[1].lower()}-s{CSEED}" if j[0] == "cal" else f"tasan-sim-{j[1]}-{j[2]}-s{SEED}"
    def url(j): return (f"https://tasks.verda.com/{NAME}/calibrate?area={j[1]}&particles={PARTICLES}&seed={CSEED}" if j[0] == "cal"
                        else f"https://tasks.verda.com/{NAME}/run?county={j[1]}&scenario={j[2]}&seed={SEED}&n_runs={NRUNS}")
    t0 = time.time(); created = False
    try:
        body = {"name": NAME, "container_registry_settings": {"credentials": {"name": CRED}},
                "containers": [{"image": IMAGE, "exposed_port": 8000,
                                "healthcheck": {"enabled": True, "port": 8000, "path": "/health"},
                                "env": [{"name": "TASAN_OUT", "value_or_reference_to_secret": "/tmp/results", "type": "plain"}]}],
                "compute": {"name": "CPU Node", "size": 8},
                "scaling": {"max_replica_count": 8, "queue_message_ttl_seconds": 7200, "deadline_seconds": 600}}
        st, r = call("POST", "/job-deployments", body); created = st in (200, 201)
        log("create deployment", status=st, body=str(r)[:400])
        if not created:
            return 1
        for _ in range(60):
            st, r = call("GET", f"/job-deployments/{NAME}/status")
            s = r.get("status") if isinstance(r, dict) else r
            if s in ("ready", "running"):
                break
            time.sleep(10)
        log("deployment status", status=s, after_s=round(time.time() - t0))
        if s not in ("ready", "running"):
            return 1
        ts = time.time()
        with ThreadPoolExecutor(8) as ex:
            subs = list(ex.map(lambda j: (j, task("POST", url(j), jid(j))), jobs))
        log("submitted", n=len(subs), statuses=sorted({x[1][0] for x in subs}), first=subs[0][1][1].decode(errors="replace")[:200], s=round(time.time() - ts))
        pending = {jid(j): j for j, (st, _) in subs if st in (200, 201, 202)}
        failed = {jid(j): f"submit {st}" for j, (st, _) in subs if st not in (200, 201, 202)}
        seen = {}; done = {}
        while pending and (time.time() - t0) / 60 < MAX_WALL_MIN:
            time.sleep(20)
            def poll(item):
                k, j = item
                st, b = task("GET", f"https://tasks.verda.com/status/{NAME}", k)
                try: s = json.loads(b).get("Status")
                except Exception: s = f"http{st}"
                return k, j, s
            with ThreadPoolExecutor(8) as ex:
                res = list(ex.map(poll, list(pending.items())))
            counts = {}
            for k, j, s in res:
                counts[s] = counts.get(s, 0) + 1
                if str(s).lower() in ("queue", "queued", "pending", "running", "inprogress", "in_progress", "processing", "started", "none"):
                    continue
                st, b = task("GET", f"https://tasks.verda.com/result/{NAME}", k)
                try: d = json.loads(b)
                except Exception: d = None
                if st == 200 and isinstance(d, dict) and ("job" in d or "events" in d):
                    if j[0] == "cal": dump_json(d, OUT / "calibration" / f"{j[1]}.json")
                    else: write_result(d, OUT)
                    done[k] = s; pending.pop(k)
                elif str(s).lower() in ("failed", "error", "cancelled", "canceled", "expired", "timeout"):
                    failed[k] = f"{s} {st} {b[:200]!r}"; pending.pop(k)
                else:
                    seen[k] = f"{s} {st} {b[:120]!r}"
            log("poll", elapsed_min=round((time.time() - t0) / 60, 1), done=len(done), pending=len(pending), failed=len(failed), statuses=counts)
        LOG.update(done=len(done), failed=failed, pending_at_end=sorted(pending), odd_status_samples=dict(list(seen.items())[:5]),
                   terminal_statuses=sorted(set(done.values())), jobs_wall_s=round(time.time() - ts))
        return 0 if not pending and not failed else 2
    finally:
        if created:
            st, r = call("DELETE", f"/job-deployments/{NAME}"); log("delete deployment", status=st, body=str(r)[:200])
            for _ in range(30):
                st2, r2 = call("GET", f"/job-deployments/{NAME}")
                if st2 == 404: break
                time.sleep(10)
            log("deployment after delete", http=st2, status=(r2.get("status") if isinstance(r2, dict) else str(r2)[:100]))
            LOG["deployment_after_delete_http"] = st2
        LOG["total_wall_min"] = round((time.time() - t0) / 60, 2)
        OUT.mkdir(exist_ok=True); (OUT / "run_log.json").write_text(json.dumps(LOG, indent=1))

if __name__ == "__main__":
    sys.exit(main())
