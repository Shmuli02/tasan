#!/usr/bin/env python3
"""Create the cheapest on-demand FIN CPU box and serve the Ask Tasan HTTPS proxy.
Credentials stay in memory / instance env. Never print, log or write keys."""
from __future__ import annotations

import json, os, stat, subprocess, sys, time
from datetime import datetime, timedelta, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent
RUN = ROOT / ".run"
SIM_API = Path("/workspace/junction-new/sim/deploy/verda")
sys.path.insert(0, str(SIM_API))
from verda_api import call  # noqa: E402

HOST = "tasan-ask"
TYPES = [("CPU.4V.16G", "24.04.base", 0.048), ("CPU-TURIN.4V.16G", "24.04.base", 0.048)]
LOCS = ["FIN-01", "FIN-02", "FIN-03"]
HELSINKI = timezone(timedelta(hours=2))  # EET / UTC+2 on 14-15 Nov 2026
CAP = 25.0

def log(msg, **kv):
    safe = {k: v for k, v in kv.items() if "key" not in k.lower() and "secret" not in k.lower() and "token" not in k.lower()}
    extra = (" " + json.dumps(safe, default=str)) if safe else ""
    print(f"[{time.strftime('%H:%M:%S')}] {msg}{extra}", flush=True)

def need_env():
    missing = [n for n in ("VERDA_CLIENT_ID", "VERDA_CLIENT_SECRET", "VERDA_API_KEY") if not os.environ.get(n)]
    if missing:
        log("missing env names", names=missing)
        sys.exit(1)
    log("env present", names=["VERDA_CLIENT_ID", "VERDA_CLIENT_SECRET", "VERDA_API_KEY"])

def ssh_cmd(kf, ip, cmd, timeout=60, stdin=None):
    return subprocess.run(
        ["ssh", "-i", kf, "-o", "UserKnownHostsFile=" + str(RUN / "known_hosts"),
         "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes",
         "-o", "ConnectTimeout=10", f"root@{ip}", cmd],
        input=stdin, text=True if isinstance(stdin, str) or stdin is None else False,
        capture_output=True, timeout=timeout,
    )

def scp(kf, ip, src, dst):
    return subprocess.run(
        ["scp", "-i", kf, "-o", "UserKnownHostsFile=" + str(RUN / "known_hosts"),
         "-o", "StrictHostKeyChecking=accept-new", "-o", "BatchMode=yes",
         str(src), f"root@{ip}:{dst}"],
        capture_output=True, text=True, timeout=60,
    )

def load_state():
    sp = RUN / "state.json"
    if sp.exists():
        return json.loads(sp.read_text())
    return {}

def save_state(state):
    RUN.mkdir(parents=True, exist_ok=True)
    # never persist keys
    clean = {k: v for k, v in state.items() if "key_material" not in k and "api_key" not in k and "secret" not in k}
    (RUN / "state.json").write_text(json.dumps(clean, indent=2) + "\n")

def existing_ours(state):
    iid = state.get("iid")
    if not iid:
        return None
    st, inst = call("GET", f"/instances/{iid}")
    if st == 200 and isinstance(inst, dict) and inst.get("status") in ("running", "starting", "pending"):
        return inst
    return None

def pick_type():
    for itype, image, price in TYPES:
        for loc in LOCS:
            st, av = call("GET", f"/instance-availability/{itype}?is_spot=false&location_code={loc}")
            available = av is True or (isinstance(av, dict) and (av.get("available") or av.get("is_available") or av is True))
            # API sometimes returns raw true or {"status":...}
            if av is True or (isinstance(av, str) and "true" in av.lower()):
                available = True
            if isinstance(av, dict):
                available = bool(av.get("available") or av.get("is_available") or av.get("in_stock"))
            log("availability", status=st, instance_type=itype, location=loc, available=available, raw=str(av)[:160])
            if st in (200, 201) and (av is True or available):
                return itype, image, price, loc
    return None

def create_ssh_key():
    RUN.mkdir(parents=True, exist_ok=True)
    kf = RUN / "id_ed25519"
    if not kf.exists():
        subprocess.check_call(["ssh-keygen", "-t", "ed25519", "-N", "", "-f", str(kf), "-q"])
        kf.chmod(stat.S_IRUSR | stat.S_IWUSR)
    pub = (RUN / "id_ed25519.pub").read_text().strip()
    st, kid = call("POST", "/ssh-keys", {"name": f"{HOST}-ephemeral", "key": pub})
    if st not in (200, 201, 202):
        log("ssh key add failed", status=st, body=str(kid)[:200])
        sys.exit(1)
    key_id = kid if isinstance(kid, str) else (kid.get("id") if isinstance(kid, dict) else None)
    if not key_id:
        log("ssh key id missing", body=str(kid)[:200])
        sys.exit(1)
    return str(kf), key_id

def deploy_instance(itype, image, price, loc, key_id):
    payload = {
        "instance_type": itype,
        "image": image,
        "ssh_key_ids": [key_id],
        "hostname": HOST,
        "description": "Tasan Ask HTTPS proxy (on-demand; keep through Sun 15:00 Europe/Helsinki)",
        "location_code": loc,
        "is_spot": False,
        "os_volume": {"name": f"{HOST}-os", "size": 30},
        "tags": [{"key": "project", "value": "tasan-ask"}],
    }
    st, iid = call("POST", "/instances", {**payload, "contract": "PAY_AS_YOU_GO"})
    log("deploy attempt", status=st, body=str(iid)[:240], contract="PAY_AS_YOU_GO", instance_type=itype, location=loc)
    if st not in (200, 201, 202):
        st, iid = call("POST", "/instances", payload)
        log("deploy retry no contract", status=st, body=str(iid)[:240])
    ident = iid if isinstance(iid, str) else (iid.get("id") if isinstance(iid, dict) else None)
    if st not in (200, 201, 202) or not ident:
        log("deploy failed")
        sys.exit(1)
    return ident, price

def wait_running(iid):
    ip = None
    inst = None
    for i in range(60):
        st, inst = call("GET", f"/instances/{iid}")
        s = inst.get("status") if isinstance(inst, dict) else None
        ip = inst.get("ip") if isinstance(inst, dict) else None
        log("wait", n=i, status=s, has_ip=bool(ip))
        if s == "running" and ip:
            return ip, inst
        if s in ("error", "no_capacity", "installation_failed", "discontinued"):
            log("instance failed", inst_status=s)
            sys.exit(1)
        time.sleep(10)
    log("timeout waiting for instance")
    sys.exit(1)

def wait_ssh(kf, ip):
    for i in range(36):
        try:
            r = ssh_cmd(kf, ip, "true", timeout=20)
            if r.returncode == 0:
                return
        except subprocess.TimeoutExpired:
            pass
        log("ssh wait", n=i)
        time.sleep(10)
    log("ssh never came up")
    sys.exit(1)

def provision(kf, ip):
    # packages
    r = ssh_cmd(kf, ip, "bash -s", timeout=300, stdin=r"""set -euo pipefail
export DEBIAN_FRONTEND=noninteractive
apt-get update -y
apt-get install -y --no-install-recommends ca-certificates curl debian-keyring debian-archive-keyring apt-transport-https nodejs
# Caddy official repo
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' > /etc/apt/sources.list.d/caddy-stable.list
apt-get update -y
apt-get install -y caddy
node --version
caddy version
mkdir -p /opt/tasan-ask
""")
    log("apt", rc=r.returncode, tail=(r.stdout or "")[-400:], err=(r.stderr or "")[-400:])
    if r.returncode != 0:
        sys.exit(1)
    # upload proxy + facts (no secrets)
    for src, dst in ((ROOT / "proxy.mjs", "/opt/tasan-ask/proxy.mjs"), (ROOT / "facts.json", "/opt/tasan-ask/facts.json")):
        if not src.exists():
            log("missing file", path=str(src))
            sys.exit(1)
        rr = scp(kf, ip, src, dst)
        log("scp", dst=dst, rc=rr.returncode, err=(rr.stderr or "")[-200:])
        if rr.returncode != 0:
            sys.exit(1)
    # write env via stdin so the key never appears in ps / ssh argv. Do not print remote output.
    key = os.environ["VERDA_API_KEY"]
    env_body = (
        "VERDA_MODEL=kimi-k3-1-pro\n"
        "VERDA_BASE_URL=https://inference.verda.com/v1\n"
        "TASAN_BIND=127.0.0.1\n"
        "PORT=8787\n"
        f"VERDA_API_KEY={key}\n"
    )
    r = ssh_cmd(
        kf, ip,
        "umask 077 && cat > /etc/tasan-proxy.env && chmod 600 /etc/tasan-proxy.env && test -s /etc/tasan-proxy.env && echo env_ok",
        timeout=30, stdin=env_body,
    )
    # only accept the literal env_ok, never echo stdout if it somehow leaked
    ok = (r.returncode == 0 and (r.stdout or "").strip().endswith("env_ok"))
    log("env file", ok=ok, rc=r.returncode)
    if not ok:
        sys.exit(1)
    # systemd + caddy
    hyphen = ip.replace(".", "-")
    host = f"{hyphen}.sslip.io"
    unit = """[Unit]
Description=Tasan Ask proxy
After=network.target
[Service]
Type=simple
EnvironmentFile=/etc/tasan-proxy.env
WorkingDirectory=/opt/tasan-ask
ExecStart=/usr/bin/node /opt/tasan-ask/proxy.mjs
Restart=always
RestartSec=3
[Install]
WantedBy=multi-user.target
"""
    caddy = f"""{host} {{
  encode gzip
  reverse_proxy 127.0.0.1:8787
}}
"""
    r = ssh_cmd(kf, ip, "bash -s", timeout=90, stdin=f"""set -euo pipefail
cat > /etc/systemd/system/tasan-ask.service << 'UNIT'
{unit}UNIT
cat > /etc/caddy/Caddyfile << 'CADDY'
{caddy}CADDY
systemctl daemon-reload
systemctl enable --now tasan-ask
systemctl restart caddy
systemctl is-active tasan-ask
""")
    log("services", rc=r.returncode, out=(r.stdout or "")[-300:], err=(r.stderr or "")[-300:])
    if r.returncode != 0:
        sys.exit(1)
    return f"https://{host}"

def wait_https(url):
    for i in range(24):
        try:
            r = subprocess.run(["curl", "-fsS", "--max-time", "20", f"{url}/health"], capture_output=True, text=True, timeout=25)
            log("health", n=i, rc=r.returncode, body=(r.stdout or "")[:200], err=(r.stderr or "")[-160:])
            if r.returncode == 0 and '"ok":true' in r.stdout.replace(" ", ""):
                return r.stdout
        except subprocess.TimeoutExpired:
            log("health timeout", n=i)
        time.sleep(10)
    log("https health failed")
    sys.exit(1)

def write_spend(state):
    start = state["start_helsinki"]
    rate = state["price"]
    # prepaid 10-min increments
    hours = max((time.time() - state["t_create"]) / 3600, 10 / 60)
    # bill rounded up to 10 minutes
    tenths = int((time.time() - state["t_create"] + 599) // 600)
    inst_cost = tenths * (rate / 6)
    md = f"""# Ask Tasan / Verda spend

All figures are USD. No credentials are recorded here.

- Instance ID: `{state["iid"]}`
- Hostname: `{HOST}`
- Type: `{state["itype"]}` on-demand in `{state["location"]}`
- Hourly rate: `${rate:.5f}` (billed in prepaid 10-minute increments)
- Started: {start} Europe/Helsinki
- Proxy URL: {state["proxy_url"]}
- Model: kimi-k3-1-pro (EU-hosted inference · Verda). Do not describe this as Finland-hosted.
- Keep the instance up through judging Sunday 12:00–15:00 Europe/Helsinki. Delete via the Verda API after the demo window; `shutdown -h` may not stop billing.
- Cap: $25.00

## Running total

| Item | Estimate |
|---|---|
| CPU instance so far (10-min increments) | ${inst_cost:.4f} |
| Inference tokens (updated after the trick suite) | see later rows |
| **Running total** | **${inst_cost:.4f}** |

Updated {datetime.now(HELSINKI).strftime("%Y-%m-%d %H:%M")} Europe/Helsinki.
"""
    (ROOT / "SPEND.md").write_text(md)
    log("wrote SPEND.md", instance_cost=round(inst_cost, 4), rate=rate)

def main():
    need_env()
    RUN.mkdir(parents=True, exist_ok=True)
    state = load_state()
    inst = existing_ours(state)
    kf = str(RUN / "id_ed25519")
    if inst:
        ip = inst["ip"]
        log("reusing instance", iid=state.get("iid"), status=inst.get("status"))
        if not Path(kf).exists():
            log("missing ssh key for reuse")
            sys.exit(1)
        wait_ssh(kf, ip)
        url = provision(kf, ip)
        wait_https(url)
        state["proxy_url"] = url
        state["ip_set"] = True
        save_state(state)
        write_spend(state)
        print(f"PROXY_URL={url}")
        print(f"INSTANCE_ID={state['iid']}")
        return 0

    # leftover check: list instances, do not modify others
    st, listing = call("GET", "/instances")
    items = listing if isinstance(listing, list) else (listing.get("instances") or listing.get("data") or []) if isinstance(listing, dict) else []
    others = []
    for it in items or []:
        if isinstance(it, dict):
            others.append({"hostname": it.get("hostname"), "type": it.get("instance_type"), "status": it.get("status")})
    log("existing project instances (left untouched)", others=others)

    chosen = pick_type()
    if not chosen:
        log("no CPU.4V.16G-class capacity")
        sys.exit(1)
    itype, image, price, loc = chosen
    log("chosen", instance_type=itype, image=image, price=price, location=loc)
    kf, key_id = create_ssh_key()
    state["key"] = key_id
    iid, price = deploy_instance(itype, image, price, loc, key_id)
    t0 = time.time()
    start = datetime.now(HELSINKI).strftime("%Y-%m-%d %H:%M")
    state.update(iid=iid, itype=itype, location=loc, price=price, t_create=t0, start_helsinki=start, image=image)
    save_state(state)
    ip, inst = wait_running(iid)
    state["has_ip"] = True
    save_state(state)
    wait_ssh(kf, ip)
    url = provision(kf, ip)
    health = wait_https(url)
    state["proxy_url"] = url
    save_state(state)
    write_spend(state)
    print(f"PROXY_URL={url}")
    print(f"INSTANCE_ID={iid}")
    print(f"HEALTH={health.strip()[:200]}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
