#!/usr/bin/env python3
"""Run (B) step 1: temp spot instance -> build sim image -> docker login (password via stdin) -> push to vccr.io -> wipe docker config -> DELETE instance/volume/key (by recorded ID only).
Credentials only from env (VERDA_CLIENT_ID/SECRET), never printed. Ephemeral SSH key in a temp dir, deleted at the end.
Cleanup runs in `finally` and from a deadman timer (MAX_LIFE_MIN), then verifies via the API that nothing is left.
"""
import json, os, shutil, subprocess, sys, tarfile, tempfile, threading, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verda_api import call

SIM = Path(__file__).resolve().parents[2]
OUT = SIM / "results_verda_serverless"
MAX_LIFE_MIN = 30
ATTEMPTS = [("1V100.4V", "24.04.cuda12.9-v100.docker", 0.122)]
CAP_USD = 2.0
LOG = {"events": []}
state = {"iid": None, "vol": None, "key": None, "t_create": None, "price": None, "cleaned": False}
lock = threading.Lock()

def log(msg, **kw):
    e = {"t": time.strftime("%H:%M:%S"), "msg": msg, **kw}; LOG["events"].append(e); print(json.dumps(e), flush=True)

def cleanup(reason):
    with lock:
        if state["cleaned"]:
            return
        log("cleanup start", reason=reason)
        if state["iid"]:
            st, inst = call("GET", f"/instances/{state['iid']}")
            vols = []
            if isinstance(inst, dict):
                vols = sorted({v for v in ([inst.get("os_volume_id")] + list(inst.get("volume_ids") or [])) if v})  # dedupe: os volume is also listed in volume_ids
            state["vol"] = vols
            st, b = call("PUT", "/instances", {"action": "delete", "id": state["iid"], "volume_ids": vols, "delete_permanently": True})
            log("delete instance", status=st, volumes=len(vols), body=str(b)[:200])
            for _ in range(60):
                st, inst = call("GET", f"/instances/{state['iid']}")
                if st == 404 or (isinstance(inst, dict) and inst.get("status") in ("discontinued", "notfound")):
                    break
                time.sleep(5)
            log("instance after delete", status=st, inst_status=inst.get("status") if isinstance(inst, dict) else str(inst)[:120])
            for v in state["vol"]:  # instance delete can leave the OS volume detached (seen 14.11.2026) -> delete it explicitly
                st_v, _ = call("PUT", "/volumes", {"action": "delete", "id": v, "is_permanent": True}); log("delete volume", status=st_v)
            if state["t_create"]:
                state["life_min"] = round((time.time() - state["t_create"]) / 60, 1)
        if state["key"]:  # delete ONLY our own key by id (the project is shared with other agents)
            st, b = call("DELETE", f"/ssh-keys/{state['key']}"); log("delete ssh key", status=st)
        state["cleaned"] = True

def ssh(kf, kh, ip, cmd, timeout=900):
    return subprocess.run(["ssh", "-i", kf, "-o", f"UserKnownHostsFile={kh}", "-o", "StrictHostKeyChecking=accept-new",
                           "-o", "ConnectTimeout=10", "-o", "BatchMode=yes", f"root@{ip}", cmd], capture_output=True, text=True, timeout=timeout)

def main():
    tmp = tempfile.mkdtemp(prefix="tasan_smoke_"); os.chmod(tmp, 0o700)
    kf, kh = f"{tmp}/k", f"{tmp}/known_hosts"
    deadman = None
    try:
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "tasan-sim-push-key", "-f", kf], check=True)
        st, kid = call("POST", "/ssh-keys", {"name": "tasan-sim-push-key", "key": Path(kf + ".pub").read_text().strip()})
        if st not in (200, 201, 202):
            log("ssh key add failed", status=st, body=str(kid)[:200]); return 1
        state["key"] = kid if isinstance(kid, str) else (kid.get("id") if isinstance(kid, dict) else None)
        log("ssh key added")
        spent_cap_ok = True
        for itype, image, price in ATTEMPTS:
            worst = price * MAX_LIFE_MIN / 60
            if worst > CAP_USD:
                log("skip type over cap", itype=itype); continue
            st, av = call("GET", f"/instance-availability/{itype}?is_spot=true&location_code=FIN-01")
            if av is not True:
                log("not available", itype=itype, status=st); continue
            payload = {"instance_type": itype, "image": image, "ssh_key_ids": [state["key"]], "hostname": "tasan-sim-push",
                       "description": "Tasan Twin smoke test - auto-deleted", "location_code": "FIN-01", "is_spot": True, "contract": "SPOT",
                       "os_volume": {"name": "tasan-sim-push-os", "size": 50, "on_spot_discontinue": "delete_permanently"},
                       "tags": [{"key": "project", "value": "tasan-sim"}]}
            st, iid = call("POST", "/instances", payload)
            log("deploy", itype=itype, status=st, body=str(iid)[:200])
            if st in (200, 201, 202) and isinstance(iid, str):
                state.update(iid=iid, t_create=time.time(), price=price, itype=itype)
                break
        if not state["iid"]:
            log("no instance deployed"); return 1
        deadman = threading.Timer(MAX_LIFE_MIN * 60, cleanup, args=("deadman timer",)); deadman.daemon = True; deadman.start()
        ip = None
        for _ in range(120):
            st, inst = call("GET", f"/instances/{state['iid']}")
            s = inst.get("status") if isinstance(inst, dict) else None
            if s == "running" and inst.get("ip"):
                ip = inst["ip"]; break
            if s in ("error", "no_capacity", "installation_failed", "discontinued"):
                log("instance failed", inst_status=s); return 1
            time.sleep(10)
        log("instance running", minutes=round((time.time() - state["t_create"]) / 60, 1))
        if not ip:
            return 1
        for _ in range(30):
            if ssh(kf, kh, ip, "true", 30).returncode == 0:
                break
            time.sleep(10)
        tarp = f"{tmp}/sim.tgz"
        with tarfile.open(tarp, "w:gz") as t:
            for p in ["Dockerfile", ".dockerignore", "requirements.txt", "twin", "config", "build/targets.json", "build/posterior.json",
                      "build/parameters.json", "build/calibration_report.json"]:
                t.add(SIM / p, arcname=f"sim/{p}", filter=lambda ti: None if "__pycache__" in ti.name else ti)
        r = subprocess.run(["scp", "-i", kf, "-o", f"UserKnownHostsFile={kh}", "-o", "BatchMode=yes", tarp, f"root@{ip}:/root/sim.tgz"], capture_output=True, text=True)
        log("upload", rc=r.returncode)
        project = os.environ["VERDA_REGISTRY_USERNAME"].split("+")[0][len("vcr-"):]
        image = f"vccr.io/{project}/tasan-sim-twin:0.1.0"
        r = ssh(kf, kh, ip, "set -e; cd /root && tar xzf sim.tgz && cd sim && T0=$(date +%s) && docker build -q -t tasan-twin:0.1.0 . >/dev/null && echo build_s=$(( $(date +%s)-T0 ))", 900)
        log("build", rc=r.returncode, stdout=r.stdout[-300:], stderr=r.stderr[-300:])
        if r.returncode != 0:
            return 1
        # secret goes only through ssh stdin -> docker login --password-stdin (never on a command line, never logged)
        p = subprocess.run(["ssh", "-i", kf, "-o", f"UserKnownHostsFile={kh}", "-o", "BatchMode=yes", f"root@{ip}",
                            f"docker login vccr.io -u '{os.environ['VERDA_REGISTRY_USERNAME']}' --password-stdin >/dev/null 2>&1 && echo login_ok"],
                           input=os.environ["VERDA_REGISTRY_SECRET"], capture_output=True, text=True, timeout=120)
        log("registry login", ok="login_ok" in p.stdout)
        if "login_ok" not in p.stdout:
            ssh(kf, kh, ip, "rm -f /root/.docker/config.json", 60); return 1
        r = ssh(kf, kh, ip, f"set -e; docker tag tasan-twin:0.1.0 {image}; T0=$(date +%s); docker push -q {image} >/dev/null; echo push_s=$(( $(date +%s)-T0 )); "
                            f"docker image inspect {image} --format 'digest={{{{index .RepoDigests 0}}}} size={{{{.Size}}}}'", 900)
        w = ssh(kf, kh, ip, "docker logout vccr.io >/dev/null 2>&1; rm -f /root/.docker/config.json; test ! -e /root/.docker/config.json && echo wiped", 60)
        log("push", rc=r.returncode, stdout=r.stdout[-400:], stderr=r.stderr[-300:], docker_config_wiped="wiped" in w.stdout)
        LOG["image"] = image
        LOG["push_stdout"] = r.stdout
        return 0 if r.returncode == 0 else 1
        OUT.mkdir(exist_ok=True)
        r2 = subprocess.run(["scp", "-r", "-i", kf, "-o", f"UserKnownHostsFile={kh}", "-o", "BatchMode=yes", f"root@{ip}:/root/out/.", str(OUT)], capture_output=True, text=True)
        log("download", rc=r2.returncode)
        return 0 if r.returncode == 0 else 1
    finally:
        if deadman:
            deadman.cancel()
        cleanup("finally")
        shutil.rmtree(tmp, ignore_errors=True)
        # verify OUR resources only, by recorded id
        left = {}
        if state["iid"]:
            st, inst = call("GET", f"/instances/{state['iid']}")
            left["instance_status"] = inst.get("status") if isinstance(inst, dict) else st
        for v in state.get("vol") or []:
            st, vv = call("GET", f"/volumes/{v}")
            left[f"volume_{v[:8]}"] = (vv.get("status") if isinstance(vv, dict) else st)
        if state["key"]:
            st, _ = call("GET", f"/ssh-keys/{state['key']}"); left["ssh_key_http"] = st
        life = state.get("life_min")
        est = round((state["price"] or 0) * (max(10, -(-life // 10) * 10) if life else 0) / 60 + 50 * 0.2 / 730 * ((life or 0) / 60), 4)
        LOG.update(leftover_check=left, instance_type=state.get("itype"), life_min=life, est_cost_usd_10min_rounded=est)
        log("final", **{k: LOG[k] for k in ("leftover_check", "instance_type", "life_min", "est_cost_usd_10min_rounded")})
        OUT.mkdir(exist_ok=True); (OUT / "push_log.json").write_text(json.dumps(LOG, indent=1))

if __name__ == "__main__":
    sys.exit(main())
