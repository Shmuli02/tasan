# Pitch script: Tasan (DECISION 3: one number, one county, one ask)

**Event:** Junction 2026, AstraZeneca "Equal Care Across Finland," Sun 15 Nov 2026, 14:00 Europe/Helsinki. Judges: Hanna Rusila, Laura Aaltonen (Marketing); Joanna Tuormaa (Business Excellence).
**Rewritten:** Sat 14 Nov, 20:15 EET, from `PLAN.md` DECISION 3 and `review/WIN_PLAN.md`.
**Shape:** 2:00 spoken + 1:00 demo = **3:00**. One number, one county (Lapland), one ask (sign the 90-day pilot).

**Locked wording:**
- **People number, verbatim (the steering message):** "About 65 more lung cancer patients a year would get curative treatment if every below-average county reached the national rate (Cancer Registry counts 2019-2023; illustrative, not stage-adjusted)." Lapland: **about 12 a year**. Source: `data/hero.json` → `people_number`.
- **Proof:** age-adjusted curative-treatment share, men, chart estimate (Kuva 16): Lapland about 16.2% [12.7–20.4] vs Vantaa-Kerava about 29.8% [24.2–36.1]. Not stage-adjusted, not survival. Women: about 23.1% vs about 39.7%.
- **Cost:** staff cost only, estimate, 90 days. Lapland T3 clock is €20,339–€23,988 (`recs/pilot_brief.md`, `recommendations.json`). The full Lapland brief incl. the Oulu-board coordinator (€23,857–€28,474) is for Q&A only.

**Off the spoken pitch (Q&A only):** 13.5 vs 46 days; Kymenlaakso; T1 fast track; T2 Oulu board / radiotherapy arm; crude 18.5 vs 35.6; colorectal screening.

**Never say:**
- "lives saved", "deaths prevented", "patients denied treatment"; any exact people number (always "about").
- That AstraZeneca has, runs or funds any pilot with a Finnish county. None exists that we know of. Our ask is for a *new* follow-up, which the challenge brief invites.
- The "17% earliest stage" figure.
- "The official target is day 28 / 80%".
- "16.2% of Lapland patients" (it is men, and a chart estimate).
- Any promise to move 16 → 30.
- Any euro figure without "staff cost only, estimate".

---

## Spoken script with timings

| Clock | Block | Speaker | Say (verbatim) | On screen |
|---|---|---|---|---|
| 0:00–0:20 | **Hook + people number** | A | "Same cancer, different postcode. About 65 more lung cancer patients a year would get curative treatment if every below-average county reached the national rate. That's Cancer Registry counts for 2019 to 2023. It's illustrative, and it isn't stage-adjusted. About 12 of them a year are in Lapland." | Slide: "≈ 65 / year · Lapland ≈ 12 / year". Footer: "Tasan's arithmetic on Cancer Registry Taulukko 11 counts, 2019–2023 · crude · illustrative · not stage-adjusted · not lives saved" |
| 0:20–0:40 | **Proof** | B | "And it isn't just age. Age-adjusted, about 16 in 100 men with lung cancer in Lapland have a curative-treatment record within a year, against about 30 in 100 in Vantaa-Kerava. That's a chart estimate from the 2026 Cancer Registry report. The intervals, about 13 to 20 and 24 to 36, don't overlap. Women show the same gap. It's not survival." | Slide: men 16.2 [12.7–20.4] vs 29.8 [24.2–36.1]; women 23.1 vs 39.7 in small type. Label "chart estimate · age-adjusted · not stage-adjusted · not survival" |
| 0:40–0:55 | **Why it persists** | A | "Goal 3 of Finland's cancer strategy says patients must start treatment within the target times. Today no county can see that clock for its own patients. Tasan is that clock." | Slide: Goal 3 wording, strategy p. 5 |
| 0:55–1:55 | **Demo (60 s)** | C drives, A speaks | See the run-of-show below | Live app |
| 1:55–2:35 | **Lapland pilot** | A | "Lapland can start on Monday. The chief medical officer signs a 90-day pilot: one nurse navigator and half an analyst. Staff cost only, estimate: about twenty to twenty-four thousand euros. In the first 30 days we measure Lapland's own baseline and check the registry against the hospital's records. After that, every patient with no treatment decision by day 28 goes to the navigator. On day 90 the county decides go or stop. Day 28 and the 80 percent bar are our design choices. The six-week reference is a THL 2016 document that is marked outdated." | Slide: Lapland card. Signer role; "€20,339–€23,988 · staff cost only, estimate · 90 days"; day-90 stop/go; "DRAFT, not discussed with the county" |
| 2:35–2:55 | **Ask** | A | "Your challenge asks for a follow-up with a Finnish wellbeing services county. Our ask: help us put this brief in front of Lapland's chief medical officer. Ninety days, one clock, one nurse. Tasan, koska hoito ei saa riippua postinumerosta." | Hand over the printed Lapland brief (if printed) |
| 2:55–3:00 | Buffer | — | Stop. No new numbers. | — |

Spoken words outside the demo: 271 (counted in STORY_2MIN.md), which is about 2:00 at a calm pace. If a rehearsal runs long, cut "Women show the same gap" and "In the first 30 days … records" first.

---

## Demo run-of-show (60 s): three wow moments

**State of the app checked 14 Nov 20:12 EET (live bundle `index-BjLwWtRE.js`).**
- **Missing: day-28 clock.** There is no live or animated clock; "day-28" exists only as text on the T3 card.
- **Partial: AI refusal.** There is no LLM ("Online LLM (not configured)"). The offline matcher gives an honest no-data answer to a six-week question. It does *not* refuse "Will this save lives?" (it gives "No direct match") or "Which drug should Lapland use?" (it dumps Lapland's signals).
- **Missing: AI-drafted brief for a judge-picked county.** "Draft a pilot brief for Kainuu" returns Kainuu's signal list, not a brief. "Show brief" renders the static Kymenlaakso + Lapland brief, still with raw markdown markers.
- **Not in the app: the people number.** "65 / 12" does not appear on screen yet. Say it from the slide.

The **TARGET** column assumes the builder ships WIN_PLAN M3/M5 and the clock before the 11:00 freeze. **Re-verify at the 12:00 rehearsal.** Use the **TODAY** column for anything that is not working then.

| Clock | Wow | TARGET click / prompt (only if verified at 12:00) | TODAY on the live build (works now) | Say |
|---|---|---|---|---|
| 0:55–1:10 | **1. Day-28 clock** | Click the Lapland clock widget, then **Start**: a patient timeline runs to day 28 and the alert goes to the navigator | **Start here** → press **3** → **Close**; point at the T3 card line "If there is no treatment decision 28 days after referral arrival, an alert goes to the named nurse navigator" | "Every lung patient's clock starts when the referral arrives. On day 28 with no treatment decision, the nurse navigator gets an alert and owns that patient." |
| 1:10–1:30 | **2. AI refuses a no-data question** | Ask box, type **"How many lung cancer patients in Lapland started treatment within six weeks last year?"** → refusal card naming the missing statistic | Scroll to **Ask about the gap** (or top bar **Analyst**). In the text box type **"How many patients in Lapland start treatment within six weeks?"** → **Ask**. Answer title: "No county publishes 6-week compliance". **Read only the title and first sentence**; the answer goes on to mention the surgery table, which is off-pitch. | "We asked it something nobody in Finland can answer, and it says so. No county publishes whether patients start treatment within six weeks. That missing number is the pilot." |
| 1:30–1:55 | **3. AI drafts the brief for the judge's county** | Ask a judge: "Pick a county." Brief dropdown → that county → **Draft** → one-page brief (signer role, 90 days, KPIs, "staff cost only, estimate", DRAFT) | **Not available.** Scroll to **Pilot brief** → **Show brief**; scroll to "Lapland" and point at the signer, cost and stop/go. Do **not** ask a judge to pick a county. | TARGET: "It drafts the same brief for any county: here's Kainuu, signer as a role because we haven't verified the name." TODAY: "This is Lapland's one-page brief: signer, cost, day-90 stop/go. The same template works for every county." |

**Prompts that must never be typed on the current build:** "Will this save lives…" (generic no match), "Which drug…" (no refusal, dumps signals), "Draft a pilot brief for …" (returns a signal list), and the "Impact of …" chip (raw JSON).

**Do NOT click during the pitch:**
- The map's default **Dx→Tx / Surgery** layer: it colours Lapland green (13.5 d) and reads as "Lapland is best".
- Any **Analyst** chip. "Where is the widest gap?" answers *primary → specialist referral*, and "Impact of …" prints raw JSON.
- **Simulator** sliders (the surgery slider can show 13.5 d → 0 d).
- **Show brief**: it renders raw markdown until the builder fixes it.
- Re-check this list after the builder's next deploy.
- Any Analyst prompt other than the six-week prompt above (today's build).
- (Unchanged from before:) map default layer, Analyst chips, Simulator sliders. Use "Show brief" only for the Lapland section, and only in TODAY mode.

---

## Demo failure fallback (in this order; never improvise numbers)

**Order:** (1) live URL → (2) offline single file `app/dist-offline/index.html` → (3) screenshots, then the backup recording.

**1. Live URL (primary).** https://petaled-trowel-90.beacon.host/ is claimed and permanent. Load it in tab 1 before going on stage, scrolled to the top. If it fails to load or a click hangs for more than 3 s, go to step 2. Do not retry the reload on stage.

**2. Offline single-file build.** Re-checked 14 Nov 20:05 EET: opened from `file://` with all network blocked, there were zero external requests and no JS errors, and the hero, Start here and Map → Treat → Lapland all work.

*Prepare before Sunday 13:30:*
1. Copy `/workspace/junction-new/app/dist-offline/index.html` onto the demo laptop's Desktop. As a fallback, copy `tasan-offline.zip` from the same folder and unzip it. Do not rename it.
2. Open Chrome, press **Ctrl+O** (Mac: **Cmd+O**), choose `Desktop/index.html` and press **Open**. You can also drag the file into a Chrome window, or type `file:///` plus the full path in the address bar. Linux: `google-chrome ~/Desktop/index.html`.
3. Check the address bar starts with `file://`. Check that the hero card says "about 16.2%".
4. Leave this as **tab 2**, scrolled to the top, next to the live tab.

*On stage:* switch to tab 2 (**Ctrl+2** / **Cmd+2**) and run exactly the same clicks. Say nothing about the switch.

**3. Screenshots, then the backup recording.** Use these if the laptop or browser itself fails. Speaker C opens the stills on the backup machine, in this order, speaking the 90-second lines over them:
1. `pitch/app_review/13_start_step1.png` (hero)
2. `14_demo_map_treat_lapland.png` (map, Treat, Lapland). Same screen offline: `15_offline_file_map_treat.png`.
3. `13_start_step3.png` (T3 card)
4. `12_pilot_brief.png` (pilot brief)

If there's time, play `pitch/app_review/backup_demo_90s.webm` (78 s, silent, 1280×800) muted while speaking the same lines. Re-record it after the Sunday build freeze; the builder's fixes will change the screens.

**Nothing on screen at all:** say "The working product is a county extract of four dates — referral arrival, first visit, queue date, first treatment — a day-28 alert, and a named navigator. The first real extract is week 1 of the pilot." Then go to the Ask.

---

## Run-of-show (who speaks)

| Time | Block | Speaker | Screen |
|---|---|---|---|
| 0:00–0:20 | People number | A (fill name) | Slide: ≈ 65 / year · Lapland ≈ 12 |
| 0:20–0:40 | Proof: men 16 vs 30 | B (fill name) | Slide: Kuva 16 chart estimate |
| 0:40–0:55 | Goal 3, missing clock | A | Slide: strategy p. 5 |
| 0:55–1:55 | Demo: clock → refusal → brief | C drives, A speaks | Live URL → offline file → stills/recording |
| 1:55–2:35 | Lapland pilot + cost | A | Slide: Lapland card |
| 2:35–3:00 | Ask | A | Printed brief |

**Backup:** if one speaker is late, A covers everything except the demo. If the demo fails mid-click, C goes to the fallback and A continues the spoken lines without new numbers.

## After the three minutes
Answers come only from `JUDGE_QA.md`. Kymenlaakso, 13.5 vs 46 days, T1 and T2 live there. If a number is not in `JUDGE_QA.md`, `data/hero.json` or the recs files, say so.
