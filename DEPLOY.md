# Redeploying Tasan

The live demo is locked to this URL and must not be replaced by a new Beacon site:

**https://petaled-trowel-90.beacon.host/**

Ask Tasan (the backend) stays at:

**https://petaled-trowel-90-ask.worker.beacon.host**

## One command

From a clone of this repository:

```bash
./deploy.sh
```

That command:

1. Fast-forwards the checkout to `origin/main`.
2. Installs app dependencies (`npm ci`) and builds the production bundle, including the data sync and TypeScript check.
3. Publishes `app/dist` to the locked Beacon site only, after a preflight `GET` that confirms the current credential can update `petaled-trowel-90`.
4. Leaves the Ask Tasan worker in place unless `app/server/proxy.mjs` or `app/server/facts-data.mjs` changed (or you pass `--redeploy-worker`).
5. Waits until the live index serves the new bundle hash, then smokes the four tabs (Overview, Tasan Live, Pilot, How we built it), the worker `/health` endpoint, and one Ask Tasan question.

Options: `--skip-pull`, `--skip-offline`, `--skip-worker`, `--skip-smoke`, `--redeploy-worker`, `--help`.

## Deploy state (not in git)

Secrets and locked-site settings live in `~/.config/tasan/` (or `$TASAN_DEPLOY_CONFIG`). The directory should be `chmod 700`, and every file in it `chmod 600`. **Never commit this directory or paste keys into the repository, tickets, or chat.**

| File | Purpose |
| --- | --- |
| `beacon-api-key` | Beacon account API key (`chk_…`), one line. A JSON `{"apiKey":"chk_…"}` file named `beacon-config.json` also works. |
| `app.env` | Non-secret settings: `SITE_SLUG`, `SITE_URL`, `WORKER_SLUG`, `VITE_TASAN_PROXY_URL`, worker compatibility fields. |
| `worker.env` | `VERDA_API_KEY` (and optional `VERDA_MODEL` / `VERDA_BASE_URL`). Used only if the worker secret needs to be created. Existing worker secrets are left unchanged across redeploys. |
| `claim.url` | Optional fallback claim link. The API key is what actually updates the claimed site. |
| `worker-source.sha256` | Hashes of the last published worker source, so unchanged code is not redeployed. |
| `last-deploy.json` | Redacted metadata from the last successful publish (no keys). |

Environment variables override the files: `BEACON_API_KEY`, `VITE_TASAN_PROXY_URL`, `VERDA_API_KEY`. If `~/.config/tasan/` has no key, the script also reads `~/.config/beacon/config.json`.

### If the config is missing

The script exits before publishing and prints what to create. To rebuild the files on this machine, you need:

1. A Beacon API key from https://beacon.host/dashboard (API key page), signed in as the account that owns `petaled-trowel-90`. Write it to `~/.config/tasan/beacon-api-key` and `chmod 600` that file. Do not paste the key into chat.
2. `app.env` with at least:

   ```
   SITE_SLUG=petaled-trowel-90
   SITE_URL=https://petaled-trowel-90.beacon.host/
   WORKER_SLUG=petaled-trowel-90-ask
   VITE_TASAN_PROXY_URL=https://petaled-trowel-90-ask.worker.beacon.host
   ```

3. For a first-time worker secret only: `worker.env` containing `VERDA_API_KEY=…` (`chmod 600`). The live worker already has this secret; you do not need to rotate it for a normal frontend redeploy.

## Safety rules

- The script will not publish if the credential cannot see `petaled-trowel-90`, or if Beacon returns a different slug. It never uses a new anonymous (expiring) URL as the public site.
- Do not commit `.env`, `.env.*.local`, `CLAIM_URL.txt`, `PUBLIC_URL.txt`, `deploy-result.json`, `server/.run/`, or anything under `~/.config/tasan/`.
- `VERDA_API_KEY` stays on the worker as a secret. It must not go in client code or the bundle.
- Clinical notes in this repo are synthetic. Do not add real patient data.

The older helper `app/scripts/deploy.sh` (also locked to this slug) is still there, but `./deploy.sh` at the repo root is the one-command path.
