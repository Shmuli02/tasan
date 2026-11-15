# APP_SCORES — judge-eye scores of the live Tasan app

Scale: 0–5 per criterion. Points = weight × score / 5. Total out of 100.

---

## Sat 14 Nov 2026, 20:31–20:36 EET — baseline (JN Pitch & Judge)

**Build tested:** live https://petaled-trowel-90.beacon.host/ , bundle `index-CpUsrW6c.js`, deployed 20:32:02 EET (`app/deploy-result.json` 20:32:06). The app shows no version or build stamp.
- The 20:21 build (`index-T34gtaTo.js`) was live when the test started. It was replaced mid-test. Its screenshots are in `pitch/app_review/2031/`, kept for the record only.
- All scores are for the 20:32 build. Its screenshots are in `pitch/app_review/2033/`.
- **Latest Builder milestone in STATUS.md:** 20:21, "Visual-first HERO". It says items 1–3 (day-28 clock, pilot brief, refusals) are "not yet". STATUS.md has no entry yet for the 20:32 deploy, which added the county panel and the day-28 clock.
- **Offline fallback:** `app/dist-offline/index.html` was refreshed at 20:32. The backup recording `backup_demo_90s.webm` is from 19:59 and shows an old build that no longer exists.

**Method:** headless Chrome at 1280×800 and 390×844.
- Clicked: hero, Sources and its Technical toggle, all 23 map areas, the county panel, the clock (Play → day-28 alert → Continue → Replay), FI/EN, and the `?county=21` deep link.
- No console errors. Load time 2.2 s; network idle at 3.3 s.

### What the app is now
The app is now a single screen:
- **First view:** an age-adjusted curative-share map (Lapland dark red) and a large "~65 more lung cancer patients a year could get curative treatment". Below that: "Lapland: ~12/yr".
- **Clicking a county** opens a panel with:
  - the crude share against the national 27.0%;
  - an **EXAMPLE DATA "Day-28 clock"** for a made-up 14-patient queue. It pauses on a "DAY-28 ALERT — Patient #7, Blocker: CT slot, Navigator: assigned" card, and after **Continue** says "treatment started on day 40 (by week 6)".
- **Removed from the UI:** the recommendations, owners, costs, pilot brief, analyst, Start here, pathway and simulator. The code is still in `src/components/`, but `App.tsx` renders only `Screen1`.

### Scores

| Criterion | Weight | Score | Points | Why |
|---|---|---|---|---|
| Actionability | 30 | **1** | 6 | The only action on screen is "the navigator steps in", inside a made-up clock. No signer, owner, cost, 90-day plan, stop/go or pilot brief is reachable. The recs data is in the bundle but never rendered. A director cannot say what to do on Monday. |
| Insight | 25 | **3** | 15 | One clear people number plus a map that shows Lapland worst: a strong 10-second read. But the map hover gives a value only for Lapland (16.2%) and Vantaa-Kerava (29.8%). No other county explains itself, and the insight stops at "there is a gap". |
| Data quality & transparency | 20 | **2** | 8 | The numbers are correct (65, 12, 18.5, 27.0, 35.6, 19.3, 18.9, 33.0, 16.2, 29.8) and two linked sources are on screen. But: (a) **17 of 21 coloured counties** say "No separate figure for this county is in the facts pack", although Table 11 publishes all of them. (b) The map shows **men-only** chart estimates without saying "men" or "chart estimate". (c) The people-number caveat is shortened and sits behind a toggle (see the checklist). (d) "could get curative treatment" overstates "would have had a curative-treatment **record**". (e) The 6-week / day-28 clock has no THL-2016-outdated or "Tasan design choice" note. |
| Execution | 15 | **3** | 9 | Fast, no errors, the clock works, FI/EN works, deep link works. But: (a) the footer badge **"AI on Verda · EU-hosted" claims an AI that the app does not have**, and a judge will try to find it. (b) The Helsinki-region inset covers the west coast (Ostrobothnia and part of Southwest Finland) at 1280×800. (c) The FI clock button reads "Toista" (Replay) before anything has played, because state carries over. (d) The jargon "facts pack" appears on screen. |
| Clarity | 10 | **4** | 8 | The cleanest version yet: one number, one map, one county click. It loses a point because two different Lapland numbers (16.2% hover, 18.5% panel) appear together and a non-expert cannot tell why. |
| **Total** | 100 | | **46** | |

### Gates

| Gate | Status | Evidence |
|---|---|---|
| Sources for every claim | **FAIL (close)** | The hero and the crude shares are linked to Cancer Registry Table 11 / Figure 16. The "AI on Verda" claim, the men-only map basis and the 6-week / day-28 clock have no source or label on screen. |
| Goal 3 indicator | **FAIL** | "Goal 3" appears nowhere on screen, in EN or FI. The only target-time measure, "Started within 6 weeks", is inside the example clock and is not linked to the strategy indicator. |
| Concrete actions | **FAIL** | No owner, signer, cost or plan is rendered (see Actionability). |
| Working demo | **PASS** | Live HTTP 200, zero JS errors, offline build refreshed at 20:32. The backup video is stale. |

### Acceptance checklist

| Item | Status | Notes |
|---|---|---|
| Live day-28 clock | **PASS** | Play → pauses on the DAY-28 ALERT (#7, "Blocker: CT slot") → Continue → "#7 treated day 40 (by week 6)". Within 6 weeks: 29% → 36% → 57%. Labelled "EXAMPLE DATA · A made-up list, not real patients". Missing: a THL-outdated / design-choice note. Screenshots: `04_clock_*`, `05_clock_after_continue_*`. |
| AI drafts a pilot brief for a judge-picked county | **FAIL** | No AI input exists anywhere: 0 inputs or textareas, no chat, no brief button. |
| AI refuses no-data questions ("Will this save lives?", drug questions) | **FAIL (cannot test)** | There is no AI surface. Kainuu and Åland correctly show "No public data" on the map. |
| 65 / 12 on screen with its exact caveat | **PARTIAL** | 65 and "Lapland ~12/yr" are on the hero, and 12 is on the Lapland panel. The caveat is **not exact** and is **behind the Sources toggle**. The screen shows only "(Cancer Registry 2019–2023, illustrative, not stage-adjusted)" and "Illustrative calculation, not stage-adjusted, not survival". It drops the facts.json caveat parts "not a published estimate and not causal", "crude shares (not age-adjusted)", "national average is not a clinical optimum" and "Never translate into lives saved". The 20:21 build showed the full caveat; the 20:32 build lost it. |
| Earlier fix 1: map opens on hero / Start-here story | **PARTIAL** | The map opens on curative share with Lapland red (done). Start here was removed, so "who signs and what it costs" can no longer be reached at all. |
| Earlier fix 2: analyst off-message / JSON dump | **MOOT** | The analyst was removed. The trap is gone, but so is the feature. |
| Earlier fix 3: number contradictions | **PARTIAL** | The 37-day and surgery-layer contradictions are gone with the pathway. Lapland now shows both age-adjusted (hover) and crude (panel) figures, labelled. New contradiction: 17 coloured counties say "no figure". |
| Earlier fix 4: cut density | **DONE** | Possibly overdone: the actions were cut with it. |
| Earlier fix 5: harden demo | **PARTIAL** | No console errors, offline build refreshed, URL claimed. Not done: build freeze, and re-recording the backup video (19:59 is stale). The pilot-brief renderer was removed. |

### Changed since last score
The last score was `APP_REVIEW.md`, build `index-BOMKJaff.js` at 19:52, which scored only Execution 3 and Clarity 3.
- **Clarity:** 3 → 4. The 19,586 px page became one screen.
- **Execution:** stays at 3. The old traps are gone, but there are new ones: the AI badge with no AI, and the "no figure" counties.
- **Actionability:** collapses, because the T3 card (owner, cost, stop/go) and the pilot brief were removed from the UI.
- **New:** a working example day-28 clock, and the 65/12 people number on the hero.

### 3 biggest fixes for the Builder, ranked by weighted score gain

**1. Put the ask back on the county panel (Actionability 1→3/4, about +12 to +18 pts; flips the "Concrete actions" gate).**
- In `app/src/components/CountyPanel.tsx`, add a "Monday card" between the crude bar and the clock. Source it from `src/content/recommendations.json`, T3:
  - Signer: Johtajaylilääkäri
  - Owner: nurse navigator, 1 FTE
  - Cost: €20,339–€23,988 per 90 days, sourced staff cost only
  - First 30 days
  - Day-90 stop/go
- Add a button "Open pilot brief" that renders `recs/pilot_brief_lapland.md` as clean markdown, with no `>` or `##` and a "DRAFT – not signed" badge. Show it for Lapland and Kymenlaakso. For other counties, use `recs/pilot_brief_template.json` with that county's number.
- In `Screen1.tsx`, add one line under "Lapland: ~12/yr": "The ask: a 90-day day-28 pilot in Lapland".

**2. Fix the data and caveats on screen (Data quality 2→4, about +8 pts; flips the "Sources" and "Goal 3" gates).**
- `CountyPanel.tsx` / `lib/facts.ts`: replace "No separate figure for this county is in the facts pack" with the Table 11 crude share. All 21 counties are in `data/csv/lung_report2026_treatment_by_wsc.csv`. Add them to facts.json or read the CSV.
- `FinlandMap.tsx`: show the hover % for every county from the Figure 16 CSV.
- Map caption in `Screen1.tsx`: "Men, age-adjusted, chart estimate (Cancer Registry Fig. 16)".
- Under the 65, show the full facts.json caveat in small print, not behind the toggle.
- Change "could get curative treatment" to "would have had a curative-treatment record".
- `ExampleClock.tsx`: add a chip, "Goal 3: treatment within target times · 6-week reference THL 2016 (marked outdated) · day-28 and 80% are Tasan design choices".

**3. Ship the AI or remove its badge (Execution 3→4, Actionability +1, about +9 pts; checklist items 2–3).**
- Add an "Ask Tasan" box to the county panel, backed by the grounded Verda proxy over `data/facts.json`. It should:
  - pre-fill "Draft a pilot brief for {county}" and output the `pilot_brief_template.json` fields with a citation for each;
  - hard-refuse `no_public_data` facts, "Will this save lives?" and drug questions with a fixed line: "No public data / Tasan does not estimate lives or drug effects".
- If it is not live and passing the trick suite by the freeze, delete the "AI on Verda · EU-hosted" footer in `Screen1.tsx` (or `App.tsx`). A visible claim with nothing behind it is a credibility hit.

Minor: shrink or move the Helsinki inset in `FinlandMap.tsx` so it stops covering the west coast. Reset the clock state per county; the FI label reads "Toista" before any play. Re-record `backup_demo_90s.webm` after the freeze.

---

## Sat 14 Nov 2026, 20:53–20:59 EET — re-score, 6-tab build (JN Pitch & Judge)

**Build tested:** live https://petaled-trowel-90.beacon.host/ serves `assets/index-BRsJI1xf.js`. Confirmed in the live HTML and in the page's script src. Built 20:52:02 EET; `app/deploy-result.json` 20:52:08. The app shows no build stamp. The offline build `app/dist-offline/index.html` was refreshed at 20:52.

**Screenshots:** `pitch/app_review/2054/`. They cover all 6 tabs, the Overview at 1280×800, 1440×900 and 1920×1080 plus mobile, the pilot brief modal, Ask Tasan chips and typed questions, the age-adjusted toggle, Sources, a fact chip, a map click and FI.

**Method:** headless Chrome. No JS errors. Load to network idle in 3.8 s. The Ask panel makes no network calls; it is bundled and labelled "EXAMPLE CHAT".

### What is on screen
- **Overview:** 4 KPI tiles: ~65/yr, Lapland 18.5% vs 27.0%, ~12/yr, and "0" public reports with a DATA GAP badge.
- **Map and ranking:** a crude-share map with a ranked list of 21 counties, plus an age-adjusted toggle that switches both to men, chart estimate.
- **Age-adjusted card:** confidence intervals for men and women.
- **"Where the data goes dark" strip.**
- **Fact-ID chips:** each opens a popover with source and caveat.
- **Ask Tasan side panel:** example chat.
- **Pilot tab:** "Open pilot brief", a full Lapland 90-day brief with problem, action, owners, cost, KPIs and day-90 stop/go.
- **Other tabs:** Counties, Pathway, Tasan Live and Simulate are **"COMING" placeholders**.

### Scores (delta from the 46 at 20:32)

| Criterion | Weight | Score | Points | Δ | Why |
|---|---|---|---|---|---|
| Actionability | 30 | **3** | 18 | +12 | The Lapland brief is signable: signer, navigator line manager, €20,339–23,988 per 90 days with its basis, 4 KPIs, a stop/go rule, and a "DRAFT – NOT SIGNED" banner. Still missing: the ask card on Overview (planned), and any brief for another county. The tested build also has no day-28 clock, because Tasan Live is a placeholder. |
| Insight | 25 | **4** | 20 | +5 | People number, full crude ranking, an age-adjusted confirmation with CIs that don't overlap, and "where the data goes dark". A judge sees the gap and its robustness in one screen. It is not 5: no "why" beyond the data-gap strip, and no county drill-down. |
| Data quality & transparency | 20 | **4** | 16 | +8 | 29 numbers spot-checked, all traced (table below). COMPUTED / CHART ESTIMATE / DATA GAP badges and fact-ID chips are on every tile. Refusals cite `nodata_*` facts. It is not 5 because the hero tile drops the benchmark condition, the "0" tile reads as a result, and the THL 6-week line has no "marked outdated" note (details below). |
| Execution | 15 | **2** | 6 | −3 | See the list of breaks below. |
| Clarity | 10 | **3** | 6 | −2 | At 1920 the Overview passes the 2-minute test: message read in about 20 s, Lapland in about 30 s, brief in 2 clicks. At 1280 and 1440 it fails, because the map is unreadable and the bars overlap. Raw fact IDs (`people_number_national`, `…_vk_men`) and 5 tabs are jargon or dead ends for a director. |
| **Total** | 100 | | **66** | **+20** | |

**Execution breaks:**
1. **4 of 6 tabs are "COMING" placeholders**: Counties, Pathway, Tasan Live, Simulate. Pilot shows "COMING" next to "The brief is ready". Counties says "Click a county on Overview", but clicking a county there only moves the callout. That is a loop with no county view.
2. **Overview layout breaks at 1440×900 and 1280×800, which is most laptops.** The map shrinks to a thumbnail of Lapland's tip, and the ranked list overflows across the age-adjusted card, colliding with the ~29.8 marker. See `9_overview_1440x900.png` and `1_Overview_0.png`. It is clean only at 1920×1080.
3. **Ask Tasan does not auto-scroll.** "Where does data go dark?" and "Compare Kymenlaakso" do answer, but below the fold (`.msgs` scrollTop stays 0), so to a judge they look dead.
4. **"Draft a pilot brief for North Karelia" silently opens the Lapland brief.**
5. **"Is Lapland's surgery wait longer?" gets the curative-share answer**, which is off-topic.
6. **Esc does not close the brief modal.**
7. The **day-28 clock from the 20:32 build is gone** (regression).

**Data-quality issues (why not 5):**
1. The **~65 hero tile drops the condition** "if every below-average county reached the national rate". It reads as an unconditional "65 more could get curative treatment".
2. The full `hero.json` caveat is nowhere on screen. The fact-chip popover shows the shorter `facts.json` version.
3. The **"0" tile** ("Public reports of patients treated within 6 weeks: 0") reads as a result, not a data gap.
4. **"THL target: 6 weeks" has no "marked outdated (THL 21/2016)" note**, on Overview or in the Ask answer.
5. The national men line ≈24.9 comes from the Kuva 15 CSV / `data/app`, not facts.json. That is sourced but has no chip.

### "Every number sourced": spot-check, 29 numbers

| Number on screen | Found in | Result |
|---|---|---|
| 65, 12, 18.5, 27.0, 35.6, 16.2, 29.8, 23.1, 39.7, 12.7–20.4, 24.2–36.1, 131/710, 15.8–21.5 | facts.json and hero.json | ✅ |
| 18.9, 19.3, 33.0, 114/591, 16.3–22.7 | facts.json | ✅ |
| 24.9 (national men, age-adjusted) | `data/csv/lung_report2026_curative_agestd_national_chart_estimate.csv` (Kuva 15) and `data/app/README.md` | ✅ (not in facts.json) |
| 33.8% no record; €20,339–23,988; €3,174–4,048; €4,663–4,891; ×1.2314 | `recs/recommendations.json` / `recs/pilot_brief_lapland.md` with `recs/sources.md` (33.8 is also in `data/raw/keuhkosyoparaportti_2026.txt`) | ✅ (recs, not facts.json) |

**Verdict:** the claim holds for numbers. The exceptions are the wording and framing problems above (benchmark condition, "0" tile, THL note), not unsourced figures.

### People-number caveat vs `hero.json` people_number
- **On the tile:** "more lung cancer patients a year could get curative treatment · measured as a curative-treatment record in the Cancer Registry, 2019–2023 · illustrative, not stage-adjusted · COMPUTED BY TASAN · CRUDE".
- **`safe_wording_en`:** "…would get curative treatment **if every below-average county reached the national rate**, based on Cancer Registry counts for 2019-2023 (illustrative, not adjusted for stage)". → **The condition is missing on screen.**
- **`caveat`:** "not a published estimate and not a causal claim… crude… stage missing for 48%… benchmark is the national average, not a clinical optimum… does not say how many lives". → **Not on screen.** The chip popover shows the shorter facts.json caveat.
- **`do_not_say`:**
  - "lives saved" appears only inside the refusal ("No public source estimates lives saved…"). Acceptable, but the seeded question "How many lives would this save?" puts the phrase on the first screen.
  - "deaths prevented" and "patients denied treatment" do not appear.
  - Always "about": ✅ (~65, ~12, "about 16 vs about 30").

### Gates

| Gate | Status | Note |
|---|---|---|
| Sources for every claim | **PASS** | A chip or source is on every tile. The brief cites its cost basis. Minor: 24.9 has no chip. |
| Goal 3 indicator | **FAIL (planned)** | The THL 6-week target and the "no public reports" gap are on screen, but nothing names Goal 3. Goal 3 chip already planned. |
| Concrete actions | **PASS** | Via Pilot → Open pilot brief, or the "Draft Lapland pilot brief" chip: signer, owner, cost, KPIs, stop/go. Not on Overview; ask card already planned. |
| Working demo | **PASS (at risk)** | Live, no JS errors, offline refreshed 20:52. The layout breaks below 1600 px wide, so the demo laptop must run at 1920×1080. The backup video (19:59) is stale. |

### Acceptance checklist
- **Live day-28 clock: FAIL (regression).** Tasan Live is "COMING". The 20:32 clock is not reachable.
- **AI drafts a pilot brief for a judge-picked county: FAIL (planned).** Lapland only, and other counties silently get Lapland.
- **AI refuses no-data questions: PASS (bundled example).**
  - "Will this save lives?" → NO SOURCED ANSWER, `nodata_lives_saved`.
  - Osimertinib vs pembrolizumab → "Tasan does not advise on drugs or treatment choice".
  - Kainuu 6-week compliance → `nodata_regional_target_compliance`.
  - Live LLM refusals are planned.
- **65 / 12 on screen with exact caveat: PARTIAL.** Both numbers are on screen. The tile drops the benchmark condition, and the hero.json caveat is not shown.
- **Earlier 5 fixes:**
  1. Map leads with hero, Lapland darkest: ✅
  2. Analyst on-message and citing: ✅ (example)
  3. Contradictions: ✅ (16.2 vs 18.5 both labelled; the "no figure" counties are fixed, all 21 ranked)
  4. Density: partial (raw IDs, 4 empty tabs)
  5. Harden: partial (layout, no freeze, stale video)

### Changed since last score (46 → 66)
- **Up:**
  - The pilot brief is back and reachable (Actionability +12).
  - Full ranking, age-adjusted CIs and a data-gap view (Insight +5).
  - Sourced badges and chips everywhere, and the "no figure in facts pack" counties are fixed (Data +8).
- **Down:**
  - Execution: placeholder tabs, broken layout below 1600 px, the clock is gone.
  - Clarity: the 6-tab shell and raw IDs.
  - The AI badge problem is fixed, because Ask Tasan is honestly labelled EXAMPLE CHAT.

### 3 biggest fixes, ranked by weighted gain (excluding the planned ask card, Goal 3 chip and live LLM)

**1. Hide or fill the empty tabs, and put the day-28 clock back (about +8: Execution 2→3, Clarity 3→4, and checklist item 1 passes again).**
- In the tab bar (`App.tsx`, which renders `ComingTab.tsx`), remove Counties, Pathway and Simulate until they ship.
- Make Tasan Live render the existing `components/ExampleClock.tsx` with the EXAMPLE label. It worked at 20:32: Play → DAY-28 ALERT → Continue.
- On the Pilot tab, delete the "COMING" tag under "The brief is ready".

**2. Fix the Overview layout at 1280–1440 px (about +5: Execution +1, Clarity +1; removes the demo-laptop risk).**
- In `app/src/styles/overview.css`, the `@media (max-width:1440px)` and `(max-width:1600px)` rules for `.grid3` squeeze the map.
- Set `.mapcard { min-height: 520px }` and give the ranked list container (`RankedChart.tsx`) `overflow: hidden` with a fixed row height, so it cannot spill into the age-adjusted card.
- Or below 1600 px use `.grid3 { grid-template-columns: 1fr }` (stacked).
- Re-check at 1280×800 and 1440×900.

**3. Make the hero tile and Ask panel honest and visible (about +4: Data 4→5).**
- In `components/Overview.tsx:110`, add "if every below-average county reached the national rate (27.0%)" to the 65 tile. Put a "Caveat" link that shows the full `hero.json` people_number caveat.
- At line 165, replace the big "0" with "None published" (keep the DATA GAP badge).
- Add "(THL 21/2016, marked outdated · day-28 and 80% are Tasan design choices)" to the "THL target: 6 weeks" line.
- In `components/AskPanel.tsx`, scroll `.msgs` to the bottom after `push()`.
- For a "pilot brief for <county>" request where the county is not Lapland, reply "Only the Lapland brief is drafted so far" instead of opening Lapland's brief.
- Make Esc close `PilotBriefModal.tsx`.

**Risk flag for the coordinator, not scored:** the brief on the public URL names real Lapland officials as "Signer: Jyri J. Taskila" and "Navigator line manager: Henna Kauranen" while it says "NOT DISCUSSED WITH THE COUNTY". The names are sourced from lapha.fi. A judge may still ask "did they agree to this?". Safer: show the role ("Johtajaylilääkäri, Lapin hyvinvointialue") and keep the names in the printed one-pager only.

## Sat 14 Nov 2026, 22:34–22:45 EET — re-score, 3-tab build index-miU57519.js (deployed 21:46) (JN Pitch & Judge)

Tested live at 1280×800 (box browser), source in app/src checked.

**Score: 80/100 (+14 vs 66).** Actionability 4/5 (24), Insight 4/5 (20), Data quality & transparency 4/5 (16), Execution 4/5 (12), Clarity 4/5 (8).

### Gates
| Gate | Status | Note |
|---|---|---|
| Sources for every claim | **PASS** | Chips on every KPI tile. The popover shows Taulukko 11 + "Open source" link. Ask answers cite fact IDs. |
| Goal 3 indicator | **PASS** (was FAIL) | Overview: `Goal 3 · "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa"` (Strategy 2026–2035, indicator 3). |
| Concrete actions | **PASS** | Pilot tab: Lapland 90-day draft. Signer is the CMO, navigator line manager is the Acting Director of Nursing, €20,339–23,988 / 90 days, 4 KPIs, stop/go rule. |
| Working demo | **PASS** | 3 real tabs (Overview, Tasan Live, Pilot). No COMING tags. No errors. At 1280×800 the map and ranked list sit side by side with no overlap; the lower part of the list falls below the fold. |

### Acceptance checklist
- **Live day-28 clock: PASS (minor).** Tasan Live (EXAMPLE · simulated patients) has Play and Day-28 alert cards, ending at "6/14 → 9/14 started within 6 weeks (illustrative)" with Replay. The alert only auto-pauses for 2 s (TasanLive.tsx PAUSE_MS). There is no presenter Continue button, so the 20:32 "pause → Continue" beat is gone.
- **AI drafts a pilot brief for a judge-picked county: FAIL.** "Draft a pilot brief for North Karelia" replies "Opening the Lapland 90-day pilot brief" and opens Lapland. It is routed locally (askLocal.ts:149, roles.ts BRIEF_COUNTY_IDS = {"21"}) and never reaches the LLM. A judge will try this.
- **AI refuses no-data questions: PASS.** "Will this save lives?" gets "No sourced answer…". Osimertinib vs pembrolizumab gets "I cannot recommend a drug or treatment choice…" plus the nodata_comorbidity_adjusted cite. "Why is Lapland behind?" gives 18.5% (131/710, CI 15.8–21.5) vs 27.0% (4009/14873), with a not-stage-adjusted note.
- **65 / 12 on screen with exact caveat: PARTIAL→nearly PASS.** The 65 tile now carries the condition "if every below-average county reached the national rate" (the previous fix #3 is done). The full hero.json caveat (not published, not causal, crude, national average ≠ clinical optimum, never lives) is still not on the Overview.
- **Previous 3 fixes:** (1) empty tabs removed and clock restored ✅; (2) 1280–1440 layout ✅ (no overlap); (3) hero condition ✅, caveat link ❌.
- **New transparency nit:** the Ask panel says "Grounded in 81 sourced facts" but doesn't say whether an answer came from the live AI (Verda/EU proxy) or a bundled local route. The routed answers (brief, why, refusals) are local.

### Changed since last score (66 → 80)
- **Up:** Goal 3 on screen (gate now passes), the clock is back, the empty tabs are gone, the layout works at 1280, the hero condition is shown, and the live Ask streams with cites. That moves Act, Exec and Clarity up by 1 each.
- **Unchanged:** Insight 4 (Counties/Pathway depth was cut; the ranking and CIs remain on the Overview). Data 4 (caveat not shown, Ask source unlabelled).

### 3 biggest fixes, ranked by weighted gain
**1. Pilot brief for any judge-picked county, never a silent Lapland (about +6–9: Actionability 4→5, Execution helped).**
- In askLocal.ts:149, stop answering every brief request with Lapland.
- For non-Lapland counties, call streamAsk with mode "brief" and county = the id (askLlm.ts:159 already supports this), filling the recs template from that county's facts.
- Or pre-generate all 21 briefs into content/briefs/ and add them to BRIEF_COUNTY_IDS.
- Offline fallback: say "No pre-generated brief for North Karelia yet — here is the Lapland template" rather than silently swapping.

**2. Show the full caveat and label where each answer comes from (about +4: Data 4→5).**
- Add a "Caveat" link on the 65 tile that opens the full hero.json caveat (not a published estimate, not causal, crude, stage missing 48%, national average ≠ clinical optimum, not lives).
- In AskPanel, tag each reply "AI · Verda EU, grounded in facts" or "Bundled sourced answer".

**3. Harden the demo beat (about +3: Execution 4→5).**
- Make the Day-28 alert hold until the presenter presses Continue (not a 2 s auto-pause), so the story beat can't be missed at 32×.
- Freeze the build.
- Re-record the backup video (backup_demo_90s.webm from 19:59 is stale and shows the old UI).
- Check that the bottom of the ranked list reads cleanly at 1280×720 on the projector.

---

## Sat 14 Nov 2026, 22:57–23:09 EET — FINAL re-score, freeze build index-BKYLrLGu.js (JN Pitch & Judge)

**Build:** the live https://petaled-trowel-90.beacon.host/ serves `assets/index-BKYLrLGu.js`. I confirmed this from the live HTML.
- Built 22:56:20 EET; `app/deploy-result.json` 22:56:24.
- **Offline fallback = freeze build.** `app/dist-offline/index.html` and `tasan-offline.zip` are from 22:56:21 and contain the new strings ("How we built it", 0.739, 0.963).
- Tested from `file://` with the network switched off. It loads, shows no errors, and when the `/ask` worker call fails it falls back to the bundled answers.

**Screenshots:** `pitch/app_review/2258/`. They cover all 4 tabs at 1920×1080 and 1280×720 (live), Ask brief tests online (`live_q_*`) and offline (`offline_q_*`), the Caveat popover, the county ask card and Generate, and the Tasan Live alert and Continue.

### Verification of the Builder's claimed fixes

| Claim | Result | Evidence |
|---|---|---|
| Any-county brief, no Lapland fallback | **PARTIAL** | See notes below. |
| Caveat link on the 65 tile | **PASS** | "Caveat" opens the full `hero.json` people_number caveat, word for word: not published, not causal, crude, 48% stage missing, national average ≠ clinical optimum, does not say how many lives. |
| Source tags on Ask replies | **PASS** | Each reply carries chips, e.g. "Cancer Registry · T10", "No public data", "Bundled sourced answer". |
| Presenter Continue on the day-28 alert | **PASS** | Tasan Live (32×) pauses on each Day-28 alert with "Continue · Space or →". Continue resumes; the next alert pauses again. No errors. |
| "How we built it" tab with Verda results | **PASS** | See notes below. |

**Any-county brief, notes:**
- **Correct counties:** typed in Ask, these open a brief for the right county, online and offline: North Karelia (21.4%, 109/510, CI 18.0–25.1; men 17.6, women 27.3), Kainuu (20.8%, 47/226, CI 16.0–26.6, correctly crude only), South Savo (23.4%), Pirkanmaa (31.9%), Helsinki (33.0%; men 29.5, women 36.6) and Kymenlaakso (19.3%). Every number matches `data/csv/lung_report2026_treatment_by_wsc.csv` and the Kuva 16 CSV.
- **Åland / Ahvenanmaa (no data) and any unknown county:** reply "Opening the Lapland 90-day pilot brief" and open Lapland, online and offline.
- **Kymenlaakso, live:** streams raw JSON into the chat for about 15–40 s, then opens the brief.
- **"Generate pilot brief" on the Overview ask card:** for a non-Lapland county it only says "Draft brief for North Karelia not pre-generated yet".

**"How we built it", notes:**
- All 5 tiles trace to `verda/HOW_WE_BUILT_NUMBERS.json`, and the source chips match:
  - 0.739 = v2 held-out exact F1 (n=401);
  - regex 0.000 untuned v2;
  - day-28 alert 0.963;
  - $0.99 / $0.89 per 1k notes;
  - 14,970 notes/yr = 2,994 patients × 5 notes (assumption, labelled SKETCH);
  - 132+5 Twin jobs, ≈$0.07–0.08, total ≈$0.11;
  - ≈$5.88–6.88 = 3.77 + 0.11 + 2–3.
- Synthetic notes are labelled "SYNTHETIC · NOT A REAL PATIENT" on every card.
- Nothing contradicts facts.json or hero.json. The 2,994 patients/yr (Cancer Registry 2020–24) differs from 14,873/5 = 2,975 (2019–23), but the windows differ and the 2,994 is not shown on screen.
- Ask is labelled "EU-hosted"; Extract is labelled Finland (FIN-01). Both are consistent with the numbers pack.

### Scores (delta from the 80 at 22:45)

| Criterion | Weight | Score | Points | Δ | Why |
|---|---|---|---|---|---|
| Actionability | 30 | **4** | 24 | 0 | A signable brief for almost any county, typed in Ask. The Overview ask card updates per county (signer and owner role, cost, stop/go). It is not 5: the Generate button doesn't generate for non-Lapland counties, and Åland / unknown counties get Lapland. |
| Insight | 25 | **4** | 20 | 0 | Unchanged core: people number, ranking, age-adjusted CIs, data gap, Goal 3. "How we built it" adds credibility, not new insight. |
| Data quality & transparency | 20 | **5** | 20 | +4 | The full hero caveat is one click from the number. Source chips are on every tile and every Ask reply. More than 20 brief numbers re-checked against the CSV, all exact. Verda numbers are each traced to a file. Synthetic and SKETCH labels are present. |
| Execution | 15 | **4** | 12 | 0 | Continue works, the offline copy is the freeze build and works, no JS errors, 1280×720 is usable on all 4 tabs. It is held back by the wrong-county fallback, Kymenlaakso's JSON stream, and the layout break when the caveat popover is open (below). |
| Clarity | 10 | **4** | 8 | 0 | 4 real tabs. The "How we built it" fan of notes reads instantly. The Overview is dense but legible. |
| **Total** | 100 | | **84** | **+4** | |

### Gates
- **Sources for every claim:** PASS.
- **Goal 3 indicator:** PASS. The Overview chip quotes the strategy wording, Strategy p.5.
- **Concrete actions:** PASS. Ask card plus briefs for each county.
- **Working demo:** PASS. Live and offline (freeze build) both work.

### STAGE-BREAKING bugs (freeze criteria)

**1. Wrong-county output.**
- "Draft a pilot brief for Åland" (also "Ahvenanmaa", or any county name the parser does not know) replies "Opening the Lapland 90-day pilot brief" and opens **Lapland's** brief. This happens online and offline.
- Cause: `app/src/lib/askLocal.ts:147`. `briefTarget(q, countyId)` falls back to the UI county (Lapland by default), so `named.isLapland` comes out true.
- Fix: if no county is named in `q`, refuse with "No public data for Åland — no brief" or "Which county?" instead of using the UI default.
- **Stage workaround if unfixed:** only type mainland county names, never Åland.

**2. Layout broken at 1920×1080 while the caveat is open.**
- Clicking "Caveat" on the 65 tile expands the hero row. The map card shrinks and the ranked list spills out of its card: rows from Ostrobothnia to Vantaa-Kerava sit below the card edge (`live_1920_caveat_open.png`).
- Fix: show the caveat as an overlay popover (absolute position, z-index) in `Overview.tsx` instead of an inline expansion.
- **Stage workaround:** close the caveat again before talking about the map. 1280×720 is fine, because the page scrolls.

No crashes. No wrong or contradictory numbers found on screen. No unsourced or false claim a judge would catch.

### Post-freeze nice-to-have
- **Kymenlaakso brief (live only):** the LLM streams raw JSON (`{"status":"DRAFT",…}`) and bracketed fact IDs into the Ask panel for about 15–40 s before the formatted brief opens. Offline it opens the brief at once. Render a "Drafting…" placeholder instead of streaming the raw tokens (`AskPanel.tsx` stream handler). **Presenter: demo North Karelia, not Kymenlaakso.**
- **"Generate pilot brief" on the Overview ask card** says "not pre-generated yet" for non-Lapland counties, while Ask generates the same brief. Wire the button to the same `countyBrief` path.
- **Owner role "Acting Director of Nursing"** is copied from Lapland (vs. hoitotyön johtaja) to every county. Use "Director of Nursing (hoitotyön johtaja)" for counties where the acting status was not checked.
- **"vs regex 0.000"** on the Extract tile is true but selective: on v1, regex scored 0.960 vs Qwen 0.954. Say "untuned regex 0.000 on held-out v2" and have the v1 result ready for Q&A.
- **Tasan Live:** the "Without 6/14 → With Tasan 9/14" example (43% → 64%) sits beside "Model output ~33% (14–58); what-if ~52% (31–75)". Both are labelled and the example falls within the model ranges, but a judge may ask why they differ. Prepare a one-line answer.
- Esc to close modals, FI number formatting (18,5 %), and a fresh backup video of the freeze build.

### Changed since last score (80 → 84)
- Fixed: the full caveat is one click away; Ask has source tags; Continue is on the alert; any named mainland county gets its own sourced brief; "How we built it" with traced Verda numbers; the offline fallback is the freeze build.
- Still open: the Lapland fallback for Åland / unknown counties; the Generate button only works for Lapland.
- New in this build: the caveat-open layout spill at 1920, and Kymenlaakso's raw JSON stream.
