# Tasan

Junction 2026 entry for the AstraZeneca challenge **Equal Care Across Finland**, plus the separate **Verda Compute Track**.

Tasan is a lung-cancer pathway clock for Finland's 22 wellbeing services counties. Public registries do not publish referral-to-treatment times or 6-week compliance at county level, so the project combines public-data insights, concrete recommendations, a working demo, and two Verda-backed prototypes: **Tasan Extract** (pathway events from synthetic clinical notes) and a **Pathway Twin** simulator.

**Live demo:** https://petaled-trowel-90.beacon.host/

**Two sides, one project:** Tasan is the county and leadership view: where the gap is and what to do. [Polku](https://polku.ender.fi) is the care-team view: it runs each lung pathway step by phone and records the step clocks that no county publishes today. Tasan links to Polku where that missing data shows up (topbar, the "Not measured" tile, the end of Tasan Live, and Ask Tasan).

Clinical notes and extract evaluation data in this repository are **synthetic** (`SYN-*` / `SYN2-*`). No real patient data is included.

## What's in this repository

| Path | Contents |
| --- | --- |
| `app/` | Vite + React + TypeScript demo, plus the Ask Tasan server |
| `data/` | Public-registry extracts, derived tables, sources, and spend notes |
| `recs/` | Recommendations and pilot briefs |
| `sim/` | Pathway Twin simulator, results, and Verda job scripts |
| `verda/` | Extract pipeline, evaluation results, and Compute Track write-up |
| `pitch/` | Pitch script, scorecard, and review notes |
| `brand/` | Logo, tokens, and UI style |
| `review/` | Demo screenshots and review notes |
| `PLAN.md`, `STATUS.md`, `CHALLENGE.txt` | Project plan, work log, and challenge text |

## Run the app locally

```bash
cd app
npm install
npm run dev          # http://127.0.0.1:5173
```

Production build (also runs data sync, TypeScript, and a smoke test):

```bash
npm run test         # sync, validate, production build
npm run preview      # http://127.0.0.1:4173
```

After a production build you can also serve a no-network static copy with `npm run stage` (http://127.0.0.1:8080). See `app/README.md` and `app/DATA_CONTRACT.md`.

Scripts that talk to Verda or the Ask Tasan proxy read credentials from the environment only. Do not commit `.env` files or keys.
