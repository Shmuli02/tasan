# Two-minute story: Tasan (DECISION 3: one number, one county, one ask)

**Rewritten:** Sat 14 Nov 2026, 20:15 EET, from `PLAN.md` DECISION 3 and `review/WIN_PLAN.md`. The spoken text is the same as `PITCH_SCRIPT.md`; the demo slot sits between paragraphs 3 and 4.
**Audience:** AstraZeneca Marketing and Business Excellence judges (non-clinical). Sunday 15 Nov, 14:00 Europe/Helsinki.
**One number:** people number (verbatim, from the steering message; basis in `data/hero.json` → `people_number`). **One county:** Lapland. **One ask:** sign the 90-day pilot.

---

Same cancer, different postcode. About 65 more lung cancer patients a year would get curative treatment if every below-average county reached the national rate. That's Cancer Registry counts for 2019 to 2023. It's illustrative, and it isn't stage-adjusted. About 12 of them a year are in Lapland.

And it isn't just age. Age-adjusted, about 16 in 100 men with lung cancer in Lapland have a curative-treatment record within a year, against about 30 in 100 in Vantaa-Kerava. That's a chart estimate from the 2026 Cancer Registry report. The intervals, about 13 to 20 and 24 to 36, don't overlap. Women show the same gap. It's not survival.

Goal 3 of Finland's cancer strategy says patients must start treatment within the target times. Today no county can see that clock for its own patients. Tasan is that clock.

*[Demo, 60 s: day-28 clock → the AI says "no county publishes this" → the pilot brief. See PITCH_SCRIPT.md.]*

Lapland can start on Monday. The chief medical officer signs a 90-day pilot: one nurse navigator and half an analyst. Staff cost only, estimate: about twenty to twenty-four thousand euros. In the first 30 days we measure Lapland's own baseline and check the registry against the hospital's records. After that, every patient with no treatment decision by day 28 goes to the navigator. On day 90 the county decides go or stop. Day 28 and the 80 percent bar are our design choices. The six-week reference is a THL 2016 document that is marked outdated.

Your challenge asks for a follow-up with a Finnish wellbeing services county. Our ask: help us put this brief in front of Lapland's chief medical officer. Ninety days, one clock, one nurse. Tasan, koska hoito ei saa riippua postinumerosta.

---

**Spoken-word count (body, excluding the demo line):** 271. That is about 2:00 at a calm pace. Cut first: "Women show the same gap" and the 30-day sentence.

**Sources behind every spoken number:**
- **People number.** Tasan's arithmetic on *Keuhkosyöpä Suomessa 2019–2023* (Syöpärekisteri/THL/FICAN, publ. 23.4.2026), Taulukko 11 counts by wellbeing county.
  - Method: for each of the 12 counties below the national 4,009/14,873 = 26.95%, gap = 0.2695 × patients − curative patients. The sum is 324.6 over 5 years, ≈ 65 a year. Lapland: 0.2695 × 710 − 131 = 60.4, ≈ 12 a year.
  - Re-computed by JN Pitch from `data/csv/lung_report2026_treatment_by_wsc.csv` on 14 Nov 20:12: it matches.
  - Caveat (`hero.json`): illustrative, not a published estimate and not causal. Crude shares, not age- or stage-adjusted (stage is missing for 48%). Benchmark = national average, not a clinical optimum. Does not say how many lives would be saved.
- **Proof.** Same report, Kuva 16, age-standardised by sex, chart-digitised ±1 pp: Lapland men 16.2 (12.7–20.4) vs Vantaa-Kerava men 29.8 (24.2–36.1); women 23.1 (17.9–29.0) vs 39.7 (33.1–47.0).
- **Goal 3 wording:** strategy 2026–2035, p. 5. Missing regional six-week monitoring: THL 2017. Six-week reference: THL Ohjaus 21/2016 §4.1, watermarked *Vanhentunut*. Day 28 and 80% are Tasan design.
- **Cost:** `recs/pilot_brief.md` / `recommendations.json`, T3 €20,339–€23,988 per county, 90 days. KT Oct 2025 pay × 2026 employer contributions of 23.14%. Staff only.
- **Signer:** johtajaylilääkäri, Lapin hyvinvointialue (Jyri J. Taskila, verified on the county site 14 Nov). Draft, not discussed with the county.

**Do not speak:**
- "lives saved", "deaths prevented", "patients denied treatment", or an exact people number (always "about").
- Any claim that AstraZeneca has or runs a pilot with a Finnish county.
- The "17% earliest stage" figure.
- 13.5 vs 46 days, Kymenlaakso, T1/T2, the Oulu board.
- "16.2% of Lapland patients" (it is men).
- Day 28 or 80% as official targets.
- Euros without "staff cost only, estimate".
- Sotkanet 6411; colorectal screening.

**Held for Q&A (`JUDGE_QA.md`):** derivation and attack lines for the 65; why Lapland; counties with no data; the AI's limits; crude 18.5 vs 35.6; women; Kymenlaakso, T1, T2; the full Lapland cost with the Oulu-board coordinator (€23,857–€28,474); 13.5 vs 46 days.
