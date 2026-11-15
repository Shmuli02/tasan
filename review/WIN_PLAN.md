# Tasan WIN PLAN: Junction 2026, AstraZeneca "Equal Care Across Finland"
*Win strategist, Sat 14 Nov 2026, about 20:15 Helsinki time (EET). Judging is Sun 15 Nov at 14:00. Feature freeze is Sun 11:00. About 16 hours are left.*
*Inputs: everything in `/workspace/junction-new`, the live app (https://petaled-trowel-90.beacon.host/, bundle `index-BjLwWtRE.js`, byte-identical to local `app/dist`), and a short web check (sources in §10). No number here is new except the arithmetic marked **[our arithmetic]**, which is computed from Registry Taulukko 11 counts in `data/csv/lung_report2026_treatment_by_wsc.csv`.*

---

## 0. Verdict (read this first)

**Can Tasan win 1st as it stands? No. As it stands it is a podium contender. It is not the favourite.**

- **Our strength** is the best evidence base most teams will have. Every number is sourced, the caveats are honest, the gap is age-standardised, there is a sharp "speed ≠ access" insight, and the recommendations already name the county signers, give sourced euro costs, and include a day-90 stop/go.
- **Our single biggest weakness compared with likely competitors** is that the product feels heavy and is not obviously AI. The page is 19.6k px tall. The same caveat appears about 12 times. There are 7 map layers and a simulator. The "AI analyst" is an offline keyword matcher, the "Online LLM" toggle says *(not configured)*, and one answer dumps raw JSON (`src/lib/analyst.ts:315`). A marketing and Business Excellence jury watching a 2-minute demo will remember the team with one clear number and an AI that answered their own question live. That team is probably not us yet.
- **The fix is not more content. It is subtraction plus one real AI moment.** See §1.

| Criterion (weight) | Now (0/1/3/5) | Why | After this plan |
|---|---|---|---|
| Actionability (30) | **3** | The recommendations are 5-grade on paper (signers, € range, stop/go), but they surface only at about 2:30 and are split over two counties and three actions | **5**: one county, one ask, a printed brief handed over |
| Insight (25) | **3** | The real gap (curative share, age-standardised, CIs do not overlap) is buried under a "missing data" headline and fragile surgery-day numbers | **5**: one number, in people, national and local |
| Data quality (20) | **5** | Exceptional. Keep it, but move it one click away | **5** |
| Execution (15) | **3** | Works offline, but the map defaults to the wrong layer, the analyst is off-message, a JSON dump, raw markdown in the brief (per `pitch/APP_REVIEW.md`, still true on the live build) | **5**: one screen, a rehearsed 60-second demo, cached AI fallback |
| Clarity (10) | **1** | A cold director gets the gap in about 45 s but the action only at about 2:30 | **5** |
| **Score** (SCORECARD formula) | **≈ 64 / 100** ("competent") | | **realistic 85–90** ("winning") |

**Is the "AI-powered" requirement met convincingly? No.** CHALLENGE.txt says, twice: *"Develop a nationwide, AI-powered solution to support equal and effective cancer care across Finland"* and *"Build an AI-powered system that supports equal and effective cancer care across Finland."* Its first "possible solution" is *"An AI analyst that explains indicator trends and proposes actions."* Today we have a rules engine labelled "Offline mode". A judge who asks "where is the AI?" gets no good answer. This is a **gate-level risk**, not polish. Fix it with move M3.

**Odds (gut, not data):** as is, about 1 in 5 for 1st and likely top 3. With M1–M4 done and rehearsed, about 1 in 2.

---

## 1. The radical simplification (top priority)

### 1.1 The reframe
**From** "a monitoring dashboard with a tracker, a map, a simulator, an analyst and three pilots"
**to** **"Tasan: ask Finland's lung-cancer gap anything, then take the pilot home."**

One screen. One number. One AI that visibly works live. One county. One ask. Everything sourced lives underneath, one click away.

### 1.2 The one number (sourced, in people)
> **≈ 65 people a year.** That is how many more lung-cancer patients would have had a curative-treatment record if every county below Finland's average had matched it.

- Basis: Finnish Cancer Registry / THL / FICAN, *Keuhkosyöpä Suomessa 2019–2023* (publ. 23.4.2026), Taulukko 11, crude share with a curative-treatment record within 12 months. National 27.0% (4,009 / 14,873).
- **[our arithmetic]** For each of the 12 counties below 27.0%: (national rate × patients) − curative patients. The sum is **≈ 325 people over 2019–2023, ≈ 65 a year**.
  - **Lapland ≈ 60** over 5 years (131 / 710 = 18.5%; national rate would give ≈ 191), **≈ 12 a year**.
  - Kymenlaakso ≈ 45 (≈ 9 a year). South Karelia ≈ 29.
  - Lapland's CI upper bound (21.5%) is below the national 27.0%, and so are Kymenlaakso's (22.7%) and South Karelia's (23.3%).
- **Mandatory spoken caveat (one line):** "That is a crude share. It is not stage-adjusted, and part of it may be case-mix or recording. The age-standardised chart shows that age alone does not explain it: men in Lapland about 16 in 100, Vantaa-Kerava about 30 in 100."
- **Boss decision needed.** DECISION 2 locked the age-standardised men's share as the hero. My recommendation: **say "≈ 65 people a year" as the headline and keep "16 vs 30, age-standardised" as the proof line directly underneath.** People beat percentages with a marketing jury, and the age-standardised figure stays visible as the defence. If the boss keeps DECISION 2, use "Same cancer. In Lapland about 16 men in 100 get curative treatment; in Vantaa-Kerava about 30." Either way, **drop 13.5 vs 46 days from the stage entirely.** It is fragile (Q1 = 0) and contradicts the hero visually.

### 1.3 Hook / one-liner
- **"Same cancer, different postcode, half the chance of curative treatment. Tasan makes that visible in your county in 90 days."**
- Finnish close (for the Finnish judges): **"Tasan, koska hoito ei saa riippua postinumerosta."** (*Tasan, because care must not depend on your postcode.*)
- **Does the name "Tasan" work?** Yes. Keep it. *Tasan* means "evenly / exactly", it echoes *tasa-arvo* (equality), every Finnish judge gets it instantly, and it ties to the clock ("*tasan* 28 päivää"). Add the English gloss once on the screen, under the logo: "*tasan* = evenly, in Finnish". Do not rename at this point.

### 1.4 Wireframe: the one screen (1280×800 and the projector at 1024×768; nothing below the fold is needed for the demo)

```
┌───────────────────────────────────────────────────────────────────────────────┐
│ TASAN  (tasan = "evenly")              Lung cancer · Goal 3 · public data only │
├───────────────────────────────────────────────┬───────────────────────────────┤
│  ≈ 65 people a year                           │   [ small Finland map, 22      │
│  more lung-cancer patients would get curative │     counties, ONE layer:       │
│  treatment if every county matched Finland's  │     shortfall in people.       │
│  average.                                     │     Lapland / Kymenlaakso /    │
│  Lapland ≈ 12 a year. Age doesn't explain it: │     S. Karelia darkest.        │
│  men ~16 vs ~30 in 100 (age-std, chart est.)  │     Click = sets the county ]  │
│  ⓘ Cancer Registry 2026, Taul. 11 · crude ·   │                               │
│    not stage-adjusted          [source ↗]     │                               │
├───────────────────────────────────────────────┴───────────────────────────────┤
│  ASK TASAN. Answers only from 60 sourced facts. Refuses anything else.        │
│  ┌─────────────────────────────────────────────────────────────┐ [Ask]        │
│  │ e.g. "Why is Lapland behind, and what should it do Monday?" │              │
│  └─────────────────────────────────────────────────────────────┘              │
│  chips: [Where is the gap?] [Is it just age?] [What does it cost?]           │
│  ── answer streams here, every sentence ends with a source chip [T11 ↗] ──    │
├───────────────────────────────────────────────────────────────────────────────┤
│  READY PILOT · Lapland · 90 days · 1 nurse navigator + 0.5 analyst ·          │
│  €20,339–23,988 · signer: johtajaylilääkäri · day-90 stop/go                  │
│  [ ✨ Draft the pilot brief for: Lapland ▾ ]        [ Evidence & sources ▸ ]   │
└───────────────────────────────────────────────────────────────────────────────┘
```

- "Evidence & sources ▸" opens a drawer holding all current content: hero card with CIs, the women's figures, the crude/age-standardised method, stage-missing, the THL 21/2016 caveat (**once**), T1/T2/T3 full text, the KPIs, the Sources list, and the data-gaps table. Nothing is deleted from the repo. It is moved out of the judged path.
- "Draft the pilot brief" produces a one-page, printable brief (with QR to the app) for the chosen county (§1.6).

### 1.5 Cut list (remove from the judged path; keep in the repo or drawer)
| Cut / hide | Why |
|---|---|
| **Simulator section** (all 3 sliders, the second full T1/T2/T3 render) | Assumption-heavy. "13.5 d → 0 d" is absurd. It duplicates the recommendations |
| **Map layer switcher (7 layers)** → one layer (shortfall in people) | The default surgery layer makes Lapland look "best" and contradicts the hero |
| **13.5 vs 46 days** everywhere on the front, and in the pitch | Fragile (Q1 = 0), off-message. Q&A only |
| **3 extra signal cards** (2-month start, 1-yr survival, stage missing) | Four competing numbers. Drawer |
| **Crude-secondary block on the front** | It becomes the one-line ⓘ under the headline |
| **"Start here" 4-step tour** | The single screen *is* the tour |
| **Pathway panel** (and its wrong "no national median" text) | Contradiction risk. Drawer |
| **Repeated THL caveat** (about 12×) → one chip: "6-week reference: THL 21/2016, marked outdated · day-28 and 80% = Tasan design" | Buries everything |
| **"Online LLM (not configured)" toggle** and the "Offline mode" badge | Signals "no AI". Replace with a real one (M3) |
| **Old keyword analyst as the primary UI** | Keep only as the offline fallback behind the new ask box |
| **Second county (Kymenlaakso) and T1/T2 on stage** | One county, one ask. Kymenlaakso is "county #2, ready" in Q&A and the brief dropdown |
| **Colorectal / Goal 2 content** | Off-angle. Drawer |
| **Developer labels** (`SIGNAL · LUNG_…`, `lung-2026-t11` chips, "Open 16"), plus YTA, MDT, SBRT, EBUS, HILMO on the front | A marketing jury |
| **Mobile layout work, offline service worker** | Not judged. The local `app/dist` fallback already works |

### 1.6 The real AI (two visible acts)
**Act 1, "Ask Tasan" (grounded Q&A with refusal):** a judge types any question. The answer streams in plain language, every sentence carries a clickable source chip, and anything outside our sourced facts gets a polite, specific refusal. **The refusal is the wow for the Data-quality jury.**

**Act 2, "Draft the pilot brief for [county]":** the AI fills a fixed one-page template for *any* of the 22 counties, using only that county's facts plus the T3 plan. Signer names appear only where they were verified (Lapland, Kymenlaakso). For the others it prints the role with "holder not verified". The output is printable.

**Build spec (Builder + Data Analyst; about 5–6 h total):**
1. **Fact pack** (`app/src/content/facts.json`, Data Analyst, 1.5 h). The script `data/scripts/build_facts.py` turns `hero.json`, `recs/top3.json`, `regions.json`, `sources.json` and the people-shortfall arithmetic into about 60 atomic cards: `{id, claim, value, unit, scope (years, geography, sex), caveat, source_id, source_title, url, page}`. Include "known unknowns" cards (no public 6-week compliance, no county 5-year survival, stage missing 47.7%) so the model can say *why* it can't answer.
2. **Endpoint** (Builder, 1.5 h). A tiny serverless function (Cloudflare Worker, Vercel or similar, whatever the team has a key for). **The API key stays server-side, never in the Vite bundle.** The request is the question plus the selected county. The function sends the system prompt plus the full fact pack (it fits in context, so no vector DB is needed), at temperature 0, with JSON output: `{answer_sentences:[{text, fact_ids[]}], refused:bool, refusal_reason, closest_fact_ids[]}`.
3. **System prompt core:** "You are Tasan's analyst. Use ONLY the facts provided. Every sentence must cite ≥1 fact_id. Never state a number not present verbatim in a cited fact. Always carry the fact's caveat when you use its number. If the question needs anything not in the facts (predictions, survival effects, drug or product questions, patient-level data), set refused=true and name which public data is missing. Never recommend a medicine or a company. Answer in the language of the question (FI/EN/SV)."
4. **Validator** (client or server, 1 h). It extracts every number from each sentence. If a number is not in that sentence's cited facts, or a sentence has no citation, it drops the sentence. If nothing survives, it shows the refusal. A badge shows "✓ 4 sentences · 6 sources · 0 unsourced numbers". This is the visible proof of "grounded".
5. **Resilience** (1 h). Pre-generate and cache answers for the 3 chips plus 10 likely judge questions (§7) in `cached_answers.json`. If the network or API fails or takes over 6 s, serve the cached answer, then the old offline matcher. Rehearse with Wi-Fi off.
6. **Brief drafter** (1 h, after 1–4). Same endpoint, `mode=brief`, with a fixed markdown template (Why this county · 90-day plan · KPIs · roles · cost · stop/go · DRAFT not signed). It renders as clean HTML with a print button. **Pre-print 5 Lapland copies** (M2).
7. **Guardrails visible on screen:** "Public aggregate data only · no patient data · AI cannot add facts". Log questions locally so a refusal can be shown in Q&A.

### 1.7 The 60-second demo, second by second (presenter drives; second teammate on the backup laptop with local `app/dist` and cached answers)
| s | Screen | Say |
|---|---|---|
| 0–8 | The one screen loads. The big number is visible | "Same cancer, different postcode. About 65 people a year in Finland miss curative lung-cancer treatment they'd get at the national average." |
| 8–15 | Hover Lapland on the map, then the ⓘ | "Lapland: about 12 a year. And it isn't age: age-standardised, men are about 16 in 100 vs 30. Cancer Registry, 2026." |
| 15–30 | Type live: **"Why is Lapland behind and what should it do on Monday?"** The answer streams with source chips | "This is Tasan's analyst. It can only use our 60 sourced facts, and every sentence cites one." (Click one chip → Taulukko 11 opens.) |
| 30–40 | Type: **"Will this save lives by 2030?"** → refusal card | "And when the data doesn't exist, it says so. No county even publishes whether patients start treatment within six weeks. That missing clock is the pilot." |
| 40–52 | Click **"Draft the pilot brief: Lapland"**. The one-pager appears | "Ninety days. One nurse navigator, half an analyst, about 20 to 24 thousand euros. A day-28 alert. The county's chief medical officer decides go or stop on day 90." |
| 52–60 | Switch the dropdown to the judge's suggested county → a new brief appears in about 5 s | "It works for all 22 counties. Joanna, this is printed for you." (Hand over the paper brief.) |

**The wow moment = the live refusal (30–40 s) followed by the brief for a county the judge picks (52–60 s).** If the live AI fails, the presenter clicks the same chips. Cached answers look identical.

---

## 2. Ranked moves (estimated judging points gained per hour of work)
Points use the SCORECARD formula (out of 100). The estimates are judgement, not data.

| # | Move | Owner | Hours | +Points | Pts/h | Done by (Sun, EET) |
|---|---|---|---|---|---|---|
| **M1** | **Rewrite the pitch around one number, one county, one ask** (§1.2–1.3, §6). Drop 13.5/46, Kymenlaakso, T1/T2 from the spoken 2 minutes | Pitch & Judge | 1 | +6 (Clarity 1→3, Insight 3→5 partly) | **6** | 01:00 |
| **M2** | **Sign-ready Lapland brief on paper + the explicit AZ ask** (§5). One A4: plan, KPIs, roles, €, AZ role, stop/go. 5 copies. QR to the app | Care Strategist | 1.5 | +6 (Actionability 3→5 with M1) | **4** | 08:00 |
| **M3** | **Real grounded AI analyst with visible refusal** (§1.6 steps 1–5) | Builder + Data Analyst | 5 | +10 (removes the AI gate risk; Execution 3→5; Insight) | **2** (but mandatory) | 06:00 code, 08:00 cached |
| **M4** | **One-screen front + Evidence drawer + cut list** (§1.4–1.5) | Builder | 3 | +6 (Clarity →5, Execution) | **2** | 04:00 |
| **M5** | **AI "draft brief for any county"** (§1.6 step 6) | Builder | 1 | +3 (Actionability, "nationwide") | **3** (after M3) | 09:00 |

**Order of work:** M1 and M2 start now (no code). M4 and the M3 fact pack in parallel tonight. The M3 endpoint after that. M5 last. If M3 is not working by 08:00, ship **cached answers only** for the 3 chips plus 10 questions. Say it plainly: "AI answers pre-generated and validated against our facts." That is still a real AI pipeline. Do not fake "live".
**Boss:** take the hero-number decision (§1.2) by 21:30. Freeze at 11:00. Run 2 rehearsals (12:00, 13:00), one driven by a second teammate. Re-record `backup_demo_90s.webm` after the freeze.

### Stop doing (cut list for the team, in addition to §1.5)
- Stop adding caveats, evidence rows and new data sources. Data quality is already a 5.
- Stop polishing the map layers, the simulator, the Start-here tour, the mobile view and offline reload.
- Stop the two-county / three-action story on stage.
- Stop arguing the THL 2016 document in the pitch. Use one line, then move on.
- Do not fix the old analyst's bugs (JSON dump, Goal 3 listing) unless it remains user-visible. It becomes the fallback only.

---

## 3. Competitor map (prediction; about 10–20 teams)
| Likely build | How common | Where Tasan looks the same | Where Tasan wins / loses |
|---|---|---|---|
| **County dashboard / choropleth of Sotkanet indicators** (screening %, waits, mortality) | Very common (half the field) | Our current app *is* this today. Map + layers + cards | Win only if we're one screen and one number. Lose if we demo layers |
| **LLM "AI analyst" chatbot over PDFs** (strategy, roadmap) | Very common | Our analyst is in the same slot but **not an LLM** | They will look more "AI". They will hallucinate or cite vaguely. **Our edge: grounded + visible refusal + numeric validator** |
| **Risk map / "underserved areas" ML** (distance to OYS/HUS, age, smoking proxies) | Common | — | Shiny but ecological and assumption-heavy. Data-quality judges will mark it down. We win on sources |
| **Symptom checker / patient app / referral triage bot** (GP-side lung symptom scoring, CXR AI) | Common | — | Matches AZ's global early-detection interest (Qure.ai, Aidence). Weak on Goal 3 and county actionability. Teams may cite Sata-alue's direct-CT pathway |
| **Waiting-time early-warning / simulator** (queue model, "what if +1 CT") | Some | Our day-28 alert + simulator | Usually synthetic data. We have real THL 21/2016 time points and a real pilot owner |
| **Screening-uptake nudges** (colorectal / LDCT invites, SMS) | Some | Our G2-1 appendix | Goal 2, not Goal 3. Lung LDCT is already piloted nationally (Jan 2026, Cancer Registry + OYS) |
| **Polished "pilot-ready" consulting pitch** (named county, costs) | Rare (1–2 teams) | **This is our true lane** | The dangerous competitor. We win if our county, signer, € and stop/go are on paper in their hands |

**Honest read:** on substance we are top-tier. On "first 60 seconds of impression" we currently look like competitor type #1 with a weaker AI than type #2. The plan moves us to the empty corner: **pilot-ready + grounded AI + one human number.**

---

## 4. The AZ angle (what these judges personally care about)
- **The brief's own words:** AZ wants to *"explore promising solutions beyond Junction, ideally through a follow-up project in collaboration with a Finnish wellbeing services county."* Judges are Marketing (Rusila, Aaltonen) and Business Excellence (Tuormaa, *"Innovation and Business Excellence Director, Nordics"*). They will ask: is this a project we could take to a county next month, and is it safe for a pharma company to sponsor?
- **AZ has done exactly this before next door.** In Estonia, AZ, MSD and Roche signed a consortium with the Ministry of Social Affairs, the Health Insurance Fund and the Connected Health Cluster to map and improve the **lung-cancer patient pathway** (Sorainen, 7 Jan 2023). AZ Oy joined HUS's CleverHealth Network, citing AI and early detection. Globally, AZ's Lung Ambition Alliance targets screening, diagnosis and quality of care. **Line:** "Tasan is the Finnish, county-level version of a model AZ already backs in Estonia."
- **Complement, don't compete,** with Finland's LDCT screening pilot (started Jan 2026, Cancer Registry + OYS, 1,200 participants, 5 areas). Screening finds cancers earlier. Tasan checks that they then *reach* curative treatment on time, in every county. Satakunta's GP-direct CT pathway (pilot 2022, routine 2024) is an in-country precedent for a T1-type fix.
- **Compliance-safe AZ role (say it before they ask):** non-promotional, no product, no patient-level data to AZ. The county owns data and decisions. Transparent under the Pharma Industry Finland Code of Ethics 2026 (collaboration and transfers disclosed). AZ contributes **project management / service-design support, funding of an independent 90-day evaluation, and convening** (FICAN North, peers via the Lung Ambition network). Wording for the money: "AZ *could* co-fund the evaluation". Do not say AZ pays clinical staff. Any funding model needs AZ's own compliance review.

## 5. The ready pilot (what AZ should see on one A4)
- **Named county: Lapland (Lapin hyvinvointialue).** It has the largest shortfall (≈ 60 people over 2019–2023, crude; CI excludes the national level). Age-standardised men ~16 vs ~30 in 100. T3 runs entirely inside the county, so it does not depend on OYS. **Ready county #2: Kymenlaakso** (≈ 45 people; HUS hand-off; signer verified).
- **Signer:** johtajaylilääkäri, Lapin hyvinvointialue, Jyri J. Taskila (verified on the county website, 14 Nov). **Navigator line manager:** vs. hoitotyön johtaja Henna Kauranen. **Data:** county analytics unit. **Partner (week-1 gate):** the OYS lung MDT lead and RT lead, not yet verified publicly. *Label: DRAFT, not discussed with the county.*
- **90 days:** days 1–30, extract 12 months of THL 21/2016 time points, run the registry-completeness check, publish the baseline, name the navigator. Days 31–60, weekly feed, day-28 alert live, navigator acts. Days 61–90, first board report (including non-pathway waits) and the day-90 stop/go.
- **KPIs:** (1) ≥85% of pathways with all 4 time points. (2) The baseline "% treated ≤42 days from referral" presented to the board. (3) ≥90% of day-28 alerts actioned within 2 working days. (4) ≥90% of new suspected cases contacted within 3 working days. Long-term: age-standardised curative share, with Pohjois-Pohjanmaa as the peer benchmark, **not a promise**. All thresholds are Tasan design choices. Say so once.
- **Cost:** **€20,339–23,988 per county for 90 days** (1.0 FTE nurse + 0.5 FTE analyst; KT pay Oct 2025 × 2026 employer contributions of 23.14%). **[our arithmetic]** Lapland has ≈ 142 lung cancers a year (710 / 5), so ≈ 35 patients in 90 days, or about **€580–690 per patient pathway tracked and navigated**. **ROI framing: no euro saving is claimed** (no sourced figure). Frame it as "the price of finding out, in 90 days, whether your county is losing ~12 curative patients a year to delay or to access". The roadmap's €300k (p.60) is national money, not county money. Do not use it.
- **The ask (last slide, last line):** "AstraZeneca: introduce Tasan to Lapland's chief medical officer. We bring this brief and a working tool. Day 1 can be in January."

## 6. Pitch skeleton (3:00 total: 2:00 story with the 60 s demo inside, 1:00 buffer for transitions and Q&A)
1. **0:00–0:10 Hook.** "Same cancer, different postcode, half the chance of curative treatment."
2. **0:10–0:30 The number.** ≈ 65 people a year; Lapland ≈ 12; "not age: 16 vs 30 in 100"; source on screen; one-line caveat.
3. **0:30–0:45 Why it persists.** Goal 3 says "patients start treatment within target times" (strategy p.5). No county can see that today. THL 2017: national follow-up "has been missing".
4. **0:45–1:45 Demo** (§1.7): ask → cited answer → refusal → Lapland brief → judge's county.
5. **1:45–2:00 Close.** "Ninety days. One nurse. About 22 thousand euros. One clock. AstraZeneca, take us to Lapland." Hand over the printed brief. "*Tasan, koska hoito ei saa riippua postinumerosta.*"
6. **Q&A (hold, don't speak):** women's figures, crude vs age-standardised, ±1 pp digitising, stage missing 47.7%, the THL 2016 status, the speed vs access paradox (North is fast to surgery yet lowest curative share), Kymenlaakso, T1/T2.

## 7. Questions to pre-cache for the AI (and to rehearse)
"Where is the gap?" · "Is it just age?" · "Why Lapland?" · "What would it cost?" · "Who signs?" · "What does the nurse navigator do?" · "Does any county publish 6-week compliance?" · "What about women?" · "How does this map to Goal 3?" · "Will it save lives?" (refusal) · "Which drug should they use?" (refusal) · "What about Kymenlaakso?" · the same in Finnish.

## 8. Risks and mitigations
| Risk | Mitigation |
|---|---|
| The "≈ 65 / ≈ 12 people" figure is attacked as crude / case-mix / recording (no-record share 16.4–43.1% by county) | Say "crude" on screen; the age-standardised proof line sits below it; the CI excludes the national level; "that uncertainty is exactly why day 1 is a completeness check" |
| The LLM hallucinates live | Numeric validator, temperature 0, fact pack only, visible "0 unsourced numbers" badge |
| Wi-Fi or API failure | Cached answers, then the offline matcher, then the backup laptop with local `app/dist`, then the recorded video |
| API key leaks in the static bundle | Server-side function only. Check the built JS for the key before deploy |
| Late hero change causes inconsistency | Boss decides by 21:30. Pitch, app and brief all change together. Feature freeze at 11:00 |
| Pharma-compliance unease | §4 role wording. "DRAFT, not discussed with the county". No product mention, ever |
| Over-claiming effect | "Proposed peer benchmark, not a promised effect". Navigator evidence is mixed: say it if asked |
| The Simulator or old screens resurface via `npm run sync` | Remove them at component level, and fix `extract_team_data.py` (`spotlight_stage`) so the sync can't revert |

## 9. Data gaps and blockers
- **No public county 6-week compliance, cancer-specific referral→treatment times, or stage by county.** That is the product's reason to exist. Keep it as one line.
- **The hero is a chart estimate** (±1 pp, Kuva 16). The people number is our arithmetic on crude counts. Both are labelled.
- **OYS MDT and RT leads not verified** → T2 stays a gated add-on and is off the stage.
- **The LLM needs an API key and a serverless host the team controls.** Not verified on the box. Builder or boss must confirm by 21:30, otherwise use the cached-only fallback.
- **The web check could not confirm any existing AZ Finland × wellbeing-county pilot.** Do not claim one. (The Satakunnan Kansa article cites a 2025 Nordic study, "about 17% of Finnish lung cancers found at the earliest stage vs >25% in Denmark and Norway". We did not open the study. Do not use it on stage.)

## 10. Sources opened for this plan (14 Nov 2026)
- Challenge brief: `/workspace/junction-new/CHALLENGE.txt` (Junction platform export, challenge 344).
- Finnish Cancer Registry / THL / FICAN, *Keuhkosyöpä Suomessa 2019–2023*, Taulukko 11 and Kuva 16: https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html (via `data/csv/lung_report2026_*.csv`).
- Kansallinen syöpästrategia 2026–2035, p.5 (Goal 3 indicators); roadmap 2026–2031: https://files.hackjunction.app/resources/
- THL 2017 *Hoitoonpääsyn seuranta syövän hoidossa* (`data/raw/thl_hoitoonpaasy_loppuraportti_2017.txt`).
- KT pay statistics and employer contributions (via `recs/top3.md`).
- AZ Estonia lung-pathway PPP: https://www.sorainen.com/deals/novel-public-private-partnership-contributes-to-the-implementation-of-cancer-control-plan/
- AZ joins CleverHealth Network: https://cleverhealth.fi/en/news/astrazeneca-joins-the-cleverhealth-network-ecosystem/
- AZ Lung Ambition Alliance / lung equity: https://www.astrazeneca.com/our-therapy-areas/oncology/lung-cancer.html · https://www.astrazeneca.com/media-centre/articles/2025/our-commitment-to-improving-lung-health-equity.html
- AZ × Qure.ai AI chest X-ray: https://www.qure.ai/us/news-press-coverages/A-new-era-for-lung-cancer-detection-AI-enabled-risk-assessment-reaches-5-million-people-around-the-world · AZ × Aidence: https://www.aidence.com/news/aidence-astrazeneca-ipn-ai/
- Finnish LDCT screening pilot (Jan 2026): https://syoparekisteri.fi/seulonta/tutkimus-2/keuhkosyovan-seulontapilotti/
- Satakunta GP-direct lung CT pathway: https://www.satakunnankansa.fi/satakunta/art-2000012403607.html
- Pharma Industry Finland Code of Ethics 2026: https://www.pif.fi/media/julkaisut/esitteita-ja-raportteja/pif_code-of-ethics_2026.pdf
