# FINDINGS_REVIEW — harsh judge-eye read of `data/FINDINGS.md`

Reviewer: JN Pitch, 14 Nov 2026, Europe/Helsinki (EET). Every claim below was checked against the cited CSV, PDF/TXT extract, or Sotkanet/StatFin file in `data/`. Locked team decision (`PLAN.md`): name **Tasan**; angle = lung cancer, diagnosis → treatment start (Goal 3), with colorectal screening only as labelled Goal 2 context.

**Headline verdict.** Almost every *number* in FINDINGS.md is faithfully copied from its source. I found no unlabelled placeholder and no invented statistic. What judges will attack is **wording and framing**: a Goal 2 screening story dressed as "where inequality starts"; a 3.4× surgery-time comparison that is not the 6-week referral clock, not all patients, and not county-level (and whose North median is pulled down by same-day surgery); and a curative-treatment share sold as a window on Goal 3 survival — including a men's *chart-estimate* hero that must not be spoken as a published table number or as "all patients." None of those are fatal *as written in the memo*, because the memo often caveats itself. They become fatal the moment they are shortened for the stage.

The live app (`app/src/content/key_message.json`) still has `"is_example": true` and a synthetic 51–76 % "on-time treatment" range. That is not a FINDINGS error, but it is a **fatal demo risk** until replaced or clearly labelled EXAMPLE.

---

## Fatal (do not say this on stage; fix the wording first)

### F1. Leading with "Detection is where it starts"

**Sentence:** "Detection is where it starts. Colorectal (bowel) cancer screening reaches too few people." (FINDINGS.md, "THE single strongest, best-evidenced gap".)

**Why it is attackable.** The locked angle is Goal 3, diagnosis → treatment, lung. Screening 80 % is a **Goal 2** indicator (strategy p. 5); FINDINGS correctly labels that in parentheses, then undermines the label with "where it starts." The team's own lung data point the other way: the capital region is *worst* at colorectal and breast screening and *best* at lung curative-treatment share (Lapland 18.5 % vs Vantaa-Kerava 35.6 %). A judge will ask: if detection were where inequality starts, why does the same capital region then look better after diagnosis? The memo does not show that screening shortfalls cause the lung treatment or survival pattern. Section on bowel survival even says screening "cannot explain" those cohorts.

**Fix.** Do not use this sentence on stage or as the app headline. Reword the memo title to: "Best-evidenced *descriptive* gap in the public files is colorectal screening (Goal 2 context). The pitch gap is lung diagnosis-to-treatment (Goal 3), where public compliance data are missing." Keep screening as a labelled aside.

### F2. Saying the South waits "3.4 times longer" as if it were the Goal 3 clock

**Sentences:** "median to **surgery 13.5 d in Pohjois-Suomi vs 46.0 d in Etelä-Suomi** (3.4×)." and "Where the median is already ≥ 42 days, more than half of those patients exceeded 6 weeks from referral."

**Why it is attackable.** The numbers 13.5 and 46.0 match Taulukko 4.1 (printed p. 27; transcription checked against `raw/lung_figs/lung2024_t41-28.png`). The 3.4× arithmetic is correct (46/13.5). Everything else is a stretch:

- The THL 6-week target starts at **referral arrival**, not diagnosis (Ohjaus 21/2016, §4.1). The table starts at **diagnosis**.
- The rows are **medians among patients who received that modality within 6 months**, not all lung patients. The same report says only about **11 %** (N = 1 627) had surgery in six months; Pohjois-Suomi actually sent the *fewest* patients to surgery (9.5 % vs 14.8 % in Sisä-Suomi, Taulukko 4.5).
- **Radiotherapy and drug therapy do not show a 3.4× North–South gap.** Drug-therapy medians: Pohjois-Suomi 42.0 d vs Etelä-Suomi 36.0 d (North *slower*). Radiotherapy: Itä 25.0 vs Länsi 45.0. Cherry-picking surgery is obvious once the rest of the table is on screen.
- Geography is **collaborative area (YTA), 2018–mid-2022**, not a 2024 wellbeing-services county. Different years from the 2019–2023 curative-share table.
- No n, no CI, only IQR. North surgery IQR is **0–44 days**. A first quartile of 0 days is in the official table (and in the national surgery IQR 0–56), and it invites the question that diagnosis date sometimes *is* the surgery date.
- The "more than half exceeded 6 weeks *from referral*" line is the team's inference, not a table cell. The logic is a lower bound (if diagnosis→treatment median ≥ 42, referral→treatment is at least that long) and it holds only for the surgery subset in Etelä-Suomi (median 46) and, more weakly, Länsi radiotherapy (45) and Sisä drugs (43). It does not hold for "lung patients in the South."

**Fix, safe wording:** "Among lung-cancer patients diagnosed January 2018–June 2022 who had surgery within six months of diagnosis, the median time from diagnosis to surgery was 13.5 days in Pohjois-Suomi (IQR 0–44) and 46.0 days in Etelä-Suomi (IQR 33–63). In the North, at least a quarter of those patients have surgery on the diagnosis date (lower quartile 0). Source: Cancer Registry 2024, Taulukko 4.1, p. 27, by collaborative area of residence. This is not the official 6-week referral-to-treatment clock, covers roughly one in ten patients, and other first treatments do not show the same pattern." This figure is now **secondary** to the age-standardised men's chart-estimate share. Whenever 13.5 vs 46 is spoken, the same-day-surgery caveat must be in the same breath. Use the inference about exceeding six weeks only with that full subset clause, or not at all in the first minute.

### F3. Demo numbers that are not in FINDINGS (live app still EXAMPLE)

**Not a FINDINGS sentence — flag because it will be on the same stage.** `app/src/content/key_message.json` currently says the on-time treatment share "ranges from 51% to 76% across counties, a 25 percentage-point spread" and sets `"is_example": true`. FINDINGS itself says **no public county-level compliance** figure exists. If that range appears without a large EXAMPLE label, it is unsourced fiction and a Data-quality gate fail.

**Fix.** Do not put 51–76 % on stage. Sync real, caveated figures or show static source tables (Taulukko 4.1 and Taulukko 11) and say the missing county clock is the product.

---

## Major

### M1. Curative-treatment share sold as the Goal 3 survival indicator

**Sentence:** "G3 indicator 1 (5-year survival of poor-prognosis cancers): proxy is lung cancer curative-treatment share." then "Lapland 18.5 % … vs Vantaa-Kerava 35.6 % … National 27.0 %. Roughly 2× gap; CIs do not overlap."

**Checked.** 18.5 % (15.8–21.5; 131/710), 35.6 % (31.9–39.6; 212/595) and the mid-list (South Karelia 18.9, Kymenlaakso 19.3, Kainuu 20.8, North Karelia 21.4, Central Uusimaa 33.7, Helsinki 33.0) all match `csv/lung_report2026_treatment_by_wsc.csv`. National 27.0 % matches the 2026 report text (4 009 / 14 873). Wilson CIs were added by the data team, not printed in the table; that should be said. 35.6/18.5 = 1.92, so "roughly 2×" is fair if it stays a ratio of crude shares.

**Why it is attackable.** The official G3-a indicator is *five-year relative survival* for lung, pancreas and liver versus the Sweden–Norway average (strategy p. 5, footnote). County 5-year lung survival is, as FINDINGS says, not in a public downloadable table. A 12-month "parantava hoito" share is a different object: not survival, not Nordic, not stage-adjusted (stage is missing for 47.7 %). "No treatment record" ranges from 16.4 % (Kymenlaakso) to 43.1 % (Varsinais-Suomi); groups are **not mutually exclusive** (report text). Mid-list counties such as Kainuu (47/226, CI 16.0–26.6) and especially Keski-Pohjanmaa (33/148, CI 16.3–29.7, not in the headline list) have wide intervals. Figures are by **home municipality in the year of diagnosis**, so they describe residents, not the hospitals of that county.

**Update, 14 Nov 2026 evening.** The age-standardised county figures have now been digitised from Kuva 16 (see `data/LUNG.md` and `data/csv/lung_report2026_curative_agestd_by_sex_chart_estimate.csv`) and are the locked **hero**, for **men**, labelled as a chart estimate: Lapland ≈16.2 % [12.7–20.4] vs Vantaa-Kerava ≈29.8 % [24.2–36.1]. Both sides are men (like-for-like). The remaining attack is not "you ignored age." It is: these are not published table numbers (±1 pp); the hero is men only (women show a same-direction, slightly wider gap: ≈23.1 % [17.9–29.0] vs ≈39.7 % [33.1–47.0]); mixing them with crude all-patient 18.5 vs 35.6 would look sloppy; and nothing is stage-adjusted.

**Fix.** Lead with the men's chart estimate, always saying "men," "about," and "chart estimate." Put the drawn CIs on the slide. Keep crude Taulukko 11 figures for Q&A only. Do not say "16.2 percent of Lapland patients" or "twice as many patients are cured." Caveat recording and case mix in the same breath.

### M2. Mixing different cohorts into one "pathway"

**The pathway summary table** lines up 2024 screening, 2025 primary-care and referral indicators, 2018–22 YTA times, 2019–23 county treatment shares, and 2015–24 bowel survival as if they were stages of one journey.

**Why it is attackable.** Years, geographies (county vs YTA vs producer), and populations differ. A director cannot be told "your screening gap becomes your treatment delay becomes your survival gap" from these tables. FINDINGS already says screening cannot explain the bowel-survival cohorts (good). The pathway table still invites the causal reading.

**Fix.** Present each block with its years and unit of geography. Do not animate a single county "walking" from Sotkanet 6103 to Taulukko 4.1 to Sotkanet 3627.

### M3. THL cancer-specific times (3 weeks / 4 weeks) sitting next to the 6-week lung proxy

**Sentence:** "The target exists: **6 weeks from referral arrival to first treatment**, plus 1-week limits for imaging report, biopsy and pathology, and cancer-specific limits such as colon/rectum 3 weeks and breast 4 weeks from queue placement."

**Checked.** The 6-week and 1-week limits are verbatim in Ohjaus 21/2016 §4.1 (printed pp. 12–13 / PDF p. 14). The 3- and 4-week figures are from §4.3.2 diagrams (queue placement → first treatment for colon/rectum and breast), and TREATMENT_TARGETS.md already warns that the arrow-to-box reading should be re-checked against the PDF figures. The PDF is watermarked **Vanhentunut**. The roadmap (p. 57) plans to define cancer-specific target times only in 2026–2028.

**Why it is attackable.** A judge will hear "the target is three to six weeks" and then look at a lung surgery median. Lung has no cancer-specific THL queue-time in §4.3.2. The document is marked outdated, even though the strategy still cites it.

**Fix.** On stage, use only the generic 6-week referral→treatment limit, cite Ohjaus 21/2016 §4.1, and if asked, say the PDF is watermarked outdated and the roadmap is still defining cancer-specific times. Keep 3- and 4-week figures off the lung slide.

### M4. Primary-care waits in the pathway table, including Vantaa-Kerava 85.4 %

**Sentence:** "Non-urgent physician visits waiting > 7 days: 32.7 % (Päijät-Häme) – 85.4 % (Vantaa-Kerava), 2025 (Sotkanet 6411)."

**Checked.** The min/max match `csv/sotkanet_6411_phc_physician_wait_over_7d.csv` for 2025. FINDINGS later correctly says Avohilmo gaps in Vantaa, Kerava and Helsinki mean these "are not used for ranking." Putting Vantaa-Kerava 85.4 % in the summary table anyway is what a judge will screenshot.

**Fix.** Delete this row from any slide. If asked, say the indicator is weak and was not used for ranking.

**Update, 14 Nov 2026 evening.** FINDINGS.md and `data/hero.json` have now dropped Sotkanet 6411. Keep it off the stage.

### M5. Language as the explanation for low capital-region screening

**Sentence:** "A plausible explanation (our inference, not shown by these data) is the roadmap's own concern: participation among people whose mother tongue is not Finnish or Swedish (R p. 27, 33). **We found no public breakdown by language.**"

**Why it is attackable.** The inference is labelled, and the missing breakdown is honest — but "plausible explanation" still plants a cause the data do not show. Many other explanations (urban invitation logistics, occupational health overlap, age-band mix in rollout years) are equally untested.

**Fix.** Say only: "We have no public split by language or socio-economic group. The roadmap flags language as a national concern; we do not attribute the Uusimaa shortfall to it."

### M6. Age-standardised treatment shares — extracted, now the hero, still a chart estimate

**Status, 14 Nov 2026 evening.** The missed-defence issue is closed. Values were digitised from R2026 Kuva 16 (±1 pp) and locked as the hero for **men**: Lapland ≈16.2 % [12.7–20.4] vs Vantaa-Kerava ≈29.8 % [24.2–36.1]. Numbers, CIs and the "chart-digitised estimate" label match `data/LUNG.md`, the CSV, and the `age_standardised_check` block in `data/hero.json`. The comparison is like-for-like (men vs men).

**New attack surface.** (1) These are not published table numbers. (2) `data/hero.json`'s *headline* field still leads with the crude 18.5 vs 35.6 all-patient shares; the age-standardised men figures sit only under `age_standardised_check`. If the app or a slide reads the headline array, the locked hero will not appear. (3) Leading with men only, when women's point-estimate gap is slightly wider, is a cherry-pick question — answerable, because both sexes' CIs do not overlap. (4) Still not stage-adjusted.

**Fix.** On stage, use the men's chart estimates as worded in the safe-to-say list. Ask the builder to point the app hero at the age-standardised men values, labelled chart estimate, or to stop reading the crude headline as the hero.

---

## Minor

### m1. "5 / 22 for women" looks like all years

**Sentence:** "Counties (21 + Helsinki) at ≥ 80 % in 2024 | **0 / 22** total; **0 / 22** for men in 2022, 2023 and 2024; 5 / 22 for women."

**Checked.** 0/22 total in 2024, 0/22 men in 2022–2024, and **5/22 women in 2024 only** (16/22 in 2022, 10/22 in 2023). The cell is easy to read as "5/22 women every year."

**Fix.** Write "5 / 22 women in 2024 (16/22 in 2022, 10/22 in 2023)."

### m2. Extra people "≈ 27 200" / "≈ 22 300 are men"

**Checked.** Method: `abs_value` treated as number who attended; implied invitees = attended / (rate/100); shortfall to 80 %. National 2024: 27 404 extra; men 22 150 (`derived_colorectal_screening_gap_to_target.csv`). County largest shortfalls: Helsinki 4 367, Länsi-Uusimaa 2 731, Varsinais-Suomi 2 383 — consistent with "≈ 4 370, ≈ 2 730, ≈ 2 380." Implied invitees 421 593 ≈ 421 600. `key_findings.json` uses 27 214 and 22 260 — a small internal inconsistency with the national-row method.

**Why it is attackable.** The memo flags the abs_value assumption, but a rounded "27 200 people" sounds like a registry headcount. Sotkanet metadata was not independently re-read here beyond the team's note.

**Fix.** "Implied shortfall, if Sotkanet abs_value is the number who attended: about 27 400 more people nationally, of whom about 22 200 would be men." Do not fight over 27 200 vs 27 400 on stage.

### m3. Screening trend 77.3 → 74.4 → 73.5 without the rollout caveat in the table

**Checked.** National totals match Sotkanet 6103. The limitations section correctly says 2022–2024 are rollout years (ages 60–70 now, expanding to 56–74 by 2031) so the decline is not purely behavioural.

**Fix.** If the trend is spoken, add "rollout years, changing age band" in the same sentence.

### m4. Breast screening four lowest and "18 of 22 reach ≥ 80 %"

**Checked.** Sotkanet 3621, 2024, sex = total (women only in practice): Helsinki 74.3, Länsi-Uusimaa 76.1, Vantaa-Kerava 76.7, Itä-Uusimaa 79.8; 18/22 ≥ 80 %. Holds.

**Fix.** None for the numbers. Keep it as Goal 2 context; do not say it "confirms" a lung-care gap.

### m5. Referral-processing range without saying four areas are missing

**Sentence:** "Referrals processed ≤ 3 days: 68.9 % (Etelä-Pohjanmaa) – 88.7 % (Kanta-Häme), 2025 (Sotkanet 13); all specialties | Moderate, not cancer-specific, producer-based."

**Checked.** Min/max match. Only **18** wellbeing areas have 2025 values; Länsi-Uusimaa, Vantaa-Kerava, Itä-Uusimaa and Keski-Uusimaa are missing (HUS reports for Uusimaa; Helsinki is present). Not cancer-specific, producer-based: correctly flagged.

**Fix.** Add "18 of 22 areas; four Uusimaa counties missing." Do not use this as a lung-referral finding.

### m6. Bowel 5-year survival 63–74 %, national 68 % (up from 63 % in 2015)

**Checked.** Sotkanet 3627, 2024: Päijät-Häme 63; Satakunta, North Savo, Kainuu 64; Central Uusimaa 74; Vantaa-Kerava and Lapland 73; national 68, 2015 national 63. Age-standardised; 10 diagnosis years; no published CIs; small counties uncertain — all already in the limitations. "Screening started in 2022, so it cannot explain these survival cohorts" is the right warning.

**Fix.** Keep the warning. Do not put cervical 56–86 % on a slide (small n; FINDINGS already flags this).

### m7. "Only 5 % of all lung cancers are found localised (11 % of those with known stage)"

**Checked.** Verbatim in the 2026 report introductory text. Holds.

**Fix.** Keep the "of those with known stage" clause; stage is missing for 47.7 %.

### m8. Stage missing 47.7 % (7 097 / 14 873)

**Checked.** `csv/lung_report2026_stage_info_coverage_national.csv` and Table 4. Holds. Linking it to sub-goal 3.2's 90 % coverage target (strategy p. 36) is fair.

### m9. Cancer deaths 13 316 in 2024; county rates 167–346, crude only

**Checked.** StatFin 13u5: 13 316 deaths, C00–C97, 2024, whole country. County crude rates 167.2 (Vantaa-Kerava) to 345.5 (Kymenlaakso). The instruction "do not rank counties on them" is correct and must be kept.

### m10. "No treatment record" 16–43 %, Varsinais-Suomi 43.1 %

**Checked.** 16.4–43.1 % in the CSV. National text: 4 089 (27.5 %); county rows sum to 4 049 / 14 774 (Åland and a few missing home municipalities). The 2026 report also says 79 % of patients with no record died within a year — so this is not only a paperwork problem.

**Fix.** Say 16.4–43.1 %, and that many of these patients died within a year.

### m11. THL 2017 quote

**Checked.** Present in `raw/thl_hoitoonpaasy_loppuraportti_2017.txt`: "Kansallinen seuranta syöpään sairastuneiden hoitoonpääsystä on puuttunut." Holds.

### m12. Sotkanet 13 / 6411 and producer vs residence; 2023 county reform

Limitations section is accurate enough. Do not let these indicators drift onto the hero slide.

---

## Safe to say on stage (as worded here)

Use only these, with the source tag. Do not "tighten" them in the moment.

1. **Goal 3, strategy p. 5:** "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa." The strategy still names the generic clock: **6 weeks from referral arrival to first treatment** (THL Ohjaus 21/2016, §4.1). That PDF is watermarked *Vanhentunut*; it has no lung-specific limit; the roadmap (3.1.2, p. 57) sets cancer-specific times only in 2026–2028. Until then, use that six-week interval as a labelled working reference. Do not invent a replacement official number, and do not use Terveydenhuoltolaki §52 as a cancer target. A second Goal 3 headline is that 5-year survival of poor-prognosis cancers should reach the Nordic level (same page). Day-28 and an 80 % on-time bar are Tasan design, not official.
2. **No public regional compliance statistic** exists for that 6-week target. THL 2017: "Kansallinen seuranta syöpään sairastuneiden hoitoonpääsystä on puuttunut."
3. **Hero number, chart estimate, men only, like-for-like:** the age-standardised share of men with a curative-treatment record (surgery or curative radiotherapy) within 12 months, lung cancers diagnosed 2019–2023, wellbeing county of residence, is **about 16.2 % in Lapland [12.7–20.4] versus about 29.8 % in Vantaa-Kerava [24.2–36.1]**. Source: *Keuhkosyöpä Suomessa 2019–2023* (publ. 23.4.2026), Kuva 16, digitised by us (±1 pp); not a published table number. Always say "men," "about," and "chart estimate." The drawn intervals do not overlap (20.4 < 24.2); they still do not if each bound is moved 1 pp toward the other. We did not age-standardise: the registry used direct standardisation, standard = national patient age distribution in the study period, four groups (<60, 60–69, 70–79, 80+), sexes separate; CIs by normal approximation. This is not 5-year survival and not stage-adjusted.
4. **Women, same chart, if asked (not the hero):** Lapland women ≈23.1 % [17.9–29.0] vs Vantaa-Kerava women ≈39.7 % [33.1–47.0]; CIs also do not overlap. Do not mix sexes on one comparison line.
5. **Crude all-patient shares, if asked (not the hero):** curative-treatment *record* within 12 months, 2019–2023: **Lapland 18.5 % (95 % CI 15.8–21.5; 131/710)**, **Vantaa-Kerava 35.6 % (31.9–39.6; 212/595)**, **national 27.0 % (4 009 / 14 873)**. 2026 lung report, Taulukko 11; Wilson CIs computed by us. Not 5-year survival; not age- or stage-adjusted. CIs on the two extremes do not overlap.
6. **Surgery-time proxy, secondary, fully caveated:** among lung-cancer patients diagnosed 1/2018–6/2022 who had surgery within 6 months, median days from *diagnosis* to surgery were **13.5 in Pohjois-Suomi (IQR 0–44)** and **46.0 in Etelä-Suomi (IQR 33–63)**. Cancer Registry 2024, Taulukko 4.1, p. 27, collaborative area of **residence**, five areas only. About one in ten patients have surgery in that window. National median to surgery was 37 days (IQR 0–56). **Whenever this contrast is spoken:** in the North, at least a quarter of those surgery patients have surgery on the diagnosis date (Q1 = 0; also true in Itä and Sisä, and nationally). Radiotherapy and drug-therapy medians do not repeat the contrast (for drugs the North is slower: 42.0 vs 36.0). Do not say "3.4×."
7. **Stage coverage:** stage at diagnosis missing for **47.7 %** (7 097 / 14 873) of lung cancers 2019–2023 (Table 4). Sub-goal 3.2 target is 90 % coverage (strategy p. 36).
8. **Localised disease:** "vain pieni osa keuhkosyövistä todetaan paikallisena, 5 % kaikista potilaista ja 11 % niistä, joilta tieto on kansallisesti saatavissa" (2026 report text).
9. **Deaths:** 13 316 cancer deaths in Finland in 2024, C00–C97 (StatFin 13u5), matching the strategy's "13 300" baseline. County rates from this table are crude only — do not rank counties on them.
10. **Goal 2 context only, if there is time:** colorectal screening 2024, Sotkanet 6103: national **73.5 %** (men 69.2, women 77.7); **0 of 22** counties at the 80 % target (strategy p. 5). Lowest: Helsinki 69.6, Kymenlaakso 70.0, Vantaa-Kerava 71.3. Do not call this Goal 3 and do not say it causes the lung pattern. **Sotkanet 6411 has been dropped. Do not show it.**
11. **Bowel survival, if asked:** 5-year relative survival 2024 (diagnoses 2015–2024) ranges 63–74 % by county, national 68 % (Sotkanet 3627, age-standardised, no CIs). Screening from 2022 cannot explain these cohorts.

---

## Pending (do not invent to fill)

- A published (non-digitised) table of age-standardised curative shares — does not exist; Kuva 16 is the source, ±1 pp chart estimates only.
- `data/hero.json` headline still leads with crude 18.5 vs 35.6; the locked hero sits under `age_standardised_check`. Builder should not read the headline array as the stage hero.
- County-level cancer-specific referral → diagnosis → treatment times (not public).
- Official THL target-time compliance by region (does not exist — this is the product).
- Sourced nurse wage / employer cost, and a tariff for T2 physician-hours (euro figures in recs remain ESTIMATE). Do not use roadmap €300,000 (p. 60) as county money.
- Whether Oulu already reviews Lapland cases (mentor Q4).
- Live app still on labelled example data; no public URL confirmed in `app/PUBLIC_URL.txt` at review time.
- Mentor confirmation (e.g. Kaisa Kaitila) not yet in the evidence file.
