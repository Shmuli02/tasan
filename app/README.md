# Equal Care — live demo (Junction 2026, AstraZeneca)

Static Vite + React + TypeScript app. Everything is bundled; after the first load it works with no network. Content is loaded from JSON that follows [DATA_CONTRACT.md](./DATA_CONTRACT.md).

## Run locally

```bash
cd /workspace/junction-new/app
npm install
npm run dev          # http://127.0.0.1:5173
```

Production build (also runs data sync + TypeScript + a smoke test via `npm test`):

```bash
npm run test         # sync, validate, production build
npm run preview      # http://127.0.0.1:4173
```

## Swap in the team dataset

Put files in `/workspace/junction-new/data` and `/workspace/junction-new/recs` as described in the contract, then:

```bash
npm run sync && npm run test && npm run deploy
```

If a file is missing or invalid, the app keeps serving labelled example data and does not crash.

## Deploy

```bash
npm run deploy
```

Writes the public URL to `PUBLIC_URL.txt` (and prints it). Redeploy is the same command.

## Stage fallback (no network)

After a production build, serve the static files from this machine only:

```bash
npm run stage        # http://127.0.0.1:8080  (builds, then serves app/dist)
```

Or: `python3 -m http.server 8080 --bind 127.0.0.1 --directory dist` from `app/` after `npm run build`. Fonts, map and data are bundled; no external requests are required. A single-file copy is also at `dist-offline/index.html` (`npm run build:offline`).

## Screenshot

```bash
npm run screenshot   # writes /workspace/junction-new/app/screenshot.png
```
