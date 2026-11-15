#!/usr/bin/env python3
"""Launch (and later delete) a Finnish Verda GPU box for Tasan Extract.

DEFAULT IS DRY-RUN. This script does nothing billed unless you pass --execute
AND set TASAN_VERDA_BUDGET_APPROVED=yes in the environment.

Planned shape (do not treat this as a reservation):
  - 1x 1A100.22V on-demand in FIN-01
  - image 24.04.cuda13.4.docker
  - ~200 GB OS volume, delete permanently on teardown
  - ephemeral SSH key, deleted on teardown
  - startup.sh installs/runs vLLM (Qwen3-32B-AWQ) via docker, bound to 127.0.0.1
  - local deadman timer + remote halt watchdog after N minutes
  - delete ONLY the instance, volume and key this script created; verify those IDs
    are gone. Never wipe other project resources (e.g. a teammate Twin box).

Credentials: VERDA_CLIENT_ID / VERDA_CLIENT_SECRET from env only. Never printed,
logged, or written to disk. Do not copy them onto the instance.

DO NOT RUN THIS SCRIPT against the live API without a written budget approval.
Even a dry-run that called availability was skipped at authoring time.
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
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verda_cloud import call  # noqa: E402

HERE = Path(__file__).resolve().parent
DEFAULT_TYPE = "1A100.22V"
DEFAULT_IMAGE = "24.04.cuda13.4.docker"
DEFAULT_LOCATION = "FIN-01"
DEFAULT_PRICE = 2.386  # USD/h on-demand, from GET /v1/instance-types on 2026-11-14
STORAGE_PER_GIB_MONTH = 0.20
HOSTNAME = "tasan-extract"
STARTUP = HERE / "startup.sh"
RUN_DIR = HERE / ".run"
STATE_PATH = RUN_DIR / "state.json"
STOP_PATH = RUN_DIR / "STOP"
READY_PATH = RUN_DIR / "READY"
# Pre-declared fallback from SPEND.md §6, used only if A100 is out of stock at launch.
CANDIDATES = [
    {"instance_type": "1A100.22V", "location": "FIN-01", "image": "24.04.cuda13.4.docker", "price": 2.386},
    {"instance_type": "1RTXPRO6000.30V.CC", "location": "FIN-03", "image": "24.04.cuda13.4.cc", "price": 2.893},
]

state = {"iid": None, "vols": [], "key": None, "t_create": None, "cleaned": False, "price": DEFAULT_PRICE}
lock = threading.Lock()
LOG = {"events": [], "synthetic_note": "no real patient data on this instance"}


def log(msg, **kw):
    # Never accept raw tokens, secrets or private keys in kw.
    banned = ("client_secret", "api_key", "access_token", "authorization", "private_key")
    safe = {k: v for k, v in kw.items() if not any(b in k.lower() for b in banned)}
    e = {"t": time.strftime("%H:%M:%S"), "msg": msg, **safe}
    LOG["events"].append(e)
    print(json.dumps(e), flush=True)


def worst_cost(price_h: float, life_min: int, vol_gb: int) -> float:
    inst = price_h * life_min / 60
    storage = vol_gb * STORAGE_PER_GIB_MONTH / 730 * (life_min / 60)
    return inst + storage


def write_state(extra=None):
    RUN_DIR.mkdir(mode=0o700, exist_ok=True)
    rec = {
        "iid": state.get("iid"),
        "key_id": state.get("key"),
        "vols": state.get("vols") or [],
        "itype": state.get("itype"),
        "location": state.get("location"),
        "image": state.get("image"),
        "price": state.get("price"),
        "t_create": state.get("t_create"),
        "ssh_key": state.get("ssh_key_path"),
        "known_hosts": state.get("known_hosts"),
        "ip_present": bool(state.get("ip")),
    }
    if extra:
        rec.update(extra)
    # IP is stored only in this 0600 file, never in last_launch_log.json
    if state.get("ip"):
        rec["ip"] = state["ip"]
    STATE_PATH.write_text(json.dumps(rec, indent=2) + "\n")
    STATE_PATH.chmod(0o600)


def cleanup(reason: str) -> None:
    """Delete only resources this process created."""
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
                "action": "delete",
                "id": state["iid"],
                "volume_ids": vols,
                "delete_permanently": True,
            })
            log("delete instance", status=st, n_volumes=len(vols), body=str(b)[:200])
            for _ in range(60):
                st, inst = call("GET", f"/instances/{state['iid']}")
                if st == 404 or (isinstance(inst, dict) and inst.get("status") in ("discontinued", "notfound")):
                    break
                time.sleep(5)
            for v in vols:
                st_v, _ = call("PUT", "/volumes", {"action": "delete", "id": v, "is_permanent": True})
                log("delete volume", status=st_v, vol_prefix=str(v)[:8])
            if state["t_create"]:
                state["life_min"] = round((time.time() - state["t_create"]) / 60, 1)
        if state["key"]:
            st, b = call("DELETE", f"/ssh-keys/{state['key']}")
            # 404 is expected if a teammate already removed project keys.
            log("delete ssh key", status=st, already_gone=(st == 404))
        state["cleaned"] = True


def verify_gone() -> dict:
    """Check that OUR ids are gone. Do not require the project to be empty."""
    out = {"instance_gone": True, "volumes_gone": True, "key_gone": True, "details": {}}
    if state["iid"]:
        st, inst = call("GET", f"/instances/{state['iid']}")
        gone = st == 404 or (isinstance(inst, dict) and inst.get("status") in ("discontinued", "notfound"))
        out["instance_gone"] = bool(gone)
        out["details"]["instance_status"] = st if st == 404 else (inst.get("status") if isinstance(inst, dict) else str(inst)[:80])
    for v in state["vols"]:
        st, body = call("GET", f"/volumes/{v}")
        if st != 404:
            out["volumes_gone"] = False
            out["details"][f"volume_{v[:8]}"] = st
    if state["key"]:
        st, keys = call("GET", "/ssh-keys")
        if isinstance(keys, list) and any(k.get("id") == state["key"] for k in keys):
            out["key_gone"] = False
        else:
            out["key_gone"] = True  # missing from list or 404: already gone
    return out


def ssh(kf, kh, ip, cmd, timeout=900):
    """Run a remote command. Never raise TimeoutExpired — a timeout must not
    tear down the instance via the caller's finally/cleanup path."""
    try:
        return subprocess.run(
            [
                "ssh", "-i", kf, "-o", f"UserKnownHostsFile={kh}",
                "-o", "StrictHostKeyChecking=accept-new",
                "-o", "ConnectTimeout=15", "-o", "BatchMode=yes",
                "-o", "RequestTTY=no",
                "-o", "ServerAliveInterval=5",
                "-o", "ServerAliveCountMax=3",
                "-o", "LogLevel=ERROR",
                f"root@{ip}", cmd,
            ],
            stdin=subprocess.DEVNULL,
            capture_output=True, text=True, timeout=timeout,
        )
    except subprocess.TimeoutExpired as e:
        out = e.stdout or ""
        err = e.stderr or ""
        if isinstance(out, bytes):
            out = out.decode(errors="replace")
        if isinstance(err, bytes):
            err = err.decode(errors="replace")
        return subprocess.CompletedProcess(e.cmd, -1, out, err + "\nTIMEOUT")


def plan_dict(args) -> dict:
    return {
        "dry_run": not args.execute,
        "instance_type": args.instance_type,
        "location_code": args.location,
        "is_spot": False,
        "contract": "PAY_AS_YOU_GO",
        "image": args.image,
        "os_volume_gb": args.volume_gb,
        "hostname": HOSTNAME,
        "model": args.model,
        "watchdog_min": args.watchdog_min,
        "price_usd_per_h_list": args.price,
        "est_worst_usd": round(worst_cost(args.price, args.watchdog_min, args.volume_gb), 2),
        "cap_usd": args.cap,
        "notes": [
            "On-demand 1A100.22V in FIN-01. Re-check availability immediately before --execute.",
            "Cleanup is scoped to IDs this script creates; other project instances are left alone.",
            "vLLM is bound to 127.0.0.1 on the instance; use SSH -L 8000:127.0.0.1:8000.",
            "Remote watchdog issues shutdown -h; the launcher must still API-delete (billing may continue until delete).",
            "Do not upload real patient notes. Corpus is SYNTHETIC.",
        ],
    }


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--execute", action="store_true", help="actually create (also needs TASAN_VERDA_BUDGET_APPROVED=yes)")
    ap.add_argument("--instance-type", default=DEFAULT_TYPE)
    ap.add_argument("--image", default=DEFAULT_IMAGE)
    ap.add_argument("--location", default=DEFAULT_LOCATION)
    ap.add_argument("--volume-gb", type=int, default=200)
    ap.add_argument("--watchdog-min", type=int, default=150)
    ap.add_argument("--price", type=float, default=DEFAULT_PRICE, help="list USD/h used for the cap check")
    ap.add_argument("--cap", type=float, default=10.0, help="refuse to start if worst-case exceeds this")
    ap.add_argument("--model", default="Qwen/Qwen3-32B-AWQ")
    ap.add_argument("--no-fallback", action="store_true", help="do not use the pre-declared FIN-03 RTX PRO 6000 CC fallback")
    args = ap.parse_args()

    plan = plan_dict(args)
    print(json.dumps(plan, indent=2))

    if not args.execute:
        print("dry-run only. Nothing was created. To launch, re-read EXTRACT_PLAN.md, "
              "re-check availability, then pass --execute with TASAN_VERDA_BUDGET_APPROVED=yes.")
        return 0
    if os.environ.get("TASAN_VERDA_BUDGET_APPROVED") != "yes":
        print("refusing: --execute requires env TASAN_VERDA_BUDGET_APPROVED=yes", file=sys.stderr)
        return 2
    if plan["est_worst_usd"] > args.cap + 1e-9:
        print(f"refusing: worst-case ${plan['est_worst_usd']} exceeds cap ${args.cap}", file=sys.stderr)
        return 2
    for k in ("VERDA_CLIENT_ID", "VERDA_CLIENT_SECRET"):
        if not os.environ.get(k):
            print(f"refusing: {k} is not set", file=sys.stderr)
            return 2
    if not STARTUP.is_file():
        print("refusing: startup.sh missing", file=sys.stderr)
        return 2

    # Pick the first on-demand candidate that is actually in stock (A100 first).
    wanted = {"instance_type": args.instance_type, "location": args.location, "image": args.image, "price": args.price}
    chain = [wanted] + [c for c in CANDIDATES if not args.no_fallback and c["instance_type"] != wanted["instance_type"]]
    chosen = None
    for c in chain:
        st, av = call("GET", f"/instance-availability/{c['instance_type']}?is_spot=false&location_code={c['location']}")
        log("availability", status=st, available=av, instance_type=c["instance_type"], location=c["location"])
        if av is True:
            worst = worst_cost(c["price"], args.watchdog_min, args.volume_gb)
            if worst > args.cap + 1e-9:
                log("skip type over cap", instance_type=c["instance_type"], worst=round(worst, 2))
                continue
            chosen = c
            break
    if not chosen:
        print("refusing: no in-cap on-demand candidate is in stock", file=sys.stderr)
        return 3
    args.instance_type = chosen["instance_type"]
    args.location = chosen["location"]
    args.image = chosen["image"]
    args.price = chosen["price"]
    log("chosen", instance_type=args.instance_type, location=args.location, image=args.image, price=args.price)

    tmp = tempfile.mkdtemp(prefix="tasan_extract_")
    os.chmod(tmp, 0o700)
    kf, kh = f"{tmp}/k", f"{tmp}/known_hosts"
    deadman = None
    try:
        subprocess.run(["ssh-keygen", "-q", "-t", "ed25519", "-N", "", "-C", "tasan-extract-ephemeral", "-f", kf], check=True)
        pub = Path(kf + ".pub").read_text().strip()
        st, kid = call("POST", "/ssh-keys", {"name": "tasan-extract-ephemeral", "key": pub})
        if st not in (200, 201, 202):
            log("ssh key add failed", status=st, body=str(kid)[:200])
            return 1
        state["key"] = kid if isinstance(kid, str) else (kid.get("id") if isinstance(kid, dict) else None)
        log("ssh key added")

        RUN_DIR.mkdir(mode=0o700, exist_ok=True)
        subprocess.run(["cp", kf, str(RUN_DIR / "id_ed25519")], check=True)
        subprocess.run(["cp", kf + ".pub", str(RUN_DIR / "id_ed25519.pub")], check=True)
        os.chmod(RUN_DIR / "id_ed25519", 0o600)
        state["ssh_key_path"] = str(RUN_DIR / "id_ed25519")
        state["known_hosts"] = str(RUN_DIR / "known_hosts")
        state["itype"] = args.instance_type
        state["location"] = args.location
        state["image"] = args.image

        def deploy(with_contract: bool):
            payload = {
                "instance_type": args.instance_type,
                "image": args.image,
                "ssh_key_ids": [state["key"]],
                "hostname": HOSTNAME,
                "description": "Tasan Extract vLLM — auto-deleted, SYNTHETIC eval only",
                "location_code": args.location,
                "is_spot": False,
                "os_volume": {"name": "tasan-extract-os", "size": args.volume_gb},
                "tags": [{"key": "project", "value": "tasan-extract"}],
            }
            if with_contract:
                payload["contract"] = "PAY_AS_YOU_GO"
            return call("POST", "/instances", payload)

        st, iid = deploy(True)
        log("deploy", status=st, body=str(iid)[:240], contract="PAY_AS_YOU_GO")
        if st not in (200, 201, 202):
            log("retry deploy without contract field")
            st, iid = deploy(False)
            log("deploy", status=st, body=str(iid)[:240], contract=None)
        if st not in (200, 201, 202):
            return 1
        # API may return a raw id or an object
        if isinstance(iid, str):
            state["iid"] = iid
        elif isinstance(iid, dict):
            state["iid"] = iid.get("id") or iid.get("instance_id")
        else:
            log("unexpected deploy body")
            return 1
        state["t_create"] = time.time()
        state["price"] = args.price

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
        # Persist known_hosts after first ssh

        ssh_ready = False
        for i in range(60):  # up to ~10 min for cloud-init / sshd
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

        scp_ok = False
        for i in range(8):
            try:
                scp = subprocess.run(
                    ["scp", "-i", kf, "-o", f"UserKnownHostsFile={kh}",
                     "-o", "BatchMode=yes", "-o", "ConnectTimeout=15",
                     "-o", "LogLevel=ERROR",
                     str(STARTUP), f"root@{ip}:/root/startup.sh"],
                    stdin=subprocess.DEVNULL, capture_output=True, text=True, timeout=60,
                )
            except subprocess.TimeoutExpired:
                log("scp timeout", attempt=i)
                time.sleep(5)
                continue
            if scp.returncode == 0:
                scp_ok = True
                break
            log("scp failed", attempt=i, rc=scp.returncode, stderr=(scp.stderr or "")[-200:])
            time.sleep(5)
        if not scp_ok:
            log("scp never succeeded")
            return 1

        # Detach with setsid so the SSH session can exit immediately.
        # Previous nohup attempts still held the session and a timeout in ssh()
        # used to abort the launcher, which then deleted the instance in finally.
        remote = (
            "chmod +x /root/startup.sh && "
            "if [ ! -f /root/startup.pid ] || ! kill -0 $(cat /root/startup.pid) 2>/dev/null; then "
            f"TASAN_MODEL={args.model} TASAN_WATCHDOG_MIN={args.watchdog_min} "
            "setsid /root/startup.sh </dev/null >/root/startup.stdout 2>/root/startup.stderr & "
            "echo $! > /root/startup.pid; "
            "fi; echo STARTUP_DISPATCHED"
        )
        dispatched = False
        for i in range(8):
            r = ssh(kf, kh, ip, remote, 45)
            if r.returncode == 0 and "STARTUP_DISPATCHED" in (r.stdout or ""):
                dispatched = True
                log("startup dispatched", attempt=i, rc=r.returncode)
                break
            log("startup dispatch retry", attempt=i, rc=r.returncode, stderr=(r.stderr or "")[-200:])
            time.sleep(8)
        if not dispatched:
            log("startup dispatch failed")
            return 1
        log("startup running in background; waiting for READY or STOP or watchdog")
        STOP_PATH.unlink(missing_ok=True)
        READY_PATH.unlink(missing_ok=True)
        write_state({"startup": "dispatched"})
        # Stay attached until STOP file, watchdog, or the instance vanishes.
        while True:
            if STOP_PATH.exists():
                log("stop file seen; will delete our resources")
                break
            # Poll remote ready marker
            rdy = ssh(kf, kh, ip, "test -f /root/tasan-vllm.ready && cat /root/tasan-vllm.ready", 20)
            if rdy.returncode == 0 and (rdy.stdout or "").strip():
                if not READY_PATH.exists():
                    READY_PATH.write_text((rdy.stdout or "").strip() + "\n")
                    log("vllm ready")
            st, inst = call("GET", f"/instances/{state['iid']}")
            s = inst.get("status") if isinstance(inst, dict) else None
            if st == 404 or s in ("discontinued", "error"):
                log("instance already gone while waiting", status=st, inst_status=s)
                break
            time.sleep(20)
    except KeyboardInterrupt:
        log("interrupted by user")
        return 1
    finally:
        if deadman:
            deadman.cancel()
        cleanup("finally")
        shutil.rmtree(tmp, ignore_errors=True)
        # Drop the 0600 state (contains IP) after teardown.
        try:
            if STATE_PATH.exists():
                STATE_PATH.unlink()
        except OSError:
            pass
        gone = verify_gone()
        LOG["verify"] = gone
        log("final verify (scoped to our ids only)", **{k: gone[k] for k in ("instance_gone", "volumes_gone", "key_gone")})
        out = HERE / "last_launch_log.json"
        # The log must not contain IPs, keys, or tokens.
        out.write_text(json.dumps(LOG, indent=2) + "\n")
    return 0 if LOG.get("verify", {}).get("instance_gone") else 1


if __name__ == "__main__":
    sys.exit(main())
