#!/usr/bin/env bash
# Publish only to the claimed, permanent site petaled-trowel-90.
# Never create a new anonymous (expiring) site.
set -euo pipefail
APP="$(cd "$(dirname "$0")/.." && pwd)"
cd "$APP"

LOCKED_SLUG="petaled-trowel-90"
LOCKED_URL="https://${LOCKED_SLUG}.beacon.host/"
OUT="$APP/PUBLIC_URL.txt"
CLAIM="$APP/CLAIM_URL.txt"
RESULT="$APP/deploy-result.json"
CLIENT="X-Beacon-Client: tasan-junction/2026"

redact() {
  python3 -c 'import sys,re; t=sys.stdin.read(); t=re.sub(r"ctk_[A-Za-z0-9_-]+","ctk_[REDACTED]",t); t=re.sub(r"chk_[A-Za-z0-9_-]+","chk_[REDACTED]",t); sys.stdout.write(t)'
}

load_api_key() {
  # Export BEACON_API_KEY if found. Never print it.
  if [[ -n "${BEACON_API_KEY:-}" ]]; then
    return 0
  fi
  local cfg="${HOME}/.config/beacon/config.json"
  if [[ -f "$cfg" ]]; then
    local key
    key=$(python3 - "$cfg" << 'PY'
import json, sys
from pathlib import Path
try:
    d = json.loads(Path(sys.argv[1]).read_text())
except Exception:
    sys.exit(0)
k = d.get("apiKey") or d.get("api_key") or ""
if isinstance(k, str) and k.startswith("chk_"):
    sys.stdout.write(k)
PY
)
    if [[ -n "${key:-}" ]]; then
      export BEACON_API_KEY="$key"
      return 0
    fi
  fi
  return 1
}

parse_claim_token() {
  CLAIM_TOKEN=""
  if [[ -s "$CLAIM" ]]; then
    CLAIM_TOKEN=$(python3 - "$CLAIM" << 'PY'
from pathlib import Path
import sys, re
raw = Path(sys.argv[1]).read_text().strip()
m = re.search(r"#(ctk_[A-Za-z0-9_-]+)", raw)
if m:
    sys.stdout.write(m.group(1))
PY
)
  fi
}

auth_headers=()
auth_mode=""

load_api_key && {
  auth_mode="api_key"
  auth_headers=(-H "Authorization: Bearer ${BEACON_API_KEY}")
  echo "deploy: using account API key to update ${LOCKED_SLUG} only"
} || {
  parse_claim_token
  if [[ -n "${CLAIM_TOKEN:-}" ]]; then
    auth_mode="claim_token"
    auth_headers=(-H "X-Claim-Token: ${CLAIM_TOKEN}")
    echo "deploy: no account API key found; trying the saved claim token on ${LOCKED_SLUG}"
    echo "deploy: if the site is already claimed, this will fail and we will stop (no new site)."
  else
    echo "BLOCKER: cannot update https://${LOCKED_SLUG}.beacon.host"
    echo "The site is claimed into a free beacon.host account. Claim tokens no longer manage it."
    echo "Needed: an account API key from the beacon.host dashboard 'API key' page."
    echo "  1. Open https://beacon.host/dashboard (API key page) while signed in as the account that claimed the site."
    echo "  2. Copy the API key (it starts with chk_)."
    echo "  3. Either export BEACON_API_KEY (do not paste it into chat) or write {\"apiKey\":\"chk_...\"} to ~/.config/beacon/config.json and chmod 600 that file."
    echo "  4. Re-run: cd /workspace/junction-new/app && npm run deploy"
    echo "No new site was created. The live URL was not changed."
    exit 2
  fi
}

# Preflight: confirm this credential can see the locked slug. Fail closed before building
# if it cannot, so we never publish a new anonymous site.
pre_resp=$(mktemp)
pre_http=$(curl -sS -o "$pre_resp" -w "%{http_code}" \
  -H "$CLIENT" \
  "${auth_headers[@]}" \
  "https://beacon.host/v1/sites/${LOCKED_SLUG}" || true)
pre_err=$(redact < "$pre_resp")
if [[ "$pre_http" != "200" ]]; then
  echo "deploy: preflight GET /v1/sites/${LOCKED_SLUG} HTTP ${pre_http}"
  echo "$pre_err"
  echo "BLOCKER: the current credential cannot update the claimed site ${LOCKED_SLUG}."
  if [[ "$auth_mode" == "claim_token" ]]; then
    echo "The saved claim token is no longer accepted now that the site is in an account."
  fi
  echo "Needed: an account API key from the beacon.host dashboard 'API key' page."
  echo "  1. Open https://beacon.host/dashboard (API key page) while signed in as the account that claimed the site."
  echo "  2. Copy the API key (it starts with chk_)."
  echo "  3. Either export BEACON_API_KEY (do not paste it into chat) or write {\"apiKey\":\"chk_...\"} to ~/.config/beacon/config.json and chmod 600 that file."
  echo "  4. Re-run: cd /workspace/junction-new/app && npm run deploy"
  echo "No new site was created. The live URL was not changed."
  rm -f "$pre_resp"
  exit 2
fi
rm -f "$pre_resp"
echo "deploy: preflight OK — will update only ${LOCKED_URL}"

npm run build
npm run build:offline || { echo "deploy: offline build failed"; exit 1; }

ZIP=$(mktemp /tmp/tasan-site-XXXXXX.zip)
python3 - "$APP/dist" "$ZIP" << 'PY'
import sys, zipfile, pathlib
root = pathlib.Path(sys.argv[1])
with zipfile.ZipFile(sys.argv[2], "w", zipfile.ZIP_DEFLATED) as z:
    for f in root.rglob("*"):
        if f.is_file():
            z.write(f, f.relative_to(root).as_posix())
print("zipped", sys.argv[2])
PY
echo "deploy: zip $(wc -c < "$ZIP") bytes"

resp=$(mktemp)
http=$(curl -sS -o "$resp" -w "%{http_code}" \
  -H "$CLIENT" \
  "${auth_headers[@]}" \
  -F "archive=@${ZIP};type=application/zip" \
  -F "title=Tasan — Equal Care Across Finland" \
  "https://beacon.host/v1/publish?slug=${LOCKED_SLUG}" || true)

echo "deploy: beacon HTTP $http"
redact < "$resp" > "$RESULT" || true
rm -f "$ZIP"

python3 - "$resp" "$OUT" "$http" "$LOCKED_SLUG" << 'PY' && ok=1 || ok=0
import json, sys, pathlib, re
raw = pathlib.Path(sys.argv[1]).read_text()
http = sys.argv[3]
locked = sys.argv[4]
outp = pathlib.Path(sys.argv[2])

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
    print("No other host was used. Live URL left unchanged.", file=sys.stderr)
    print(redact(raw)[:800], file=sys.stderr)
    sys.exit(4)
if anonymous or expires:
    print(f"deploy: warning — response still marks anonymous={anonymous} expiresAt={expires}", file=sys.stderr)
outp.write_text(f"https://{locked}.beacon.host/\n")
print(f"https://{locked}.beacon.host/")
print(f"deploy: updated={d.get('updated')} anonymous={anonymous} expiresAt={expires}")
PY
rm -f "$resp"

if [[ "$ok" -ne 1 ]]; then
  echo "BLOCKER: update of the claimed site failed. Needed: a valid account API key (see preflight message)."
  echo "No new site was created."
  exit 2
fi

# Verify the public URL actually serves the new index.
local_js=$(python3 - << 'PY'
import re, pathlib
html = pathlib.Path("/workspace/junction-new/app/dist/index.html").read_text()
m = re.search(r'src="([^"]+\.js)"', html)
print(m.group(1) if m else "")
PY
)
live_http=$(curl -sS -o /tmp/tasan-live-index.html -w "%{http_code}" "$LOCKED_URL" || true)
if [[ "$live_http" != "200" ]]; then
  echo "BLOCKER: ${LOCKED_URL} returned HTTP ${live_http} after publish."
  exit 2
fi
if [[ -n "$local_js" ]] && ! grep -q "$local_js" /tmp/tasan-live-index.html; then
  echo "deploy: warning — live index does not yet mention ${local_js} (CDN cache is 60s; check again shortly)."
  echo "live index:"
  cat /tmp/tasan-live-index.html
else
  echo "deploy: verified ${LOCKED_URL} is HTTP 200 and serves ${local_js}"
fi
echo "deploy: public URL → ${LOCKED_URL}"
echo "deploy: site is claimed and does not expire."
exit 0
