# Tasan Extract — Verda GPU launch (do not run until approved)

`launch_extract_instance.py` is a **dry-run by default**. It must not be started with `--execute` until:

1. The user approves a budget (operational cap $10, hard $25 — see `../../EXTRACT_PLAN.md`).
2. Availability is re-checked: `GET /v1/instance-availability/1A100.22V?is_spot=false&location_code=FIN-01`.
3. Env `TASAN_VERDA_BUDGET_APPROVED=yes` is set for that one process.
4. You have confirmed you will not delete or interfere with any other project instance (cleanup is scoped to IDs this script creates).

Credentials stay in `VERDA_CLIENT_ID` / `VERDA_CLIENT_SECRET`. They are never printed and must never be copied onto the instance.

## Intended command (when approved)

```bash
# still a dry-run (prints the plan, creates nothing):
python3 launch_extract_instance.py

# live launch — only after written approval:
TASAN_VERDA_BUDGET_APPROVED=yes python3 launch_extract_instance.py --execute --watchdog-min 180 --cap 10
```

Then, from a second shell, tunnel and run the client:

```bash
ssh -i <ephemeral-key> -L 8000:127.0.0.1:8000 -o BatchMode=yes root@<ip>
python3 ../client/extract_client.py --base-url http://127.0.0.1:8000/v1 --model Qwen/Qwen3-32B-AWQ --concurrency 8
```

## Known risks (read before --execute)

- The on-demand `contract` value `PAY_AS_YOU_GO` is inferred, not proven by a live create. If the API rejects it, drop the field and retry only with approval.
- Hugging Face download of Qwen3-32B-AWQ may exceed 30 minutes; the watchdog can halt the box mid-pull if `--watchdog-min` is too tight. 180 minutes is the default (~$7.2 instance + storage).
- `shutdown -h` on the instance may **not** stop billing. The launcher’s API delete is what actually ends the charge. If the controller process dies, you must delete the instance by hand.
- vLLM flags for Qwen3 “thinking off” differ across versions; the client also sends `chat_template_kwargs.enable_thinking=false` and can append `/no_think`.
- Confirm the Hugging Face repo `Qwen/Qwen3-32B-AWQ` still exists at pull time; fallback is documented in EXTRACT_PLAN.md.
- Do not upload real patient notes. The eval corpus is SYNTHETIC.
