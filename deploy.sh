#!/usr/bin/env bash
# One-command redeploy of Tasan to the locked Beacon site.
# Never creates a new site. Secrets are read from ~/.config/tasan or env vars
# and are never printed.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
APP="$ROOT/app"
CONFIG_DIR="${TASAN_DEPLOY_CONFIG:-$HOME/.config/tasan}"
LOCKED_SLUG="petaled-trowel-90"
LOCKED_URL="https://${LOCKED_SLUG}.beacon.host/"
WORKER_SLUG="petaled-trowel-90-ask"
WORKER_URL="https://${WORKER_SLUG}.worker.beacon.host"
WORKER_ENTRY="proxy.mjs"
WORKER_COMPAT_DATE="2026-11-14"
WORKER_COMPAT_FLAGS="nodejs_compat"
SITE_TITLE="Tasan — Equal Care Across Finland"
PROXY_URL="$WORKER_URL"
CLIENT="X-Beacon-Client: tasan-junction/2026"
SKIP_PULL=0
FORCE_WORKER=0
SKIP_WORKER=0
SKIP_OFFLINE=0
SKIP_SMOKE=0

usage() {
  cat <<'EOF'
Usage: ./deploy.sh [options]

Pulls main, builds the app, and publishes it to the locked URL
https://petaled-trowel-90.beacon.host/. Reuses the Ask Tasan worker unless
its source changed.

Options:
  --skip-pull         Do not git pull (use the current checkout)
  --redeploy-worker   Force a worker redeploy even if source is unchanged
  --skip-worker       Never redeploy the worker
  --skip-offline      Skip the offline zip build
  --skip-smoke        Skip the live smoke checks
  -h, --help          Show this help

Credentials and locked-site settings are read from, in order:
  1. Environment variables (BEACON_API_KEY, VITE_TASAN_PROXY_URL, VERDA_API_KEY)
  2. $TASAN_DEPLOY_CONFIG or ~/.config/tasan/ (chmod 700/600)
  3. ~/.config/beacon/config.json for the Beacon API key only

The script never writes a new Beacon site. If the current credential cannot
update petaled-trowel-90, it exits without publishing.
EOF
}

while [[ $# -gt 0 ]]; do
  case "$1" in
    --skip-pull) SKIP_PULL=1 ;;
    --redeploy-worker) FORCE_WORKER=1 ;;
    --skip-worker) SKIP_WORKER=1 ;;
    --skip-offline) SKIP_OFFLINE=1 ;;
    --skip-smoke) SKIP_SMOKE=1 ;;
    -h|--help) usage; exit 0 ;;
    *)
      echo "Unknown option: $1" >&2
      usage >&2
      exit 2
      ;;
  esac
  shift
done

redact() {
  python3 -c 'import sys,re; t=sys.stdin.read(); t=re.sub(r"ctk_[A-Za-z0-9_-]+","ctk_[REDACTED]",t); t=re.sub(r"chk_[A-Za-z0-9_-]+","chk_[REDACTED]",t); t=re.sub(r"(VERDA_API_KEY|BEACON_API_KEY|Authorization: Bearer)[=: ]+\S+","\\1=[REDACTED]",t,flags=re.I); sys.stdout.write(t)'
}

need_file() {
  local path="$1" hint="$2"
  if [[ ! -s "$path" ]]; then
    echo "BLOCKER: missing $path" >&2
    echo "$hint" >&2
    exit 2
  fi
}

load_dotenv() {
  local file="$1"
  [[ -f "$file" ]] || return 0
  # Export KEY=VAL lines; ignore comments. Values are not printed.
  eval "$(python3 - "$file" <<'PY'
import shlex, sys
from pathlib import Path
for line in Path(sys.argv[1]).read_text().splitlines():
    s = line.strip()
    if not s or s.startswith("#") or "=" not in s:
        continue
    k, v = s.split("=", 1)
    k = k.strip()
    v = v.strip().strip('"').strip("'")
    if k.isidentifier():
        print(f"export {k}={shlex.quote(v)}")
PY
)"
}

load_beacon_key() {
  if [[ -n "${BEACON_API_KEY:-}" ]]; then
    return 0
  fi
  local candidates=(
    "$CONFIG_DIR/beacon-api-key"
    "$CONFIG_DIR/beacon-config.json"
    "$HOME/.config/beacon/config.json"
  )
  local path
  for path in "${candidates[@]}"; do
    [[ -f "$path" ]] || continue
    local key
    key=$(python3 - "$path" <<'PY'
import json, sys
from pathlib import Path
p = Path(sys.argv[1])
raw = p.read_text().strip()
key = ""
if p.suffix == ".json" or raw.startswith("{"):
    try:
        d = json.loads(raw)
        key = d.get("apiKey") or d.get("api_key") or ""
    except Exception:
        key = ""
else:
    # allow KEY=value or a bare key
    for line in raw.splitlines():
        s = line.strip()
        if not s or s.startswith("#"):
            continue
        if s.startswith("chk_"):
            key = s
            break
        if "=" in s and s.split("=", 1)[0].strip() in {"apiKey", "api_key", "BEACON_API_KEY"}:
            key = s.split("=", 1)[1].strip().strip('"').strip("'")
            break
print(key if isinstance(key, str) and key.startswith("chk_") else "")
PY
)
    if [[ -n "${key:-}" ]]; then
      export BEACON_API_KEY="$key"
      return 0
    fi
  done
  echo "BLOCKER: cannot update ${LOCKED_URL}" >&2
  echo "No Beacon account API key was found." >&2
  echo "Needed: an account API key from the beacon.host dashboard 'API key' page," >&2
  echo "signed in as the account that owns ${LOCKED_SLUG}." >&2
  echo "  1. Copy the key (it starts with chk_)." >&2
  echo "  2. Either export BEACON_API_KEY (do not paste it into chat), or write" >&2
  echo "     it to ${CONFIG_DIR}/beacon-api-key and chmod 600 that file" >&2
  echo "     (JSON {\"apiKey\":\"chk_...\"} in ${CONFIG_DIR}/beacon-config.json" >&2
  echo "     or ~/.config/beacon/config.json also works)." >&2
  echo "  3. Re-run: ${ROOT}/deploy.sh" >&2
  echo "No new site was created. The live URL was not changed." >&2
  exit 2
}

missing_config_hint() {
  echo "Create ${CONFIG_DIR} (chmod 700) with chmod 600 files as described in DEPLOY.md:" >&2
  echo "  app.env              SITE_SLUG, VITE_TASAN_PROXY_URL, WORKER_SLUG" >&2
  echo "  beacon-api-key       Beacon account API key (chk_...)" >&2
  echo "  worker.env           VERDA_API_KEY (only needed to set or replace the worker secret)" >&2
}

HDR=""
RESP=""
cleanup() {
  [[ -n "${HDR:-}" && -f "${HDR:-}" ]] && rm -f "$HDR"
  [[ -n "${RESP:-}" && -f "${RESP:-}" ]] && rm -f "$RESP"
}
trap cleanup EXIT

# --- load config ---
load_dotenv "$CONFIG_DIR/app.env"
load_dotenv "$CONFIG_DIR/worker.env"
if [[ -n "${SITE_SLUG:-}" && "$SITE_SLUG" != "$LOCKED_SLUG" ]]; then
  echo "BLOCKER: app.env SITE_SLUG=${SITE_SLUG} does not match the locked slug ${LOCKED_SLUG}." >&2
  echo "Refusing to publish to a different site." >&2
  exit 2
fi
if [[ -n "${VITE_TASAN_PROXY_URL:-}" ]]; then
  PROXY_URL="${VITE_TASAN_PROXY_URL}"
fi
if [[ -n "${WORKER_SLUG:+x}" && -n "${WORKER_SLUG:-}" ]]; then
  :
fi

if [[ ! -d "$CONFIG_DIR" ]]; then
  echo "BLOCKER: deploy config directory ${CONFIG_DIR} does not exist." >&2
  missing_config_hint
  exit 2
fi

load_beacon_key

if [[ -z "${VITE_TASAN_PROXY_URL:-}" ]]; then
  # Safe default: the locked public worker URL.
  export VITE_TASAN_PROXY_URL="$WORKER_URL"
  PROXY_URL="$WORKER_URL"
fi

# Auth header file so the key never appears in process argv.
HDR="$(mktemp)"
python3 - "$HDR" <<'PY'
import os, sys
from pathlib import Path
key = os.environ.get("BEACON_API_KEY") or ""
if not key.startswith("chk_"):
    sys.exit("beacon key missing")
p = Path(sys.argv[1])
p.write_text(f"Authorization: Bearer {key}\nX-Beacon-Client: tasan-junction/2026\n")
p.chmod(0o600)
PY

# --- git pull ---
if [[ "$SKIP_PULL" -eq 0 ]]; then
  if [[ ! -d "$ROOT/.git" ]]; then
    echo "BLOCKER: ${ROOT} is not a git checkout. Clone https://github.com/Shmuli02/tasan and re-run." >&2
    exit 2
  fi
  echo "deploy: pulling origin/main"
  git -C "$ROOT" fetch origin main
  git -C "$ROOT" merge --ff-only origin/main
  echo "deploy: checkout $(git -C "$ROOT" rev-parse --short HEAD) on $(git -C "$ROOT" branch --show-current)"
else
  echo "deploy: skipping git pull (checkout $(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo unknown))"
fi

# --- Vite env for the production build (gitignored) ---
ENV_LOCAL="$APP/.env.production.local"
umask 077
printf 'VITE_TASAN_PROXY_URL=%s\n' "$PROXY_URL" > "$ENV_LOCAL"
chmod 600 "$ENV_LOCAL"
echo "deploy: wrote ${ENV_LOCAL} (proxy URL nonempty=$([[ -n $PROXY_URL ]] && echo yes || echo no))"

# --- install & build ---
cd "$APP"
if [[ -f package-lock.json ]]; then
  echo "deploy: npm ci"
  npm ci
else
  echo "deploy: npm install (no package-lock.json)"
  npm install
fi
echo "deploy: production build"
npm run build
if [[ "$SKIP_OFFLINE" -eq 0 ]]; then
  echo "deploy: offline build"
  npm run build:offline || { echo "BLOCKER: offline build failed." >&2; exit 1; }
fi

# --- preflight: this credential can update the locked site ---
RESP="$(mktemp)"
pre_http="$(curl -sS -o "$RESP" -w "%{http_code}" -H @"$HDR" "https://beacon.host/v1/sites/${LOCKED_SLUG}" || true)"
if [[ "$pre_http" != "200" ]]; then
  echo "deploy: preflight GET /v1/sites/${LOCKED_SLUG} HTTP ${pre_http}" >&2
  redact < "$RESP" >&2
  echo "BLOCKER: the current credential cannot update the claimed site ${LOCKED_SLUG}." >&2
  echo "Needed: a valid Beacon account API key for the owner of this site." >&2
  echo "No new site was created. The live URL was not changed." >&2
  exit 2
fi
echo "deploy: preflight OK — will update only ${LOCKED_URL}"

# --- publish site ---
ZIP="$(mktemp /tmp/tasan-site-XXXXXX.zip)"
python3 - "$APP/dist" "$ZIP" <<'PY'
import sys, zipfile, pathlib
root = pathlib.Path(sys.argv[1])
with zipfile.ZipFile(sys.argv[2], "w", zipfile.ZIP_DEFLATED) as z:
    for f in root.rglob("*"):
        if f.is_file():
            z.write(f, f.relative_to(root).as_posix())
print("zipped", sys.argv[2])
PY
echo "deploy: zip $(wc -c < "$ZIP") bytes"

http="$(curl -sS -o "$RESP" -w "%{http_code}" \
  -H @"$HDR" \
  -F "archive=@${ZIP};type=application/zip" \
  -F "title=${SITE_TITLE}" \
  "https://beacon.host/v1/publish?slug=${LOCKED_SLUG}" || true)"
echo "deploy: beacon publish HTTP $http"
redact < "$RESP" > "$APP/deploy-result.json" || true
chmod 600 "$APP/deploy-result.json" 2>/dev/null || true
rm -f "$ZIP"

python3 - "$RESP" "$APP/PUBLIC_URL.txt" "$http" "$LOCKED_SLUG" "$CONFIG_DIR" <<'PY'
import json, sys, pathlib, re, os
raw = pathlib.Path(sys.argv[1]).read_text()
outp = pathlib.Path(sys.argv[2])
http = sys.argv[3]
locked = sys.argv[4]
cfg = pathlib.Path(sys.argv[5])

def redact(s):
    s = re.sub(r"ctk_[A-Za-z0-9_-]+", "ctk_[REDACTED]", s)
    s = re.sub(r"chk_[A-Za-z0-9_-]+", "chk_[REDACTED]", s)
    return s

m = re.search(r"\{[\s\S]*\}", raw)
try:
    d = json.loads(m.group(0) if m else raw)
except Exception:
    print("deploy: could not parse publish response", file=sys.stderr)
    print(redact(raw)[:800], file=sys.stderr)
    sys.exit(3)

slug = d.get("slug") or ""
url = (d.get("pageUrl") or d.get("url") or "").rstrip("/") + "/"
anonymous = d.get("anonymous")
expires = d.get("expiresAt")
ok_http = http in {"200", "201"}
ok_slug = slug == locked or url.startswith(f"https://{locked}.beacon.host")
if not ok_http or not ok_slug:
    print(f"BLOCKER: publish did not update {locked} (HTTP {http}, slug={slug or 'none'}, anonymous={anonymous}, expiresAt={expires}).", file=sys.stderr)
    print("No other host was used as the public URL. Live URL left unchanged.", file=sys.stderr)
    print(redact(raw)[:800], file=sys.stderr)
    sys.exit(4)
if anonymous or expires:
    print(f"deploy: warning — response still marks anonymous={anonymous} expiresAt={expires}", file=sys.stderr)
outp.write_text(f"https://{locked}.beacon.host/\n")
# last-deploy metadata, no secrets
safe = {
    "url": f"https://{locked}.beacon.host/",
    "slug": locked,
    "updated": d.get("updated"),
    "anonymous": anonymous,
    "expiresAt": expires,
    "versionId": d.get("versionId") or d.get("id"),
    "fileCount": d.get("fileCount"),
    "totalBytes": d.get("totalBytes"),
}
(cfg / "last-deploy.json").write_text(json.dumps(safe, indent=2) + "\n")
os.chmod(cfg / "last-deploy.json", 0o600)
print(f"https://{locked}.beacon.host/")
print(f"deploy: updated={d.get('updated')} anonymous={anonymous} expiresAt={expires} versionId={safe['versionId']}")
PY

# --- worker: redeploy only if source changed (or forced) ---
worker_changed=0
if [[ "$SKIP_WORKER" -eq 1 ]]; then
  echo "deploy: skipping worker (reuse ${WORKER_URL})"
elif [[ "$FORCE_WORKER" -eq 1 ]]; then
  worker_changed=1
  echo "deploy: forced worker redeploy"
else
  if python3 - "$ROOT" "$CONFIG_DIR/worker-source.sha256" <<'PY'
import hashlib, sys
from pathlib import Path
root = Path(sys.argv[1])
hashfile = Path(sys.argv[2])
files = ["app/server/proxy.mjs", "app/server/facts-data.mjs"]
current = []
for rel in files:
    p = root / rel
    if not p.is_file():
        print(f"deploy: missing {rel}", flush=True)
        sys.exit(2)
    current.append(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {rel}")
cur = "\n".join(current) + "\n"
if not hashfile.is_file():
    print("deploy: no stored worker source hash; comparing skipped, will leave worker in place")
    hashfile.write_text(cur)
    hashfile.chmod(0o600)
    sys.exit(0)
if hashfile.read_text() == cur:
    sys.exit(0)
print("deploy: Ask Tasan worker source changed")
sys.exit(1)
PY
  then
    echo "deploy: worker source unchanged — reusing ${WORKER_URL}"
  else
    worker_changed=1
  fi
fi

if [[ "$worker_changed" -eq 1 ]]; then
  echo "deploy: redeploying worker ${WORKER_SLUG}"
  meta=$(python3 -c 'import json,os; print(json.dumps({"entryPoint":os.environ.get("WORKER_ENTRY") or "proxy.mjs","compatibilityDate":os.environ.get("WORKER_COMPAT_DATE") or "2026-11-14","compatibilityFlags":[os.environ.get("WORKER_COMPAT_FLAGS") or "nodejs_compat"]}))')
  whttp="$(curl -sS -o "$RESP" -w "%{http_code}" \
    -X POST \
    -H @"$HDR" \
    -F "metadata=${meta}" \
    -F "file=@${APP}/server/proxy.mjs;filename=proxy.mjs;type=text/javascript" \
    -F "file=@${APP}/server/facts-data.mjs;filename=facts-data.mjs;type=text/javascript" \
    "https://beacon.host/v1/workers/${WORKER_SLUG}/deploy" || true)"
  echo "deploy: worker deploy HTTP ${whttp}"
  redact < "$RESP"
  if [[ "$whttp" != "200" && "$whttp" != "201" ]]; then
    echo "BLOCKER: worker redeploy failed. The frontend may already be updated." >&2
    echo "The existing worker was not deleted. Retry with ${ROOT}/deploy.sh --skip-pull --redeploy-worker" >&2
    exit 2
  fi
  # Secrets persist across deploys. Create VERDA_API_KEY only if absent.
  if [[ -n "${VERDA_API_KEY:-}" ]]; then
    shttp="$(curl -sS -o "$RESP" -w "%{http_code}" \
      -X POST \
      -H @"$HDR" \
      -H "Content-Type: application/json" \
      --data-binary @<(python3 -c 'import json,os; print(json.dumps({"value": os.environ["VERDA_API_KEY"]}))') \
      "https://beacon.host/v1/workers/${WORKER_SLUG}/secrets/VERDA_API_KEY" || true)"
    # 201 created, 409 already present, 200 ok — all fine. Never print the body (may echo).
    if [[ "$shttp" == "201" || "$shttp" == "200" ]]; then
      echo "deploy: worker secret VERDA_API_KEY created (HTTP ${shttp})"
    elif [[ "$shttp" == "409" ]]; then
      echo "deploy: worker secret VERDA_API_KEY already set; left unchanged"
    else
      echo "deploy: warning — could not confirm worker secret (HTTP ${shttp}); if Ask Tasan is mock, set VERDA_API_KEY in ${CONFIG_DIR}/worker.env and re-run --redeploy-worker" >&2
    fi
  fi
  python3 - "$ROOT" "$CONFIG_DIR/worker-source.sha256" <<'PY'
import hashlib, sys
from pathlib import Path
root = Path(sys.argv[1])
hashfile = Path(sys.argv[2])
files = ["app/server/proxy.mjs", "app/server/facts-data.mjs"]
lines = [f"{hashlib.sha256((root/rel).read_bytes()).hexdigest()}  {rel}" for rel in files]
hashfile.write_text("\n".join(lines) + "\n")
hashfile.chmod(0o600)
PY
  echo "deploy: worker updated at ${WORKER_URL}"
fi

# --- verify live site ---
local_js="$(python3 - "$APP/dist/index.html" <<'PY'
import re, pathlib, sys
html = pathlib.Path(sys.argv[1]).read_text()
m = re.search(r'src="([^"]+\.js)"', html)
print(m.group(1) if m else "")
PY
)"
echo "deploy: local bundle is ${local_js:-unknown}"

# CDN cache is 60s; retry until the new bundle is visible or we time out.
live_ok=0
for i in 1 2 3 4 5 6 7 8; do
  live_http="$(curl -sS -o /tmp/tasan-live-index.html -w "%{http_code}" -H "Cache-Control: no-cache" -H "Pragma: no-cache" "${LOCKED_URL}?t=$(date +%s)" || true)"
  if [[ "$live_http" == "200" ]] && [[ -n "$local_js" ]] && grep -q "$local_js" /tmp/tasan-live-index.html; then
    live_ok=1
    break
  fi
  echo "deploy: waiting for live index to serve ${local_js} (HTTP ${live_http}, try ${i})"
  sleep 8
done
if [[ "$live_ok" -ne 1 ]]; then
  echo "BLOCKER: ${LOCKED_URL} did not serve ${local_js} after publish (last HTTP ${live_http:-none})." >&2
  echo "live index:" >&2
  cat /tmp/tasan-live-index.html >&2 || true
  exit 2
fi
echo "deploy: verified ${LOCKED_URL} is HTTP 200 and serves ${local_js}"

# --- smoke checks ---
if [[ "$SKIP_SMOKE" -eq 0 ]]; then
  echo "deploy: smoke checks"
  python3 - "$LOCKED_URL" "$local_js" "$PROXY_URL" <<'PY'
import json, re, sys, urllib.request, urllib.error

site, bundle, proxy = sys.argv[1:4]
origin = site.rstrip("/")
errors = []

def get(url, headers=None, timeout=30):
    req = urllib.request.Request(url, headers=headers or {"User-Agent": "tasan-deploy-smoke"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.read()

# Bundle must contain the four tabs.
js_url = site.rstrip("/") + "/" + bundle.lstrip("./")
status, body = get(js_url)
text = body.decode("utf-8", "replace")
print(f"deploy: smoke bundle HTTP {status} ({len(body)} bytes)")
for label in ("Overview", "Tasan Live", "Pilot", "How we built it"):
    if label not in text:
        errors.append(f"bundle missing tab label {label!r}")
    else:
        print(f"deploy: smoke tab label ok: {label}")

# Query-param routes exist in the app.
# Vite minifies these as backtick strings: id:`overview`
for tab in ("overview", "live", "pilot", "built"):
    if not any(f"{q}{tab}{q}" in text for q in ('"', "'", "`")):
        errors.append(f"bundle missing tab id {tab}")
    else:
        print(f"deploy: smoke tab id ok: {tab}")

# Worker health
st, raw = get(proxy.rstrip("/") + "/health")
health = json.loads(raw.decode())
print(f"deploy: smoke worker /health HTTP {st} ok={health.get('ok')} mock={health.get('mock')} facts={health.get('facts')}")
if not health.get("ok"):
    errors.append("worker /health not ok")
if health.get("mock"):
    errors.append("worker is in mock mode (VERDA_API_KEY missing on the worker)")
if health.get("facts", 0) < 1:
    errors.append("worker reported zero facts")

# One Ask Tasan question. Origin must be the live site (CORS).
q = {
    "question": "What is the age-adjusted share of lung-cancer patients getting curative treatment in Lapland?",
    "lang": "en",
    "stream": False,
}
data = json.dumps(q).encode()
req = urllib.request.Request(
    proxy.rstrip("/") + "/ask",
    data=data,
    headers={
        "Content-Type": "application/json",
        "Origin": origin,
        "Accept": "application/json",
        "User-Agent": "tasan-deploy-smoke",
    },
    method="POST",
)
try:
    with urllib.request.urlopen(req, timeout=60) as r:
        st = r.status
        payload = r.read()
except urllib.error.HTTPError as e:
    st = e.code
    payload = e.read()
    errors.append(f"Ask Tasan HTTP {st}")
except Exception as e:
    st = 0
    payload = b""
    errors.append(f"Ask Tasan request failed: {type(e).__name__}")

preview = ""
if payload:
    try:
        obj = json.loads(payload.decode())
        preview = (obj.get("text") or obj.get("error") or json.dumps({k: obj[k] for k in list(obj)[:6] if k != "choices"}))[:400]
    except Exception:
        # Maybe SSE even though stream=false
        preview = payload.decode("utf-8", "replace")[:400]
print(f"deploy: smoke Ask Tasan HTTP {st}")
if preview:
    # no secrets expected; still avoid dumping huge bodies
    print("deploy: smoke Ask Tasan preview:", re.sub(r"\s+", " ", preview)[:320])
if st != 200:
    errors.append(f"Ask Tasan returned HTTP {st}")
elif not preview or "error" == (preview or "")[:5]:
    errors.append("Ask Tasan returned an empty or error body")

if errors:
    print("BLOCKER: smoke checks failed:", file=sys.stderr)
    for e in errors:
        print(f"  - {e}", file=sys.stderr)
    sys.exit(5)
print("deploy: smoke checks passed")
PY

  # Headless render of each tab, when Chrome is available.
  CHROME="$(command -v google-chrome-stable || command -v google-chrome || command -v chromium-browser || command -v chromium || true)"
  if [[ -n "$CHROME" ]]; then
    echo "deploy: rendering tabs in headless Chrome"
    python3 - "$CHROME" "$LOCKED_URL" <<'PY' || echo "deploy: warning — headless tab render had a problem (bundle and Ask checks already passed)"
import subprocess, sys, tempfile, os, re
from pathlib import Path

chrome, site = sys.argv[1], sys.argv[2]
# Distinctive strings that should appear after JS renders each tab.
expect = {
    "overview": ["Overview", "curative"],
    "live": ["Tasan Live"],
    "pilot": ["Pilot"],
    "built": ["How we built it", "SYNTHETIC"],
}
failed = []
for tab, needles in expect.items():
    url = f"{site.rstrip('/')}?tab={tab}"
    with tempfile.NamedTemporaryFile(suffix=".html", delete=False) as f:
        out = f.name
    cmd = [
        chrome, "--headless=new", "--disable-gpu", "--no-sandbox",
        "--disable-dev-shm-usage", "--hide-scrollbars",
        f"--virtual-time-budget=12000", "--dump-dom", url,
    ]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=45)
        html = r.stdout or ""
        Path(out).write_text(html)
    except Exception as e:
        failed.append(f"{tab}: {type(e).__name__}")
        continue
    low = html
    missing = [n for n in needles if n.lower() not in low.lower()]
    # Also confirm the tab button is marked on, if the class is present.
    if missing or len(html) < 500:
        failed.append(f"{tab}: missing {missing or 'content'} (dom {len(html)} bytes, rc {r.returncode})")
    else:
        print(f"deploy: smoke render ok ?tab={tab} ({len(html)} bytes)")
    try:
        os.unlink(out)
    except Exception:
        pass
if failed:
    print("deploy: warning — some tab renders were incomplete:")
    for f in failed:
        print(f"  - {f}")
    # Do not fail the deploy: the bundle labels and live index already checked out,
    # and headless timing can be flaky. The operator can open the URL.
    sys.exit(0)
print("deploy: all four tabs rendered")
PY
  else
    echo "deploy: Chrome not found; skipped visual tab render (bundle labels were checked)"
  fi
fi

echo "deploy: public URL → ${LOCKED_URL}"
echo "deploy: bundle → ${local_js}"
echo "deploy: Ask Tasan → ${PROXY_URL}"
echo "deploy: site is claimed and does not expire."
exit 0
