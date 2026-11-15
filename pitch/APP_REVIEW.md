# APP_REVIEW — Tasan live demo, harsh judge pass

Reviewer: JN Pitch. Sat 14 Nov 2026, ~19:55–20:05 Europe/Helsinki (EET).
Build reviewed: live https://petaled-trowel-90.beacon.host/ , bundle `index-BOMKJaff.js` (redeployed 19:52 EET, mid-review; every screenshot was retaken on this build).
Method: headless Chrome (Playwright) at 1280×800; every nav link, map layer, county, analyst chip, slider, "Start here" step and "Show brief" clicked. Screenshots: `pitch/app_review/`. Silent backup recording (78 s, 1280×800): `pitch/app_review/backup_demo_90s.webm`.
Ground truth: `data/hero.json`, `data/LUNG.md`, `recs/top3.md`, `recs/recommendations.json`, `recs/pilot_brief.md`.

## Verdict

| Criterion | Weight | Score (0/1/3/5) | Points |
|---|---|---|---|
| Execution | 15% | **3** | 9 / 15 |
| Clarity | 10% | **3** | 6 / 10 |

**No fatal issue.** No EXAMPLE or synthetic data is left (the banner is gone). Every hero number matches `hero.json`. The hero caveat is on the same card. T3 leads.
**Why not 5.** Two clicks a judge might make contradict the pitch:
- The map opens on the surgery-days layer, which colours Lapland green ("13.5 d", ranked best).
- The analyst's default answer says the widest gap is primary → specialist referral, which is an all-specialty indicator.

The guided "Start here" path ends on that analyst answer. A cold director reaches the gap in about 30 s, but reaches "who signs and what it costs" only at about 2:30. The page is 19,586 px tall (40,916 px on mobile).

Deploy note (updated 20:05 EET): the public URL is claimed and permanent. Stage fallback order is in PITCH_SCRIPT.md: live URL → `app/dist-offline/index.html` → screenshots/recording.

## 1. Screens and interactions tested

| # | Screen / action | Screenshot | Result |
|---|---|---|---|
| 1 | First view (top bar, key message, hero) | `01_first_view.png`, `scroll_00.png` | Loads in 2.1 s, network idle 3.3 s. Hero visible above the fold. |
| 2 | "Start here" guided path, steps 1–4 | `01b_start_here.png`, `13_start_step1..4.png` | Works (Next / keys 1–4 / Esc). Step 2 lands on "Why Tasan exists" and the signal cards, **not on the map**. Step 4 lands on the **analyst default answer (referral)**. |
| 3 | Nav: The gap / Map / Analyst / Simulator / Sources | `02_nav_*.png` | All anchors work. |
| 4 | Map layers Detect, Refer, Treat, Dx→Tx, Surgery, Radiotherapy, Drug therapy | `03_map_*.png` | All render. **Default layer = Dx→Tx surgery** (from `key_message.json` `spotlight_stage: "diagnosis"`). |
| 5 | County select: Lapland, Vantaa-Kerava, Kymenlaakso (Treat layer) | `04_county_*.png`, `04b_*` | Pathway panel updates. It shows the **crude** 18.5%; the age-adjusted 16.2% is not on this screen. |
| 6 | Analyst: 8 chips + free text ("What should Lapland sign on Monday?") | `05_analyst_*.png` | Deterministic, offline, cites sources. The "Impact of T3" answer **dumps raw JSON** (`[{"claim":…`). "How does this map to Goal 3?" lists 15 longlist items, all badged GOAL 3, including "(Goal 2, secondary)". The free-text Lapland answer leads with crude 18.5% and has no Monday action. |
| 7 | Citation chip click | `06_cite_click.png` | Jumps to Sources and highlights the entry. Works. |
| 8 | Simulator: 3 sliders at max | `07_simulator_*.png` | Works and is labelled an assumption. The surgery slider produces "Pohjois-Suomi 13.5 d → 0 d", which is absurd if projected. |
| 9 | Pilot brief ("Show brief") | `12_pilot_brief.png`, `12b_*` | Renders, but shows **raw markdown** ("> ## ⚠ DRAFT – not signed") and an internal note ("Generated from top3.json by scripts/gen_pilot_brief.py, so do not hand-edit"). |
| 10 | Offline: live tab after Wi-Fi drop | `08_offline_reload.png` | In-tab interactions keep working. A **reload fails** (no service worker). |
| 11 | Offline: local `app/dist` served on 127.0.0.1 with all external requests blocked | `11_local_offline_dist.png` | **Works fully, zero external requests** (fonts and data bundled). This is the venue fallback. |
| 12 | Projector 1024×768 | `09_projector_1024x768.png` | Headline is readable. Caveat and KPI text (11–12 px) is unreadable from the back of a room. |
| 13 | Mobile 390 px | `10_mobile_390*.png` | No horizontal overflow, but the page is 40,916 px tall. |
| 14 | Console / network | — | Only error: `favicon.ico` 404. No JS errors. External source links are plain `<a>`; none are needed for the demo. |

## 2. Number check against ground truth

| On screen | Ground truth | Status |
|---|---|---|
| Hero men Lapland ~16.2 [12.7–20.4], V-K ~29.8 [24.2–36.1] | hero.json `lung_curative_share.regions` | ✅ match |
| Hero women ~23.1 [17.9–29**.0**], ~39.7 [33.1–47**.0**] | hero.json | ⚠️ App shows "17.9–29" and "33.1–47" because the trailing zeros are dropped. Cosmetic, but a judge reads "29" as a different number. |
| Crude 18.5 (131/710), 35.6 (212/595), FI 27.0 (4009/14873) | hero.json `crude_secondary` | ✅ (labelled "SECONDARY VALUE · CRUDE (NOT THE HERO NUMBER)") |
| 13.5 [0–44] / 46 [33–63] / FI 37 [0–56] d | hero.json `lung_dx_to_surgery_days` | ✅ on the signal card |
| **Pathway panel: "Diagnosis → treatment: No public data — No national median was published in Taulukko 4.1"** | hero.json `national: 37.0` ("national median from text p.27"), shown 2 screens earlier as "Finland 37 d" | ❌ **Contradiction.** Source: `app/scripts/extract_team_data.py:547` → `src/content/regions.json`. |
| 2-month 27.7 [25.9–29.6] vs 38.7 [36.6–40.8] | hero.json | ✅ |
| 1-yr survival 40.1 / 46.8 / FI 42.9 + CIs | hero.json | ✅ |
| Stage missing 47.7% (7097/14873) | hero.json | ✅ number. ⚠️ The card is badged "CHART ESTIMATE", but 47.7% is a printed Taulukko 4 count; only the 22–68% county range is chart-read. |
| T1 Kymenlaakso crude 19.3% (16.3–22.7; 114/591) | top3.md, pilot_brief.md, LUNG.md | ✅ |
| T2 Pohjois-Pohjanmaa men ≈23.2 (19.7–26.7), women ≈25.3 (21.0–30.7) | top3.md | ✅ |
| Costs T3 €20,339–23,988; T1 €5,863–7,477 (conditional); T2 €3,518–4,486 (90 d) | pilot_brief.md | ✅ |
| Signers: Rajaniemi (Kymenhva), Taskila (Lapland); navigator line managers Kuusisto / Kauranen | pilot_brief.md | ✅ |
| Analyst "widest gap": referral 68.9–88.7% (Sotkanet 13) | **not in hero.json or recs**; FINDINGS_REVIEW treats referral as context | ❌ Off-message as the default answer (see Fix 2). |
| Analyst/Simulator treatment spread 18.5–35.6 | crude | ⚠️ Correct but crude. It never shows the age-adjusted hero, so judges see two different "Lapland" numbers. |

## 3. Caveat check (same screen as the number?)

| Locked rule | Status |
|---|---|
| Hero labelled chart estimate / age-adjusted / not stage-adjusted / not survival | ✅ Chip and full caveat are on the hero card. |
| 13.5 vs 46: dx→surgery, 2018–mid-2022, surgical minority, ≥25% same-day | ✅ On the signal card and the Surgery map layer. ❌ **Missing** in the analyst "widest gap" answer (it says "surgical patients only, ~11%" but not same-day) and in Simulator "Assumption A" (no same-day note; the slider can show 13.5 → 0 d). |
| THL 21/2016 shown as outdated; day-28 and 80% are Tasan design choices | ✅ Everywhere. Over-done: the same two sentences appear about 12 times, which buries everything else. |
| No unlabelled EXAMPLE or synthetic data | ✅ |
| T3 leads, T1/T2 alongside | ✅ (and repeated in full in the Simulator section) |
| Lapland county view: age-adjusted figure | ❌ The county panel shows only crude 18.5%. The hero 16.2% (men) is not on the map screen the demo uses. |

## 4. Cold walk-through: non-technical county director, no presenter

| Clock | What they see | Got it? |
|---|---|---|
| 0:00–0:15 | Key message: "No county publishes whether lung-cancer patients start treatment within six weeks…" | The *missing-data* message lands. The *gap* is not in the headline sentence. |
| 0:15–0:45 | Hero card: a 30-word headline label, then 4 big numbers, then a 90-word caveat | Gap understood ("Lapland men ~16% vs ~30%"). The caveat paragraph is skipped. |
| 0:45–1:10 | Crude secondary block, then "2 · Where": yellow THL box (3 near-identical caveat sentences), then 4 signal cards | Lost. Four competing numbers. "SIGNAL · LUNG_TREATED_WITHIN_2_MONTHS" is developer text. |
| 1:10–1:40 | Map defaults to surgery days; Lapland is green and ranked 22nd = best | **Contradiction with the hero.** A director would conclude Lapland is doing well. |
| 1:40–2:30 | "3 · What to do": a 130-word lead paragraph, then the T3 card with a 180-word paragraph, then KPIs and the caveat twice | Knows the action is "Tasan clock + nurse navigator". |
| ~2:30 | Cost range, Owner role, Signer, Stop/go | **"What to sign on Monday" is reached only now.** |

**Result:** gap ✅ (<45 s). Where it sits in the pathway ⚠️ (the map is not in the guided path and opens on the wrong layer). Monday action ⚠️ (named by ~1:40; the signer and cost appear at ~2:30). **Fails the 2-minute test unassisted**; it passes only with a presenter driving the exact clicks below.

Jargon on screen: YTA, MDT, SBRT, EBUS, ECOG/G8/CFS, HILMO, NSCLC, "Taulukko 4.1", "Kuva 16", snake_case ids (`colorectal_screening_share`, `referral_within_3d_share`), source-id chips (`lung-2026-t11`), "Open 16", "Online LLM (not configured)".

## 5. What is broken or fragile

1. Analyst "Impact of T3" prints raw JSON (`src/lib/analyst.ts:311–315`, `JSON.stringify(rec.evidence)`).
2. Pilot brief renders literal markdown markers and an internal generator note.
3. Map default layer contradicts the hero (surgery days; Lapland "best").
4. Pathway "No national median" contradicts the 37 d shown on the signal card.
5. The guided path's step 2 skips the map. Step 4 ends on an off-message analyst answer.
6. Simulator surgery slider can show "13.5 d → 0 d".
7. Reload with no network fails (no service worker). The local `dist` fallback works.
8. `favicon.ico` 404 (console error, cosmetic).
9. Freeze the build by Sunday 10:00 and do not redeploy after the rehearsal. The URL is claimed and permanent.
10. Page length is 19.6k px desktop and 40.9k px mobile. T3/T1/T2 are rendered in full twice: KeyMessage section and Simulator section.

## 6. Top 5 fixes, ranked by score gain

**1. Make "Start here" the 90-second story, and point the map at the hero (Execution 3→5 and Clarity 3→5 hinge on this; about +4 pts).**
- `src/content/key_message.json`: set `spotlight_stage` to the treatment stage and `spotlight_indicator_id` to `lung_curative_share`, so the map opens on **Treat** (Lapland red, ranked 1st = lowest).
- Fix it in `scripts/extract_team_data.py` too, or the next `npm run sync` reverts it.
- In `StartHere.tsx`:
  - Step 2: scroll to `#map` with layer Treat and Lapland selected.
  - Step 3: scroll to the T3 **Cost range / Owner role / Stop-go** block, not the T3 title.
  - Step 4: open the **Pilot brief** instead of Analyst + Simulator.
- Make the map heading dynamic: "Where the wait is too long" is wrong on the Treat layer. Use "Who reaches curative treatment".

**2. Fix the analyst's off-message and broken answers (removes the two worst judge-click traps).**
- `src/lib/analyst.ts`, "widest gap" intent: answer with the hero (men ~16.2 vs ~29.8, chart estimate, CIs do not overlap; women ~23.1 vs ~39.7). Mention Sotkanet 13 only as "all-specialty context".
- Add the ≥25%-same-day caveat wherever 13.5 vs 46 is quoted.
- Lines 311–315: render `rec.evidence` as a bulleted claim + source title list, not `JSON.stringify`.
- "How does this map to Goal 3?": list only T3/T1/T2. Drop longlist items, and never badge a "(Goal 2, secondary)" item GOAL 3.
- `Pathway.tsx`: remove the **GOAL 3** badge from "Primary → specialist referral (all specialties)". It is not a Goal 3 indicator.
- Remove the default auto-answer, or make it the hero answer.

**3. Remove the number contradictions.**
- `scripts/extract_team_data.py:547` → `regions.json`: replace "No national median was published in Taulukko 4.1" with "National median 37 d (IQR 0–56, report text p.27); counties not published — YTA only".
- `Pathway.tsx`, Treatment step for Lapland and Vantaa-Kerava: add the age-adjusted line "men ~16.2% / women ~23.1% (chart estimate)" under the crude bar, so the demo screen shows the hero number.
- Format CIs with one decimal everywhere: 29.0 and 47.0, not 29 and 47.
- Stage-missing card: move the "CHART ESTIMATE" chip from the 47.7% headline to the "22–68% by county" sentence.
- `Simulator.tsx` Assumption A: add the same-day caveat line and clamp the result display at the published Q1, or hide the surgery slider.

**4. Cut density (Clarity).**
- `Simulator.tsx`: delete the second full rendering of T3/T1/T2 and keep only the sliders.
- Show the THL caveat once per section as a one-line chip ("6-week reference: THL 21/2016, marked outdated · day-28 and 80% are Tasan design"), with the long CAVEAT text behind "Details". It is currently repeated about 12 times.
- Collapse the three non-hero signal cards (2-month, 1-yr survival, stage missing) behind "More public signals".
- Replace developer labels: `SIGNAL · LUNG_…` → plain titles; `(colorectal_screening_share)` → drop; "Open 16" → "Show Kymenlaakso"; hide "Online LLM (not configured)".
- Key message headline: lead with the gap ("Men in Lapland: about 16% reach curative lung-cancer treatment; Vantaa-Kerava about 30%. No county can see its own 6-week clock. Tasan is that clock."), keeping chips.
- T3 card: put a 4-line "Monday card" above the 180-word paragraph (Signer · Cost/90 d · First 30 days · Day-90 stop/go).

**5. Harden the demo itself (Execution).**
- Pilot brief renderer (`PilotBrief.tsx`): strip leading `>` and `##`, render "⚠ DRAFT – not signed" as a badge, and drop the "Generated from top3.json by scripts/gen_pilot_brief.py…" line.
- Add `public/favicon.svg` (kills the only console error).
- **Freeze the build after Sunday's 10:00 rehearsal.** The URL is already claimed.
- On the demo laptop, pre-open `app/dist-offline/index.html` from `file://` in tab 2 (re-verified 20:05 EET: zero external requests, no JS errors).
- Have a second team member drive the run-of-show once. Re-record `backup_demo_90s.webm` after the freeze; the current one is from the 19:52 build.

Expected after fixes 1–5 plus one rehearsal by a second driver: Execution 5, Clarity 5 (+10 pts on the 100-pt formula). Fixes 1–2 alone: Execution about 5 if rehearsed, Clarity stays 3 (+6).
