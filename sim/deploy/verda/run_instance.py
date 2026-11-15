#!/usr/bin/env python3
"""Verda single-instance FULL run (approved, cap $5 for A+B): spot instance -> build sim image -> 132 scenario jobs + 5 calibration jobs -> copy back -> DELETE everything.
Credentials only from env (VERDA_CLIENT_ID/SECRET), never printed. Ephemeral SSH key in a temp dir, deleted at the end.
Cleanup runs in `finally` and from a deadman timer (MAX_LIFE_MIN), then verifies via the API that nothing is left.
"""
import json, os, shutil, subprocess, sys, tarfile, tempfile, threading, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
from verda_api import call

SIM = Path(__file__).resolve().parents[2]
OUT = SIM / "results_verda"
MAX_LIFE_MIN = 45
ATTEMPTS = [("1V100.4V", "24.04.cuda12.9-v100.docker", 0.122), ("1A100.22V", "24.04.cuda12.9.docker", 1.193)]
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
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "tasan-full-ephemeral", "-f", kf], check=True)
        st, kid = call("POST", "/ssh-keys", {"name": "tasan-full-ephemeral", "key": Path(kf + ".pub").read_text().strip()})
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
            payload = {"instance_type": itype, "image": image, "ssh_key_ids": [state["key"]], "hostname": "tasan-full",
                       "description": "Tasan Twin smoke test - auto-deleted", "location_code": "FIN-01", "is_spot": True, "contract": "SPOT",
                       "os_volume": {"name": "tasan-full-os", "size": 50, "on_spot_discontinue": "delete_permanently"},
                       "tags": [{"key": "project", "value": "tasan-full"}]}
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
        script = r"""set -e; cd /root && tar xzf sim.tgz && cd sim
echo "nproc=$(nproc)"; docker --version
T0=$(date +%s); docker build -q -t tasan-twin:0.1.0 . >/dev/null; echo "build_s=$(( $(date +%s)-T0 ))"
docker image inspect tasan-twin:0.1.0 --format 'image_id={{.Id}} size={{.Size}}'
mkdir -p /root/out && chmod 777 /root/out
T0=$(date +%s); docker run --rm -v /root/out:/results tasan-twin:0.1.0 python -m twin.runner --n-runs 20000 --seed 1 --workers $(nproc) --out /results; echo "scenario_jobs_s=$(( $(date +%s)-T0 ))"
for A in YTA-ETELA YTA-ITA YTA-LANSI YTA-POHJOIS YTA-SISA; do T0=$(date +%s); docker run --rm -v /root/out:/results tasan-twin:0.1.0 python -m twin.cli calibrate --area $A --particles 4000 --out /results; echo "calib_${A}_s=$(( $(date +%s)-T0 ))"; done
docker run --rm -v /root/out:/results tasan-twin:0.1.0 python -m twin.aggregate --results /results
du -sh /root/out
"""
        r = ssh(kf, kh, ip, script, 2100)
        log("remote run", rc=r.returncode, stdout=r.stdout[-3000:], stderr=r.stderr[-800:])
        OUT.mkdir(exist_ok=True)
        r2 = subprocess.run(["scp", "-r", "-i", kf, "-o", f"UserKnownHostsFile={kh}", "-o", "BatchMode=yes", f"root@{ip}:/root/out/.", str(OUT)], capture_output=True, text=True)
        log("download", rc=r2.returncode)
        return 0 if r.returncode == 0 else 1
    finally:
        if deadman:
            deadman.cancel()
        cleanup("finally")
        shutil.rmtree(tmp, ignore_errors=True)
        st_i, ins = call("GET", "/instances"); st_v, vol = call("GET", "/volumes"); st_k, keys = call("GET", "/ssh-keys")
        st_t, trash = call("GET", "/volumes/trash")
        left = {"instances_not_discontinued": [i.get("id") for i in ins if i.get("status") not in ("discontinued",)] if isinstance(ins, list) else str(ins)[:100],
                "volumes": len(vol) if isinstance(vol, list) else str(vol)[:100],
                "volumes_in_trash": len(trash) if isinstance(trash, list) else str(trash)[:100],
                "ssh_keys": len(keys) if isinstance(keys, list) else str(keys)[:100]}
        life = state.get("life_min")
        est = round((state["price"] or 0) * (max(10, -(-life // 10) * 10) if life else 0) / 60 + 50 * 0.2 / 730 * ((life or 0) / 60), 4)
        LOG.update(leftover_check=left, instance_type=state.get("itype"), life_min=life, est_cost_usd_10min_rounded=est)
        log("final", **{k: LOG[k] for k in ("leftover_check", "instance_type", "life_min", "est_cost_usd_10min_rounded")})
        OUT.mkdir(exist_ok=True); (OUT / "run_log.json").write_text(json.dumps(LOG, indent=1))

if __name__ == "__main__":
    sys.exit(main())
