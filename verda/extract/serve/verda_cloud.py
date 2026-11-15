"""Minimal Verda Cloud API client for Tasan Extract.

Credentials are read ONLY from env (VERDA_CLIENT_ID / VERDA_CLIENT_SECRET),
kept in memory, and never printed, logged or written to disk.
Token endpoint: POST https://api.verda.com/v1/oauth2/token
"""
import json, os, urllib.request, urllib.error

API = "https://api.verda.com/v1"
_tok = None


def _token():
    global _tok
    if _tok is None:
        cid = os.environ["VERDA_CLIENT_ID"]
        sec = os.environ["VERDA_CLIENT_SECRET"]
        body = json.dumps({
            "grant_type": "client_credentials",
            "client_id": cid,
            "client_secret": sec,
        }).encode()
        r = urllib.request.Request(
            f"{API}/oauth2/token", data=body, method="POST",
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(r, timeout=30) as f:
            _tok = json.loads(f.read())["access_token"]
    return _tok


def call(method, path, payload=None):
    data = json.dumps(payload).encode() if payload is not None else None
    r = urllib.request.Request(
        f"{API}{path}", data=data, method=method,
        headers={"Authorization": f"Bearer {_token()}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(r, timeout=60) as f:
            raw = f.read()
            try:
                return f.status, json.loads(raw) if raw else None
            except json.JSONDecodeError:
                return f.status, raw.decode(errors="replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode(errors="replace")[:500]
