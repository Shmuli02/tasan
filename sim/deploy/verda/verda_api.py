"""Minimal Verda Cloud API client. Credentials are read ONLY from env (VERDA_CLIENT_ID / VERDA_CLIENT_SECRET),
kept in memory, and never printed, logged or written to disk. Token endpoint: POST https://api.verda.com/v1/oauth2/token."""
import json, os, urllib.request, urllib.error

API = "https://api.verda.com/v1"
_tok = None

def _token():
    global _tok
    if _tok is None:
        body = json.dumps({"grant_type": "client_credentials", "client_id": os.environ["VERDA_CLIENT_ID"],
                           "client_secret": os.environ["VERDA_CLIENT_SECRET"]}).encode()
        r = urllib.request.Request(f"{API}/oauth2/token", data=body, method="POST", headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=30) as f:
            _tok = json.loads(f.read())["access_token"]
    return _tok

def call(method, path, payload=None, _retry=True):
    global _tok
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(f"{API}{path}", data=data, method=method,
                               headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(r, timeout=60) as f:
            raw = f.read()
            try:
                return f.status, json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return f.status, raw.decode(errors="replace")
    except urllib.error.HTTPError as e:
        if e.code == 401 and _retry:  # access token expired (seen after ~25 min on 14.11.2026) -> refresh once
            _tok = None
            return call(method, path, payload, _retry=False)
        return e.code, e.read().decode(errors="replace")[:500]
