# Junction 2026 – AstraZeneca "Equal Care Across Finland" – NEW project (no reuse of Polku or any older work)
Goal: win. Judging Sun Nov 15 14:00 (Helsinki). Brief: CHALLENGE.txt / challenge.pdf
Criteria: Actionability 30, Insight 25, Data quality & transparency 20, Execution (live demo) 15, Clarity (<2 min) 10.
Must: sources for every claim; >=1 Goal 3 indicator of national cancer strategy 2026-2035; concrete recommendations; working demo.
Official resources: https://files.hackjunction.app/resources/Kansallinen_syopastrategia_2026_2035_FINAL.pdf and the roadmap (toimeenpanon tiekartta 2026-2031) on files.hackjunction.app.

Team (coordinator junction-new-boss):
- JN Data Analyst -> data/   (gap + where in pathway + by region, SOURCES.md)
- JN Care Strategist -> recs/ (actions, owner, cost, KPI, evidence, Goal 3 mapping)
- JN Builder -> app/          (live demo, public URL, offline-safe)
- JN Pitch & Judge -> pitch/  (scoring, name, story, script, deck, submission, Q&A)

Timeline (Helsinki):
- Sat 23:00 data: first gap finding + sources; strategist: Goal 3 map + action longlist; builder: app skeleton on placeholder-labelled data; pitch: scorecard + 3 name/story options
- Sun 02:00 real data + recs wired into app v1, deployed
- Sun 08:00 judge review round, fixes
- Sun 11:00 FEATURE FREEZE; 12:00 rehearsal; submission before deadline; 14:00 judging
Rule: no invented numbers; anything placeholder is labelled EXAMPLE.
Post status to STATUS.md (one line per update, with your name and time).

## DECISION (Sat 19:30, boss): name "Tasan", angle = lung cancer, diagnosis -> treatment start (Goal 3)
Hero gap: lung cancer median dx->surgery 13.5 d North Finland vs 46.0 d South (Keuhkosyöpä Suomessa 2024, Taul 4.1); curative-treatment share Lapland 18.5% vs Vantaa-Kerava 35.6%, national 27.0% (lung report 2026, Taul 11). Goal 3 indicators hit: treatment within target times (THL Ohjaus 21/2016: 6 wk referral->treatment) + poor-prognosis survival.
Second insight: no public county-level cancer waiting-time data -> Tasan = monitoring + early warning + recommended actions.
Supporting (Goal 2 context, label it): colorectal screening 73.5% vs 80% target, no county meets it, men worst.

## DECISION 2 (Sat 19:45, boss): hero number = age-adjusted lung curative-treatment share (chart estimate, label it)
Lapland men ~16.2% (12.7-20.4) vs Vantaa-Kerava ~29.8% (24.2-36.1); women ~23.1% vs ~39.7%. CIs don't overlap. Source: data/hero.json + LUNG.md.
13.5 vs 46 d (dx->surgery) is now SECONDARY and always carries the 'surgery on diagnosis date in >=25% of cases' caveat.
Lead rec = T3 (Tasan clock). No public referral->diagnosis or 6-week compliance data anywhere = why Tasan exists.

## DECISION 3 (Sat 20:10, boss) – WIN PLAN adopted (review/WIN_PLAN.md, REVIEW.md)
- Spoken lead = people number: "~65 more lung cancer patients a year would get curative treatment if every county below the 27.0% national share reached it (~12 in Lapland)". The analyst MUST verify it first; labelled crude, not stage-adjusted. Proof underneath: age-adjusted ~16 vs ~30 per 100 men.
- One county on stage = Lapland. One ask = sign the 90-day Tasan pilot. Kymenlaakso, 13.5 vs 46 d and the Oulu board/RT arm are off the spoken pitch (kept in the app/appendix).
- Wow = a grounded AI analyst on Verda (EU open-weight): ~60 sourced facts, cites every sentence, refuses questions with no data, drafts a pilot brief live for a county the judge picks. Cached fallback answers. Plus the animated day-28 clock.
- Front page = one screen. Pre-generate AI briefs for all counties.
- Verda side track: the same AI analyst + compute-heavy simulation on Verda; process summary to their Discord.
- OUT: any claim of an existing AZ-county pilot in Finland; the "17% earliest stage" figure; unverified OYS names on stage.

## DECISION 4 (20:15) Verda track = "Tasan Pathway Twin" (review/VERDA_PLAN.md)
- Simulation for each county and scenario, run as Verda batch jobs. Output: the share treated within 6 weeks, with intervals. A zero-effect scenario is always shown. Never "lives saved".
- Live analyst on the Verda Inference API through a server-side proxy. Wording: "EU-hosted inference" (Germany), not "Finland".
- The main page stays one screen. The Twin goes on a separate secondary view, so the app does not get heavier.
- Build and validate locally first; nothing goes to Verda until the user approves a credit budget.
- Go/no-go Sun 08:00: if the sim fails the registry-curve check, ship only the interval, the analyst and a batch test of trick questions.
- Submissions: Discord summary + Junction Platform, both posted only with the user's approval.

## DECISION 5 (20:17) User: too much text. The app goes visual-first.
- Finland county map hero + one big number (~65/yr). At most ~40 words per screen; sources behind toggles.
- County click: gap bar + animated day-28 clock (EXAMPLE).
- "What if?" toggle uses the Verda Pathway Twin output (map recolours, uncertainty, zero-effect visible).
- "Ask Tasan" AI chat on Verda: chips for brief, why, and an honest refusal.
- Verda is visible on stage: the live AI plus the what-if simulation. Footer badge "AI on Verda · EU-hosted".

## DECISION 6 (20:36) User: site feels "empty, like nothing". Full rethink: a real product, rich but scannable.
Tasan becomes a product a county uses, not a single map. Top tabs, each a full, visual screen (charts and cards, short labels, no paragraphs):
1. Overview: headline, map, 3–4 KPI tiles (curative gap, ~65/yr, Lapland ~12/yr, "0 counties publish referral→treatment times") and a ranked bar chart of all counties.
2. Counties: pick any county to see its profile (curative share vs national, rank, CI, survival/stage facts where we have them, data gaps) and an auto "pilot brief" button.
3. Pathway: a visual referral → imaging → biopsy → MDT → treatment diagram, 6-week target bar, where the data goes dark (black box), Goal 3 indicators.
4. Tasan Live (EXAMPLE): the product itself, a navigator/CMO console with a patient list with day clocks, a day-28 alert queue, a blocker breakdown (CT, biopsy, MDT slot), the % within 6 weeks trend and an animated playback. It must look like real software.
5. Simulate (Verda): a what-if with navigator/alert toggles and capacity sliders, a per-county 6-week share with intervals, a zero-effect line and a "computed on Verda" note.
6. Pilot: the generated brief for the chosen county (cost, owner, KPIs, 90-day timeline, stop/go), with PDF download.
Ask Tasan (AI on Verda) is a persistent side panel on every tab, context-aware (knows the current county/tab), with suggested chips.
Every number keeps a source pop-over. Brand: level logo, navy/teal/off-white.

## DECISION 7 (20:42) Verda is a separate track with an ambitious goal (user request)
- New agent: JN Verda Lead (2ec6ee3f-5108-453a-b55a-66f5cbe950e9).
- Hero: "Tasan Extract", an open-weight LLM on a Verda GPU (Finnish DC if available). It turns synthetic Finnish clinical notes into pathway events and day-28 alerts, with an eval for accuracy, throughput and cost per 1,000 notes. It feeds Tasan Live.
- The Pathway Twin sim (Data Analyst) is the second Verda component; Ask Tasan on the Verda Inference API is the third.
- GPU budget under $25, inside the team cap of $50 target / $100 hard.

## DECISION 8 (22:40) Wind down to done (user request)
- Only high-value work from here. Verda: finish the existing work (Extract v1 results, Pathway Twin, Ask proxy, VERDA.md, Discord draft); no LoRA or further expansion.
- Builder's final queue: any-county brief, the How-we-built page, caveat link, answer-source tags, presenter Continue; then freeze.
- 22:41 amendment (user): Verda phase 2 continues (LoRA, sweep, live endpoint), within the $50 Extract cap. Everything else is in wind-down.

## DECISION 7 (Sun 15.11): Tasan and Polku are one project, two audiences
Tasan = county/leadership view. Polku (https://polku.ender.fi) = care-team view that records the step clocks. Tasan links out to Polku (no shared code): topbar switch, "Not measured" tile, Tasan Live end banner, Ask Tasan answer. Supersedes the "no reuse of Polku" note in the header for linking.
