# Ask Tasan / Verda spend

All figures are USD. No credentials are recorded here.

## Host

Verda on-demand `CPU.4V.16G` / `CPU-TURIN.4V.16G` in FIN-01, FIN-02 and FIN-03 returned **no capacity** on 2026-11-14 (availability list had only GPU types: `1A100.22V`, `1RTXPRO6000.30V.CC`, `8B300.240V.CC.AMD`). A probe create of `CPU.4V.16G` in FIN-01 came back 503 "Not enough resources". The cheapest in-stock GPU (`1A100.22V`, $2.386/h) would cost about $42 if left up from this evening through judging Sunday 15:00 Europe/Helsinki, which would breach the $25 cap, and this track was not to launch a GPU/Extract box. Teammate instance `tasan-extract` (`1A100.22V`) was left untouched.

The portable proxy (`app/server/proxy.mjs`) was therefore deployed as a **Beacon Worker**, the fallback already designed for this file:

- Proxy URL: https://petaled-trowel-90-ask.worker.beacon.host
- This is a Worker, not a new Beacon static site. The public app stays at https://petaled-trowel-90.beacon.host/
- Model: kimi-k3-1-pro (EU-hosted inference · Verda). Do not describe inference as Finland-hosted.
- `VERDA_API_KEY` is a Worker secret only (name listed; value never stored in git, logs or the client).
- CORS locked to https://petaled-trowel-90.beacon.host and localhost.
- Instance ID: none (no Verda Cloud VM)
- Instance spend: **$0.00**

If CPU.4V.16G-class stock returns, `app/server/launch_proxy_instance.py` can still stand up the on-demand CPU + Caddy/sslip.io path. Keep any such instance up through Sunday 12:00–15:00 Europe/Helsinki and delete it via the Verda API after the demo; `shutdown -h` may not stop billing.

## Inference

List prices used for estimates: about $2.00 / 1M input tokens and $10.00 / 1M output tokens for kimi-k3-1-pro (confirm in the Verda console). The Worker system prompt includes the 81-fact pack (order-of-magnitude ~8–15k input tokens per call).

| Item | Estimate |
|---|---|
| Verda Cloud CPU instance | $0.00 |
| Inference tokens (smoke tests + 18-prompt trick suite + earlier empty-content probes) | ~$1.50–$3.00 |
| **Running total** | **≈ $2–$3, well under $25** |

Method: about 26 chat-completion calls to kimi-k3-1-pro. Each call sends the bundled 81-fact system prompt (on the order of 8–15k input tokens) plus a short question. Outputs were typically a few hundred to ~2k tokens; two brief drafts ran longer. Using the published-order list prices of about $2.00 / 1M input tokens and $10.00 / 1M output tokens, the central estimate is under $2, with a $3 ceiling to cover hidden thinking tokens from the pre-patch probes. Confirm exact usage in the Verda console; this file never stores keys or raw usage payloads.

Cap: $25.00. Updated 2026-11-14 21:34 Europe/Helsinki.
