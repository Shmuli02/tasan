#!/usr/bin/env python3
"""Launch tasan-extract-p2, run the phase-2 session script, copy results, API-delete.

Dry-run by default. Requires --execute and TASAN_VERDA_BUDGET_APPROVED=yes.
Cleanup is scoped to IDs this process creates. 404 on SSH key delete is success.
Never prints IPs, keys, or tokens.
"""
from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
import threading
import time
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE = Path(__file__).resolve().parent
EXTRACT = HERE.parents[1]
sys.path.insert(0, str(Path("/workspace/junction-new/sim/deploy/verda")))
from verda_api import call  # noqa: E402

HOSTNAME = "tasan-extract-p2"
KEY_NAME = "tasan-extract-p2-ephemeral"
VOL_NAME = "tasan-extract-p2-os"
RUN = HERE.parent / ".run_p2"
STATE_PATH = RUN / "state.json"
STOP_PATH = RUN / "STOP"
DONE_LOCAL = RUN / "DONE"
LOG_PATH = HERE / "last_phase2_log.json"
PAYLOAD = HERE / "payload.tgz"
SESSION = HERE / "run_session.sh"
OUT_TGZ = EXTRACT / "eval" / "results" / "phase2" / "tasan-extract-out.tgz"

EET = timezone(timedelta(hours=2), name="EET")
lock = threading.Lock()
state = {"iid": None, "vols": [], "key": None, "ip": None, "t_create": None, "cleaned": False, "price": 2.386}
LOG = {"events": [], "synthetic_note": "no real patient data on this instance"}
deadman = None
tmp = None


def now() -> str:
    return datetime.now().strftime("%H:%M:%S")


def log(msg: str, **kw) -> None:
    ev = {"t": now(), "msg": msg, **{k: v for k, v in kw.items() if k not in ("ip", "key_material")}}
    LOG["events"].append(ev)
    print(json.dumps(ev, default=str), flush=True)


def write_state(extra=None) -> None:
    RUN.mkdir(parents=True, exist_ok=True)
    blob = {k: state[k] for k in state}
    if extra:
        blob.update(extra)
    STATE_PATH.write_text(json.dumps(blob, default=str))
    os.chmod(STATE_PATH, 0o600)


def ssh(kf, kh, ip, cmd, timeout=900):
    try:
        return subprocess.run(
            ["ssh", "-i", kf, "-o", f"UserKnownHostsFile={kh}",
             "-o", "StrictHostKeyChecking=accept-new", "-o", "ConnectTimeout=15",
             "-o", "BatchMode=yes", "-o", "RequestTTY=no",
             "-o", "ServerAliveInterval=15", "-o", "ServerAliveCountMax=4",
             "-o", "LogLevel=ERROR", f"root@{ip}", cmd],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ""
        err = e.stderr or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        if isinstance(err, bytes):
            err = err.decode(errors="replace")
        return subprocess.CompletedProcess(e.cmd, -1, out, err + "\nTIMEOUT")


def cleanup(reason: str) -> None:
    with lock:
        if state["cleaned"]:
            return
        log("cleanup start", reason=reason)
        if state["iid"]:
            st, inst = call("GET", f"/instances/{state['iid']}")
            vols = []
            if isinstance(inst, dict):
                vols = sorted({v for v in ([inst.get("os_volume_id")] + list(inst.get("volume_ids") or [])) if v})
            for v in state["vols"]:
                if v not in vols:
                    vols.append(v)
            st, b = call("PUT", "/instances", {
                "action": "delete", "id": state["iid"], "volume_ids": vols, "delete_permanently": True,
            })
            log("delete instance", status=st, n_volumes=len(vols), body=str(b)[:200])
            for _ in range(40):
                st, inst = call("GET", f"/instances/{state['iid']}")
                if st == 404 or (isinstance(inst, dict) and inst.get("status") in ("discontinued", "notfound", "deleted")):
                    break
                time.sleep(3)
            for v in vols:
                st_v, _ = call("PUT", "/volumes", {"action": "delete", "id": v, "is_permanent": True})
                log("delete volume", status=st_v, vol_prefix=str(v)[:8])
        if state["key"]:
            st, b = call("DELETE", f"/ssh-keys/{state['key']}")
            log("delete ssh key", status=st, already_gone=(st == 404))
        state["cleaned"] = True


def verify_gone() -> dict:
    out = {"instance_gone": True, "volumes_gone": True, "key_gone": True, "details": {}}
    if state["iid"]:
        st, inst = call("GET", f"/instances/{state['iid']}")
        gone = st == 404 or (isinstance(inst, dict) and inst.get("status") in ("discontinued", "notfound", "deleted"))
        out["instance_gone"] = bool(gone)
        out["details"]["instance_status"] = st if st == 404 else (inst.get("status") if isinstance(inst, dict) else str(inst)[:80])
    for v in state["vols"]:
        st, body = call("GET", f"/volumes/{v}")
        status = body.get("status") if isinstance(body, dict) else None
        listed = False
        stl, allv = call("GET", "/volumes")
        if isinstance(allv, list) and any(x.get("id") == v for x in allv):
            listed = True
        if st != 404 and status not in ("deleted", "discontinued") and listed:
            out["volumes_gone"] = False
            out["details"][f"volume_{v[:8]}"] = {"http": st, "status": status, "listed": listed}
        else:
            out["details"][f"volume_{v[:8]}"] = {"http": st, "status": status, "listed": listed, "treated_as_gone": True}
    if state["key"]:
        st, keys = call("GET", "/ssh-keys")
        if isinstance(keys, list) and any(k.get("id") == state["key"] for k in keys):
            out["key_gone"] = False
        else:
            out["key_gone"] = True
    stl, insts = call("GET", "/instances")
    out["details"]["n_instances_in_project"] = len(insts) if isinstance(insts, list) else None
    return out


def _scp(kf, kh, ip, remote, local, timeout=120) -> bool:
    Path(local).parent.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(
            ["scp", "-i", kf, "-o", f"UserKnownHostsFile={kh}", "-o", "BatchMode=yes",
             "-o", "ConnectTimeout=15", "-o", "LogLevel=ERROR",
             f"root@{ip}:{remote}", str(local)],
            stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=timeout,
        )
        exists = Path(local).exists()
        log("scp", remote_name=Path(remote).name, rc=r.returncode, exists=exists,
            bytes=Path(local).stat().st_size if exists else 0)
        return r.returncode == 0 and exists
    except subprocess.TimeoutExpired:
        log("scp timeout", remote_name=Path(remote).name)
        return False


def pull_results(kf, kh, ip) -> bool:
    OUT_TGZ.parent.mkdir(parents=True, exist_ok=True)
    ok = _scp(kf, kh, ip, "/root/tasan-extract-out.tgz", OUT_TGZ, 180)
    # Always also try logs so a failed session is diagnosable.
    for remote, name in (
        ("/var/log/tasan-extract-p2.log", "session.remote.log"),
        ("/root/tasan-extract-FAILED", "FAILED.txt"),
        ("/root/tasan-extract-DONE", "DONE.txt"),
        ("/root/session.stderr", "session.stderr"),
        ("/root/session.stdout", "session.stdout"),
    ):
        _scp(kf, kh, ip, remote, OUT_TGZ.parent / name, 60)
    return ok


def main() -> int:
    global deadman, tmp
    ap = argparse.ArgumentParser()
    ap.add_argument("--execute", action="store_true")
    ap.add_argument("--watchdog-min", type=int, default=150)
    ap.add_argument("--instance-type", default="1A100.22V")
    ap.add_argument("--location", default="FIN-01")
    ap.add_argument("--image", default="24.04.cuda13.4.docker")
    ap.add_argument("--volume-gb", type=int, default=200)
    ap.add_argument("--price", type=float, default=2.386)
    args = ap.parse_args()
    plan = {
        "dry_run": not args.execute, "instance_type": args.instance_type,
        "location_code": args.location, "is_spot": False, "image": args.image,
        "os_volume_gb": args.volume_gb, "hostname": HOSTNAME,
        "watchdog_min": args.watchdog_min, "price_usd_per_h_list": args.price,
        "cap_usd": 50.0, "notes": ["SYNTHETIC only", "controller API-deletes our IDs only"],
    }
    print(json.dumps(plan, indent=2))
    if not args.execute:
        log("dry-run only")
        return 0
    if os.environ.get("TASAN_VERDA_BUDGET_APPROVED") != "yes":
        print("refusing: --execute requires TASAN_VERDA_BUDGET_APPROVED=yes", file=sys.stderr)
        return 2
    if not PAYLOAD.exists() or not SESSION.exists():
        print("missing payload.tgz or run_session.sh", file=sys.stderr)
        return 2

    RUN.mkdir(parents=True, exist_ok=True)
    STOP_PATH.unlink(missing_ok=True)
    DONE_LOCAL.unlink(missing_ok=True)
    tmp = tempfile.mkdtemp(prefix="tasan_p2_")
    kf = str(Path(tmp) / "k")
    kh = str(Path(tmp) / "known_hosts")
    rc = 1
    try:
        # SSH key
        subprocess.run(["ssh-keygen", "-t", "ed25519", "-N", "", "-f", kf, "-q"], check=True)
        pub = Path(kf + ".pub").read_text().strip()
        # persist a copy for debugging ssh later (0600)
        shutil.copy2(kf, RUN / "id_ed25519")
        os.chmod(RUN / "id_ed25519", 0o600)
        st, body = call("POST", "/ssh-keys", {"name": KEY_NAME, "key": pub})
        kid = None
        if isinstance(body, dict):
            kid = body.get("id")
        elif isinstance(body, str):
            kid = body
        if st not in (200, 201, 202) or not kid:
            # maybe returned object
            log("ssh key add failed", status=st, body=str(body)[:200])
            return 1
        state["key"] = kid
        log("ssh key added", name=KEY_NAME)

        st_s, avail_s = call("GET", f"/instance-availability/{args.instance_type}?is_spot=true&location_code={args.location}")
        st_o, avail_o = call("GET", f"/instance-availability/{args.instance_type}?is_spot=false&location_code={args.location}")
        log("availability", status_spot=st_s, spot=avail_s, status_od=st_o, od=avail_o,
            instance_type=args.instance_type, location=args.location)
        use_spot = avail_s is True
        if not use_spot and avail_o is not True:
            log("A100 not available (spot or od), abort without create")
            return 1
        price = 1.193 if use_spot else args.price
        state["price"] = price
        log("chosen market", is_spot=use_spot, price=price)

        def deploy(is_spot, with_contract=True):
            payload = {
                "instance_type": args.instance_type, "image": args.image,
                "ssh_key_ids": [state["key"]], "hostname": HOSTNAME,
                "description": "Tasan Extract phase2 LoRA — auto-deleted, SYNTHETIC only",
                "location_code": args.location, "is_spot": is_spot,
                "os_volume": {"name": VOL_NAME, "size": args.volume_gb},
                "tags": [{"key": "project", "value": "tasan-extract"}],
            }
            if with_contract:
                payload["contract"] = "PAY_AS_YOU_GO"
            return call("POST", "/instances", payload)

        st, iid = deploy(use_spot, True)
        log("deploy", status=st, body=str(iid)[:240], contract="PAY_AS_YOU_GO", is_spot=use_spot)
        if st not in (200, 201, 202):
            st, iid = deploy(use_spot, False)
            log("deploy retry no contract", status=st, body=str(iid)[:240], is_spot=use_spot)
        if st not in (200, 201, 202) and use_spot and avail_o is True:
            log("spot create failed, falling back to on-demand")
            use_spot = False
            price = args.price
            state["price"] = price
            st, iid = deploy(False, True)
            log("deploy od fallback", status=st, body=str(iid)[:240])
            if st not in (200, 201, 202):
                st, iid = deploy(False, False)
                log("deploy od fallback no contract", status=st, body=str(iid)[:240])
        if st not in (200, 201, 202):
            return 1
        if isinstance(iid, str):
            state["iid"] = iid
        elif isinstance(iid, dict):
            state["iid"] = iid.get("id") or iid.get("instance_id")
        else:
            return 1
        state["t_create"] = time.time()
        write_state()

        deadman = threading.Timer(args.watchdog_min * 60, cleanup, args=("local deadman timer",))
        deadman.daemon = True
        deadman.start()

        ip = None
        for _ in range(180):
            st, inst = call("GET", f"/instances/{state['iid']}")
            s = inst.get("status") if isinstance(inst, dict) else None
            if isinstance(inst, dict):
                vols = [v for v in ([inst.get("os_volume_id")] + list(inst.get("volume_ids") or [])) if v]
                if vols:
                    state["vols"] = vols
            if s == "running" and inst.get("ip"):
                ip = inst["ip"]
                break
            if s in ("error", "no_capacity", "installation_failed", "discontinued"):
                log("instance failed", inst_status=s)
                return 1
            time.sleep(10)
        log("instance running", minutes=round((time.time() - state["t_create"]) / 60, 1))
        if not ip:
            return 1
        state["ip"] = ip
        write_state()

        ssh_ready = False
        for i in range(60):
            r = ssh(kf, kh, ip, "echo SSH_OK", 20)
            if r.returncode == 0 and "SSH_OK" in (r.stdout or ""):
                ssh_ready = True
                log("ssh ready", attempt=i)
                break
            log("ssh not ready yet", attempt=i, rc=r.returncode)
            time.sleep(10)
        if not ssh_ready:
            log("ssh never became ready")
            return 1

        for label, src, dest in (("session", SESSION, "/root/run_session.sh"), ("payload", PAYLOAD, "/root/payload.tgz")):
            ok = False
            for i in range(6):
                try:
                    scp = subprocess.run(
                        ["scp", "-i", kf, "-o", f"UserKnownHostsFile={kh}", "-o", "BatchMode=yes",
                         "-o", "ConnectTimeout=15", "-o", "LogLevel=ERROR", str(src), f"root@{ip}:{dest}"],
                        stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60,
                    )
                except subprocess.TimeoutExpired:
                    log("scp timeout", what=label, attempt=i)
                    time.sleep(5)
                    continue
                if scp.returncode == 0:
                    ok = True
                    break
                log("scp failed", what=label, attempt=i, rc=scp.returncode)
                time.sleep(5)
            if not ok:
                log("scp never succeeded", what=label)
                return 1
        log("files copied")

        remote = (
            "chmod +x /root/run_session.sh && "
            f"if [ ! -f /root/session.pid ] || ! kill -0 $(cat /root/session.pid) 2>/dev/null; then "
            f"TASAN_WATCHDOG_MIN={args.watchdog_min} "
            "setsid /root/run_session.sh </dev/null >/root/session.stdout 2>/root/session.stderr & "
            "echo $! > /root/session.pid; fi; echo SESSION_DISPATCHED"
        )
        dispatched = False
        for i in range(8):
            r = ssh(kf, kh, ip, remote, 45)
            if r.returncode == 0 and "SESSION_DISPATCHED" in (r.stdout or ""):
                dispatched = True
                log("session dispatched", attempt=i)
                break
            log("dispatch retry", attempt=i, rc=r.returncode)
            time.sleep(8)
        if not dispatched:
            log("session dispatch failed")
            return 1

        # Block in large intervals until DONE, FAILED, STOP, or instance gone.
        while True:
            if STOP_PATH.exists():
                log("stop file seen")
                pull_results(kf, kh, ip)
                break
            rdy = ssh(kf, kh, ip, "if [ -f /root/tasan-extract-DONE ]; then echo DONE; cat /root/tasan-extract-DONE; elif [ -f /root/tasan-extract-FAILED ]; then echo FAILED; cat /root/tasan-extract-FAILED; else echo RUNNING; tail -n 3 /var/log/tasan-extract-p2.log 2>/dev/null; fi", 30)
            out = (rdy.stdout or "").strip()
            if out.startswith("DONE"):
                log("remote DONE")
                DONE_LOCAL.write_text(out + "\n")
                pull_results(kf, kh, ip)
                rc = 0
                break
            if out.startswith("FAILED"):
                log("remote FAILED", detail=out[:300])
                pull_results(kf, kh, ip)
                rc = 1
                break
            st, inst = call("GET", f"/instances/{state['iid']}")
            s = inst.get("status") if isinstance(inst, dict) else None
            if st == 404 or s in ("discontinued", "error"):
                log("instance already gone while waiting", status=st, inst_status=s)
                break
            # large-chunk wait
            time.sleep(180)
        return rc
    except KeyboardInterrupt:
        log("interrupted")
        try:
            if state.get("ip"):
                pull_results(str(Path(tmp) / "k"), str(Path(tmp) / "known_hosts"), state["ip"])
        except Exception:
            pass
        return 1
    finally:
        if deadman:
            deadman.cancel()
        cleanup("finally")
        if tmp:
            shutil.rmtree(tmp, ignore_errors=True)
        try:
            if STATE_PATH.exists():
                STATE_PATH.unlink()
        except OSError:
            pass
        gone = verify_gone()
        LOG["verify"] = gone
        log("final verify (scoped to our ids only)", **{k: gone[k] for k in ("instance_gone", "volumes_gone", "key_gone")})
        # scrub any IPs from log before write
        text = json.dumps(LOG, default=str, indent=2)
        import re
        text = re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", text)
        LOG_PATH.write_text(text + "\n")


if __name__ == "__main__":
    raise SystemExit(main())
