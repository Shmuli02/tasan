# Judge Q&A — Tasan

**Use:** after the three-minute pitch, Sunday 15 November 2026, 14:00 Europe/Helsinki. Answers stay inside the `FINDINGS_REVIEW.md` "safe to say" list. If a figure is not on that list, say so. Do not tighten a range, drop a caveat, or fill a PENDING with a guess. Day-28 and 80% are Tasan design; 29-day and 23.6% figures are proposed peer benchmarks, not promised effects. Sotkanet 6411 has been dropped — do not volunteer it.

**Updated 14 Nov 20:15 EET for DECISION 3.** The spoken pitch is one number (about 65 a year, Lapland about 12), one proof (men 16 vs 30, chart estimate), one county (Lapland) and one ask. Kymenlaakso, 13.5 vs 46 days, T1 and T2 are **Q&A only** (sections below). Never say "lives saved", "deaths prevented" or "patients denied treatment". Never give an exact people number, and never claim an existing AstraZeneca–county pilot.

---

## The people number (DECISION 3)

### P1. "Where does 'about 65 a year' come from?"

"It's our arithmetic on published Cancer Registry counts. It isn't a published estimate. Taulukko 11 of the 2026 lung-cancer report gives, for every wellbeing county, how many lung-cancer patients diagnosed 2019 to 2023 had surgery or curative radiotherapy recorded within 12 months. Nationally that's 4,009 out of 14,873, or 27.0 percent. Twelve counties are below that. For each, we take 27.0 percent of its patients and subtract the patients who actually had a curative-treatment record. That adds up to about 325 over five years, about 65 a year. Lapland is 710 patients and 131 with a record. At the national rate it would be about 191, so the gap is about 60 over five years, about 12 a year. It's crude and illustrative, not stage-adjusted, and it says nothing about lives saved."
- Source: `data/hero.json` → `people_number`. JN Pitch re-computed it from `data/csv/lung_report2026_treatment_by_wsc.csv` on 14 Nov 20:12 EET: 324.6 / 5 = 64.9 a year; Lapland 60.4 / 5 = 12.1.

### P2. "That's cherry-picked. You only add up the counties below average." (the strongest attack)

"Yes, that's the question we asked: what if the counties below the national rate reached it? It's a levelling-up scenario, not a zero-sum one. Some of any below-average gap is chance. If we count only the counties whose 95 percent interval sits entirely below the national rate, it's still about 50 a year. Lapland's interval tops out at 21.5 percent, well under 27."
- [Our arithmetic, 14 Nov.] 50.0 a year from the counties whose upper CI is below 26.95%: Lapland, Kymenlaakso, Varsinais-Suomi, Pohjois-Pohjanmaa, South Karelia, North Karelia.
- Do not volunteer the next point; if pressed, concede it: across all 22 counties, the gaps net to roughly zero against the national rate, because above-average counties offset them. The 65 is a one-sided, levelling-up figure by design.

### P3. "Isn't that just older, sicker patients in the North?"

"Age alone doesn't explain it. The age-adjusted chart in the same report shows about 16 in 100 men in Lapland against about 30 in Vantaa-Kerava, and the intervals don't overlap. Stage and fitness we can't adjust for: stage is missing for about 48 percent of lung cancers nationally. That's exactly why the pilot starts with the county's own data."

### P4. "Or is it just how treatment is recorded?"

"Possibly in part, and we say so. The share with no treatment record varies a lot by county. In some counties drug therapy is barely recorded in the registers. That's why day 1 to 30 of the pilot is a completeness check against the hospital's own records, before any baseline is published."

### P5. "So 65 people a year are being denied treatment? Lives lost?"

"No. We don't say that, and the data can't. Curative treatment means surgery or curative radiotherapy recorded within a year. It isn't survival. The benchmark is the national average, not a clinical optimum. The number tells a county where to look, not how many lives it would save."

### P6. "Why the national average? The best counties are higher."

"Because it's the most defensible benchmark: half of Finland already reaches it. Vantaa-Kerava is at about 36 percent crude, so the national rate is a modest bar, not the ceiling."

Other attack lines to know (do not volunteer them):
- The 2019–2023 diagnosis years include the COVID years. The per-year figure is a five-year average (÷5).
- The 22 counties sum to 14,774 patients against the national 14,873. The 99-patient difference (residence outside the 22 counties, e.g. Åland or unknown) is in the national rate but not in any county; the effect is negligible.
- The method note in `hero.json` says "would have had a curative-treatment record". The spoken line says "would get curative treatment". If a judge presses on tense or causality, restate it the `hero.json` way.

---

## Why Lapland, other counties, and the AI

### L1. "Why Lapland?"

"It has the largest shortfall of any county: about 12 patients a year, crude. Its interval sits wholly below the national rate. In the report's age-adjusted chart, Lapland men are the lowest of all counties, at about 16.2 percent (chart estimate). And Tasan's clock runs entirely inside the county: about 140 lung cancers a year, so about 35 patients in 90 days, which is small enough for one navigator. The signer role is the johtajaylilääkäri; we checked the current holder's name on the county website on 14 November. The brief is a draft. Nothing has been sent to or discussed with the county."
- Ready county #2, if asked: Kymenlaakso (about 9 a year, CI also below national; HUS hand-off; signer name also checked). Details are in R2 and R6 below.

### L1b. "Why compare with Vantaa-Kerava? It isn't even the highest."

"True. For men, West Uusimaa (about 32) and Pirkanmaa (about 31) are higher on the chart. Vantaa-Kerava is the highest crude share (35.6 percent) and the highest age-adjusted figure for women (about 40). It's a like-for-like illustration, not a league table. The people number uses the national rate, not Vantaa-Kerava."

### L2. "Pick my county: Kainuu (or any other). What does Tasan say?"

- **Every one of the 22 wellbeing counties** has a Taulukko 11 count, so the people-number gap (or "at or above the national rate") exists for each. See `people_number.counties` in `hero.json` for the 12 below.
- **No county**, including that one, publishes six-week referral-to-treatment compliance. That is the gap Tasan fills.
- **The age-adjusted chart estimate (Kuva 16)** has been digitised for every county, by sex, in `data/csv/lung_report2026_curative_agestd_by_sex_chart_estimate.csv`, ±1 pp. Quote it as "about" and "chart estimate".
- **Signer names** have been checked only for Lapland and Kymenlaakso. For any other county, give the role (johtajaylilääkäri), "holder not verified".
- **Åland** is not one of the 22 wellbeing counties. It runs its own system, and we have no comparable data for it. Say "no data", don't estimate.
- **What the app does today, if a judge picks a county:** clicking the county on the map (Treat layer) shows its crude share against the national rate. Typing "Draft a pilot brief for X" does **not** produce a brief on the current build; it lists that county's public signals. Do not demo it unless the builder ships brief drafting and it passes the 12:00 rehearsal.

### L3. "Is this really AI? What can't it do?"

Say only what is true of the build that is on stage. Check at the 12:00 rehearsal.
- **Current build (live 20:12):** "The analyst on stage today is offline, deterministic retrieval over our sourced data files. Every answer cites its source, and it works with no internet. It is not a large language model. It can't answer anything outside those files. If the data doesn't exist, as with six-week compliance, it says no county publishes it."
- **If the grounded LLM ships (WIN_PLAN M3):** "It's a language model, but it may only use 81 sourced facts, including 14 questions it refuses because no public data exists. Every sentence must cite one, and a validator drops any sentence with a number that isn't in the cited fact."
- **In both cases, the limits:**
  - It never sees patient data.
  - It doesn't predict survival or lives saved.
  - It doesn't recommend drugs or products.
  - It can't add facts.
  - The county, not the tool, makes clinical decisions.
- **Known weak spots in the current build (don't demo them):**
  - It does not refuse a drug question; it answers with Lapland's signals.
  - It answers "Will this save lives?" with a generic "no direct match", not a proper refusal.
  - The "Impact of …" chip prints raw JSON.

### L4. "Has AstraZeneca done this with a county already?"

"Not that we know of, and we don't claim it. Your challenge brief says you'd like a follow-up with a Finnish wellbeing services county. This is sized for that."

---

## The hero number

### H1. "How was the age adjustment done? Did you do it?"

We did not do the age adjustment. The Finnish Cancer Registry did, in *Keuhkosyöpä Suomessa 2019–2023* (published 23 April 2026). The methods say regional treatment shares are presented separately for men and for women using **direct age standardisation**. The standard population is the age distribution of **all patients in Finland in the study period**, in **four age groups**: under 60, 60–69, 70–79, and 80 and older. The report's confidence intervals use a **normal approximation**. We read the values from Kuva 16, the county figure. There is no published table of these numbers.

### H2. "Why do you keep saying 'chart estimate'?"

Because the report publishes the age-standardised curative shares only as figures — Kuva 15 for collaborative areas, Kuva 16 for wellbeing counties — not as a table. We digitised Kuva 16 by pixel measurement. Every value, including the drawn confidence intervals, is an estimate to about **plus or minus one percentage point**, and must be spoken as "about." We will not present 16.2 or 29.8 as if they were printed table cells. The crude all-patient shares (Lapland 18.5%, Vantaa-Kerava 35.6%) *are* printed, in Taulukko 11; those are not the hero.

### H3. "Is this men only, or all patients?"

The hero comparison is **men on both sides**: Lapland men about 16.2% [12.7–20.4] versus Vantaa-Kerava men about 29.8% [24.2–36.1]. It is like-for-like. We will not say "16.2 percent of Lapland patients." Women are on the same chart, and they are not the hero: Lapland women about 23.1% [17.9–29.0] versus Vantaa-Kerava women about 39.7% [33.1–47.0]. The women's gap is in the same direction and, on the point estimates, slightly wider. The crude all-patient figures from Taulukko 11 are 18.5% (15.8–21.5; 131/710) in Lapland and 35.6% (31.9–39.6; 212/595) in Vantaa-Kerava, national 27.0% (4,009/14,873). Do not put a men's chart estimate and a crude all-patient share on the same line.

### H4. "Do the confidence intervals overlap?"

For the hero comparison, no. Lapland men's upper bound is 20.4; Vantaa-Kerava men's lower bound is 24.2. That is a 3.8 point gap between the intervals. Because these are chart estimates, each bound could be off by about one point. Even if we move both bounds toward each other by one point — 21.4 versus 23.2 — they still do not overlap. The women's intervals also do not overlap: 29.0 versus 33.1, and still not after a one-point shift. We did not run a statistical test; we are reporting that the intervals as drawn, and as read by us, do not overlap. This is not five-year survival, and it is not adjusted for stage, comorbidity, fitness, or recording practice. Age structure alone does not explain the gap.

### H5. "At least a quarter of patients have surgery on the diagnosis date — all patients? Everywhere?"

No. The caveat applies to the **surgery-time table**, not to the hero share, and to patients whose first treatment within six months was surgery — about one in ten nationally — not to all lung-cancer patients. In Taulukko 4.1, the lower quartile is zero days in the North (0–44), and also in East and Inland Finland, and nationally (0–56). So in the North, at least a quarter of those surgery patients have surgery on the registry diagnosis date. The South's lower quartile is 33 days, so this particular dating effect is not what produces the 46-day Southern median. Our guess, which the report does not state, is that the diagnosis is sometimes dated from the resection specimen. Whenever we say 13.5 versus 46 days, we say this in the same breath. We will not say "the North is three times faster" without it.

---

## The four pitch warnings

### W1. "This is just a North-versus-South story."

No. Speed and access run in different directions. The hero is an access proxy, men, chart estimate, and it is lower in Lapland than in Vantaa-Kerava. The secondary time figure runs the other way: among patients who had surgery within six months, the median from diagnosis to surgery was 46 days in the South Finland collaborative area and 13.5 in the North (Finnish Cancer Registry, 2024, Taulukko 4.1, p. 27; diagnoses 1/2018–6/2022; five YTAs of residence; and in the North at least a quarter of those patients have surgery on the diagnosis date). That is why we do not offer one national fix: T1 is a speed intervention in a South-YTA county; T2 is an access intervention in Lapland, where the North is already the fastest YTA to surgery.

### W2. "Your times are only five regions."

Yes. The public diagnosis-to-treatment medians exist for five collaborative areas, not twenty-two counties, and only for 2018 to mid-2022, for patients who received that modality within six months. We will not put the 46-day South YTA median on a slide titled Kymenlaakso as if it were the county's number. That gap is why T3 exists: extract referral-arrived, diagnosis, and first-treatment dates at county level, from next month.

### W3. "You said curative shares were not age-adjusted. Now they are?"

The **crude** shares in Taulukko 11 are still not age-adjusted, and they are still not five-year survival. The report also published an age-standardised view, but only as charts. We have now digitised those charts (±1 pp), and the men's figures are the hero, labelled as a chart estimate. Stage is still missing for 47.7% of the national lung cohort (7,097 / 14,873), so nothing we show is stage-adjusted. Age-adjusted figures in the 2024 report tables are surgery, drug therapy and radiotherapy, not the later "curative" group, and they are a different cohort. We will not mix those into the hero line.

### W4. "THL 21/2016 is outdated. What target do you actually cite?"

We cite the target the strategy itself names. Goal 3, page 5, says patients should start treatment within the target times, and the footnote points to THL Ohjaus 21/2016. That guidance, section 4.1, is a generic six-week clock from the arrival of the referral to the start of the first treatment. The PDF is watermarked *Vanhentunut*. It has no lung-specific limit. The 2026–2031 roadmap, measure 3.1.2, page 57, says cancer-specific treatment-time targets will be set in 2026 to 2028. There is no newer published Finnish official clock. Until those times exist, our working reference is that six-week interval, clearly labelled as the strategy's named reference, document outdated. We do not invent a replacement official number. We do not use Terveydenhuoltolaki §52 (three or six months for non-urgent specialist care) as a cancer target. Day-28 is Tasan's design — two-thirds of 42 days — not an official threshold. An 80% on-time bar would also be our operational proposal, not the law.

---

## The three recommendations

### R1. "Why should T3 lead? It's just a dashboard."

T3 is the only recommendation whose KPI is the Goal 3 wording itself: the share of patients whose first treatment starts within the target time, measured from referral arrival, in a named county. No public statistic currently reports that by region. T3 is also what makes T1 and T2 honest: it supplies the county time baseline we do not have. The product is not the chart. It is the extract, the day-28 alert, and a named nurse navigator who owns every delayed patient, reporting monthly to a clinical director. We do not claim that a dashboard alone raises the curative share, the men's chart estimate, or five-year survival.

### R2. "Why Kymenlaakso for the fast track? South Karelia is lower."

Kymenlaakso's crude curative-record share is 19.3% (114/591; CI 16.3–22.7). South Karelia is 18.9%, slightly lower. The age-standardised men's chart estimates are about 18.0% [14.1–22.8] in Kymenlaakso and about 19.0% [13.8–25.6] in South Karelia. We are not picking "the worst county." We are picking a South-YTA county with about 118 diagnoses a year (591 over five years) and a design that needs pre-agreed HUS slots. The speed problem we can document is at YTA level: Etelä-Suomi surgery median 46.0 days, with the caveats above. T3 days 1–30 measure the county clock before we set a county target. If a judge from South Karelia offers a pilot, the same fast-track design can travel.

### R3. "You will cut Kymenlaakso from 46 to 29 days?"

No. We will not promise that. 46 days is the South Finland *YTA* median from diagnosis to surgery, not a Kymenlaakso figure, and not a referral clock. In the North, at least a quarter of those surgery patients have surgery on the diagnosis date, so the contrast is not a clean speed gap. 29 days is the Sisä-Suomi YTA median, which we may use as a proposed peer benchmark once we have the county baseline. If a lung clinic already exists, week 1 maps the missing step and we close that step, rather than inventing a pathway on top of one.

### R4. "Doesn't a tumour board already exist in Oulu? This already exists."

Almost certainly a thoracic MDT already exists at Oulu. We are not proposing to set one up. The recommendation is that every new Lapland lung cancer is listed on that existing board, by video, before a treatment decision. We have not yet confirmed how many Lapland cases are already reviewed there. That is our first week-1 question. If the answer is "most of them," T2 becomes "close the gap to 100%," not "create a board." We will also not treat a low recorded-MDT share as proof that cases are not discussed, until we check recording.

### R5. "You will raise Lapland from 16.2% to 29.8%, or from 18.5% to 23.6%?"

No, we will not promise that. 16.2 and 29.8 are men's chart estimates, and 23.6% is Pohjois-Pohjanmaa's crude all-patient share — a proposed peer benchmark, not an evidenced effect. The process KPI we will hold is the share of new cases discussed at the Oulu board before a treatment decision, with a proposed operational bar of 90%. Outcome changes, if any, will be read later, with registry lag, and they still will not be five-year survival. MDT evidence in the literature is observational and open to selection bias.

### R6. "Who owns this, what happens next month, and what does it cost?"

The intended signers, taken from the counties' public leadership pages on 14 November 2026, are Tuula Rajaniemi, johtajaylilääkäri of Kymenlaakson hyvinvointialue, and Jyri J. Taskila, johtajaylilääkäri of Lapin hyvinvointialue. The nurse navigator in each county would be line-managed by the chief nursing officer: Mari Kuusisto in Kymenlaakso, Henna Kauranen in Lapland. Operational sponsors, also public: Ari Ronkainen (hallintoylilääkäri, erikoissairaanhoito) in Kymenlaakso, and Anu Maksimow (somaattisen erikoissairaanhoidon johtaja) in Lapland. The HUS thoracic counterpart, the Kymenlaakso pulmonology chief, and the OYS MDT and radiotherapy leads are roles we have not yet named. The one-page briefs are drafts. Nothing has been sent to, or agreed with, either county, or with Pohde. We will not speak as if those people have already signed.

First month, in both counties: extract referral arrival, first visit, queue date and first treatment for the last 12 months of lung cancers, run a registry-completeness check, name the navigator, and set the county's own baseline. In Kymenlaakso, map the pathway and name the HUS counterpart. In Lapland, audit which 2025 cases were already listed at the existing OYS board, and which curative-radiotherapy referrals started.

**Cost (say "staff cost only, estimate").** The figures are for 90 days, from `recs/pilot_brief.md` and `recommendations.json`:
- **Kymenlaakso:** €20,339–€23,988. That is T3: a 1.0 FTE nurse navigator at €11,726–€14,954 plus a 0.5 FTE analyst at €8,613–€9,034. If the week-1 map shows that T1 needs its own 0.5 FTE pathway coordinator, add €5,863–€7,477, for **€26,202–€31,465**. Otherwise the T3 navigator covers it.
- **Lapland:** **€23,857–€28,474**. That is T3 at €20,339–€23,988 plus T2's 0.3 FTE MDT list coordinator at €3,518–€4,486.

Details are in R6b.

### R6b. "What exactly does that cost include and exclude, who pays, and how does it compare with the roadmap money?"

**Includes.** Only staff salaries for the posts named above, for 90 days. Pay is KT Kunta- ja hyvinvointialuetyönantajat's October 2025 wellbeing-sector pay: sairaanhoitaja €3,174 task-based / €4,048 total earnings; analyytikko €4,663 / €4,891 a month. On top of that, KT's 2026 employer contributions of 23.14%. The low end of each range is task-based pay, the high end total earnings with supplements. It is an "estimate": it uses national averages, not either county's own pay scale, and later pay rises are not included.

**Excludes, with no euro figure because we have no sourced price:**
- Physician time: SOP set-up, est. 40–80 h in Kymenlaakso; MDT time, est. 0.75–1.5 h per case × about 36 cases a quarter in Lapland; baseline audit 16–32 h.
- Dashboard integration with the county EHR/BI platform. No quote was obtained; the Tasan prototype is reused.
- Extra CT/EBUS lists, if needed, and reflex biomarker panels.
- Video/PACS, which is assumed to exist.
- In Lapland, the curative-radiotherapy access arm (slot quota, Kela travel, patient hotel). It is design only and is sized with the OYS radiotherapy lead after the week-1 gate.

So never say "Tasan costs €20k". Say "the staff cost of the 90-day pilot is about €20–24k per county, estimate".

**Who pays.** The pilot county, from its own operating budget: Kymenhva for Kymenlaakso, and Lapin hyvinvointialue for Lapland. The OYS side of T2 (MDT time, radiotherapy) is an agreement with Pohde and has no euro figure yet. We have **not** identified a grant or national money for the county pilot, and we do not claim one. Nothing has been sent to or agreed with either county.

**Comparison with the roadmap's national money.** The roadmap's €300,000 for 3.2.2–3.2.3 (pages 60–61) is national money for FICAN and THL to set up peer benchmarking between counties. It is **not county money and not Tasan's budget**. Tasan's county data could later feed that national process; that is the link, not a funding line. The roadmap's pathway money, about €5 M a year under 3.1.1, which also covers 2.5.2 and 3.1.2–3.1.4 (pages 54–56), is likewise national (FICAN, Duodecim, Palko). For scale only, not as a funding claim: one county's 90-day staff cost is roughly €20–31k, a small fraction of those national lines.

**If pressed for a total:** both pilot counties together come to €44,196–€52,462 on the base case. That is €20,339–€23,988 plus €23,857–€28,474. With Kymenlaakso's conditional coordinator, it is €50,059–€59,939. Same labels: staff cost only, estimate, 90 days.

### R8. "What is the day-90 stop/go rule?"

They are our design, not official targets. For T3, go if at least 85% of pathways have all four THL time points, the county baseline has been shown to the board, and at least 90% of day-28 alerts are actioned within two working days. Pause the dashboard and fix recording first if completeness stays under 70%. For T1, go if the missing step is in place, at least 20 suspected-lung-cancer patients have been through the redesigned path, the median referral-to-decision time is at least seven days shorter than the county's own T3 baseline, and non-pathway CT waits have not lengthened by more than 10%. For T2, go if at least 90% of new Lapland cases are listed at the existing OYS board before the treatment-intent decision — or coverage is at least 20 points above the week-1 audit — listing has not added more than seven days, and at least 90% of curative-radiotherapy recommendations have an OYS start date within 14 days, with travel booked. The curative share cannot be judged at day 90; there is registry lag.

### R9. "You have added reserved radiotherapy slots in Lapland. Will that close the 16.2 versus 29.8 gap?"

We will not promise that. For men, age-standardised surgery shares in an earlier report were 9.1% in Lapland and 9.0% in Vantaa-Kerava, so the later curative-record gap is not obviously a surgery-volume gap. Any-radiotherapy shares were 21.5% versus 32.3%, but that report does not split curative from palliative radiotherapy. "The gap is likely in curative radiotherapy" is our inference, and we will say so. T2's 90-day tests are coverage of the existing OYS board and booked curative-radiotherapy starts, not a move in the chart-estimate share.

### R7. "What is the KPI, in Goal 3's own words?"

Goal 3 on page 5: patients start treatment within the target times. Operationally, in the pilot: the percentage of lung-cancer patients whose first treatment starts within six weeks of referral arrival, using the strategy's named reference, labelled outdated. Secondary, and labelled as ours: a proposed 80% on-time bar, and a day-28 alert so the navigator acts before the six-week mark. Poor-prognosis five-year survival and the −10% mortality target are national Goal 3 headline indicators; a 90-day county pilot will not move them, and we will not claim it will. The men's chart-estimate share is context for why Lapland is a pilot, not the 90-day KPI.

---

## Data, clocks, and the demo

### Q1. "Is 46 versus 13.5 days the Goal 3 clock?"

No. Goal 3 is referral arrival to first treatment, in target times. Table 4.1 is diagnosis to first surgery, among the 11% of patients (N = 1,627) who had surgery within six months, YTA of residence, 2018 to mid-2022. The national surgery median is 37 days (IQR 0–56). South IQR is 33–63; North IQR is 0–44. In the North, at least a quarter of those patients have surgery on the diagnosis date. Drug times run the other way: North 42 days, South 36. We do not say "the South waits 3.4 times longer for treatment."

### Q2. "Why lung? Why not screening? Detection is where it starts."

The locked angle is Goal 3, treatment within target times, on a poor-prognosis cancer. Colorectal screening is Goal 2, and we will not lead with it. If you ask: in 2024, national colorectal screening coverage (Sotkanet 6103) was 73.5% (men 69.2, women 77.7). None of the 22 counties had reached the 80% Goal 2 bar. Helsinki men were 65.2%, Kymenlaakso men 65.6%. That can be an appendix action, not the pitch. We do not use Sotkanet 6411.

### Q3. "Can I trust the curative-record geography? Recording looks messy. And for men, is this even surgery?"

It is messy, and we say so. "No recorded treatment" ranges from 16.4% in Kymenlaakso to 43.1% in Varsinais-Suomi; Lapland is 33.8%. Some of the apparent access gap may be recording. Residence-based numbers describe residents, not the hospital that treated them. A separate, earlier report (2024, Taulukko 3.7) shows age-standardised *surgery* shares for men of 9.1% (6.0–13.7) in Lapland and 9.0% (5.5–14.1) in Vantaa-Kerava — CIs overlap completely — in a 2018–mid-2022 cohort. So for men, the later curative-record gap is not obviously a surgery-volume gap; curative radiotherapy may be part of the difference. That is our inference from a different cohort, and we will not hang the pitch on it.

### Q4. "Is any number in the app synthetic or example data?"

No. Since the 19:52 build, the app shows only public aggregate data. Chart-read values are labelled "chart estimate", and derived values are labelled "derived by Tasan". The people number (about 65 / about 12) is our arithmetic on published counts and is labelled illustrative. No county's six-week compliance appears anywhere, because none is published.

### Q5. "What about the legal maximum, or Swedish and Danish package pathways?"

The legal non-urgent specialist-care maximum is not our cancer target. The roadmap, 2.5.2 pages 52–53 and 3.1.2 pages 56–57, already points to Danish, Swedish and Norwegian package-pathway models as the design Finland will write into cancer-specific chains in 2026 to 2028. T1 is a county-level attempt to work in that spirit for lung, now, with a working six-week reference, not a claim that we have replaced the forthcoming national times.

### Q6. "Deaths, 13,300, county rates?"

13,316 cancer deaths in 2024, Statistics Finland table 13u5, against the strategy's baseline of about 13,300. We will not rank counties on crude death rates. Those rates run from 167 to 346 per 100,000 and are not age-standardised in the extract we have.

### Q7. "90 days — what would we actually see?"

A named signer and a named navigator. A county baseline for referral, diagnosis and first-treatment dates. Every day-28 case owned. In Lapland, a listing rule for the Oulu board and a count of how many cases were already on it. In Kymenlaakso, a written map of the diagnostic week and whether HUS slots are pre-agreed. We would not expect a change in five-year survival, or a trustworthy move in the chart-estimate share, in ninety days.

### Q8. "Why should AstraZeneca pick this up after Junction?"

Because the challenge brief asks for a follow-up with a Finnish wellbeing services county, and this is sized for that: one cancer, one clock, one navigator, 90 days, in a named county (Lapland), tied to Goal 3 as written. We are not claiming that any AstraZeneca–county pilot exists. The ask is to help us put the Lapland brief in front of the county's chief medical officer.

---

## If we do not know

Say "we have not sourced that," then offer the closest figure we have, with its caveats. Do not guess Oulu's current listing practice (that is the week-1 audit), Kymenlaakso's own median, a printed (non-digitised) age-standardised table number, or a euro total that includes unpriced CT lists, slots or travel. Staff-cost ranges may be quoted only as sourced above. Named office-holders have not agreed to sign. A wrong number is worse than an honest gap.
