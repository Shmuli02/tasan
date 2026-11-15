#!/usr/bin/env python3
"""SSH / tunnel helpers. Never prints the instance IP or key material."""
from __future__ import annotations

import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

RUN = Path(__file__).resolve().parent / ".run"
KEY = RUN / "id_ed25519"
STATE = RUN / "state.json"
KNOWN = Path("/tmp/tasan_extract_known_hosts")
TUNNEL_PID = RUN / "tunnel.pid"


def _ip() -> str:
    st = json.loads(STATE.read_text())
    ip = st.get("ip")
    if not ip:
        raise SystemExit("no ip in state.json")
    return ip


def _ssh_base() -> list[str]:
    return [
        "ssh", "-i", str(KEY),
        "-o", f"UserKnownHostsFile={KNOWN}",
        "-o", "StrictHostKeyChecking=accept-new",
        "-o", "ConnectTimeout=15",
        "-o", "BatchMode=yes",
        "-o", "RequestTTY=no",
        "-o", "ServerAliveInterval=15",
        "-o", "ServerAliveCountMax=4",
        "-o", "LogLevel=ERROR",
        f"root@{_ip()}",
    ]


def redact(s: str) -> str:
    return re.sub(r"\b(?:\d{1,3}\.){3}\d{1,3}\b", "<ip>", s or "")


def ssh(cmd: str, timeout: int = 60) -> subprocess.CompletedProcess:
    return subprocess.run(
        _ssh_base() + [cmd],
        stdin=subprocess.DEVNULL,
        capture_output=True, text=True, timeout=timeout,
    )


def start_tunnel(local_port: int = 8000) -> int:
    if TUNNEL_PID.exists():
        try:
            pid = int(TUNNEL_PID.read_text().strip())
            os.kill(pid, 0)
            return pid
        except (OSError, ValueError):
            pass
    proc = subprocess.Popen(
        [
            "ssh", "-i", str(KEY), "-N",
            "-L", f"{local_port}:127.0.0.1:8000",
            "-o", f"UserKnownHostsFile={KNOWN}",
            "-o", "StrictHostKeyChecking=accept-new",
            "-o", "ConnectTimeout=15",
            "-o", "BatchMode=yes",
            "-o", "ExitOnForwardFailure=yes",
            "-o", "ServerAliveInterval=15",
            "-o", "ServerAliveCountMax=4",
            "-o", "LogLevel=ERROR",
            f"root@{_ip()}",
        ],
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    time.sleep(1)
    if proc.poll() is not None:
        raise SystemExit(f"tunnel exited immediately rc={proc.returncode}")
    TUNNEL_PID.write_text(str(proc.pid) + "\n")
    return proc.pid


def stop_tunnel() -> None:
    if not TUNNEL_PID.exists():
        return
    try:
        pid = int(TUNNEL_PID.read_text().strip())
        os.kill(pid, 15)
    except (OSError, ValueError):
        pass
    TUNNEL_PID.unlink(missing_ok=True)


def main() -> int:
    if len(sys.argv) < 2:
        print("usage: remote.py ssh <cmd> | tunnel-start | tunnel-stop | health")
        return 2
    op = sys.argv[1]
    if op == "ssh":
        r = ssh(" ".join(sys.argv[2:]), timeout=120)
        sys.stdout.write(redact(r.stdout))
        sys.stderr.write(redact(r.stderr))
        return r.returncode
    if op == "tunnel-start":
        pid = start_tunnel()
        print(f"tunnel pid {pid}  localhost:8000 -> remote 127.0.0.1:8000")
        return 0
    if op == "tunnel-stop":
        stop_tunnel()
        print("tunnel stopped")
        return 0
    if op == "health":
        r = ssh("curl -sf http://127.0.0.1:8000/v1/models && echo && cat /root/tasan-vllm.ready 2>/dev/null || echo NOT_READY; nvidia-smi --query-gpu=memory.used,memory.total,utilization.gpu --format=csv,noheader", 30)
        sys.stdout.write(redact(r.stdout + r.stderr))
        return 0 if "NOT_READY" not in (r.stdout or "") and r.returncode == 0 else 1
    return 2


if __name__ == "__main__":
    raise SystemExit(main())
