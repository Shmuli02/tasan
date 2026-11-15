# FINDINGS: Tasan — lung cancer, diagnosis → treatment (Goal 3)

Access/compute date 2026-11-14. Every number has its source in brackets. See also:
- Full source list: `SOURCES.md`
- Lung detail and verification: `LUNG.md`
- Headline numbers for the Builder: `hero.json` (supersedes `key_findings.json`)
- Data availability: `DATA_GAPS.md`
- Goal 3 mapping: `GOAL3_INDICATORS.md`
- Target times: `TREATMENT_TARGETS.md`

## ★ The pitch gap (Goal 3): lung cancer, diagnosis → treatment, and no public way to see it
**Goal 3 indicator 3** (S p. 5): "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa".
- The official clock is **6 weeks from referral arrival to first treatment** (THL Ohjaus 21/2016 §4.1, verified verbatim). There is no lung-specific target.
- **No public statistic reports compliance by region, for any cancer.** THL 2017: "Kansallinen seuranta syöpään sairastuneiden hoitoonpääsystä on puuttunut."
- That missing county clock is the product.

What the public registry reports do show, each with its own cohort and geography (do not chain them into one pathway):

| Measure | Regional contrast | Cohort / geography | Source |
|---|---|---|---|
| Curative-treatment record within 12 mo (crude) | **Lapland 18.5 % (CI 15.8–21.5; 131/710)** vs **Vantaa-Kerava 35.6 % (31.9–39.6; 212/595)**; national 27.0 % (4 009/14 873) | dx 2019–2023, wellbeing county of residence | R2026 Taulukko 11; Wilson CIs computed by us |
| Same, **age-standardised** | Lapland ≈16 % men / ≈23 % women vs Vantaa-Kerava ≈30 % / ≈40 %; CIs do not overlap in either sex | same | R2026 Kuva 16, chart-digitised ±1 pp |
| Median days diagnosis → surgery (surgery-first patients only) | **Pohjois 13.5 (IQR 0–44)** vs **Etelä 46.0 (33–63)**; national 37 (0–56) | dx 1/2018–6/2022, 5 collaborative areas | R2024 Taulukko 4.1, PDF p. 28 |
| Share of *all* patients whose first active treatment started ≤ 2 months from diagnosis | Länsi **27.7 %** vs Sisä **38.7 %** (Itä 38.0, Etelä 32.9, Pohjois 30.5) | same | derived from R2024 Taulukko 4.5 |
| 1-year relative survival, age-standardised | Pohjois **40.1 % (37.5–43.0)** vs Sisä **46.8 % (44.1–49.6)**; national 42.9 % | follow-up 2020–2022, collaborative area | R2024 Taulukko 5.1 |
| Stage at diagnosis missing | **47.7 %** (7 097/14 873) nationally; ≈22–68 % by county | dx 2019–2023 | R2026 Taulukko 4; Kuva 13 digitised |

R2024 = https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf · R2026 = https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html

**Say it safely**
- Surgery times:
  - The interval starts at diagnosis, not referral.
  - It covers only patients whose first treatment was surgery (nationally about 1 in 10).
  - Three areas have a lower quartile of 0 days, so diagnosis dating flatters them.
  - Radiotherapy and drug-therapy medians do not repeat the North–South pattern; for drug therapy the North is slower: 42.0 vs 36.0 d.
- Do **not** claim that more than half of patients exceeded 6 weeks.
- Curative share:
  - Call it "a crude share with a curative-treatment *record*". It is a proxy, not 5-year survival.
  - It is not adjusted for stage, comorbidity or recording.
  - The age-standardised chart shows that age alone does not explain the gap.
- The capital region does *better* on lung curative share. Do not chain this to the screening pattern below.

**G3 indicator 1** (5-yr survival of poor-prognosis cancers vs Nordic level)
- No public regional 5-year survival for lung, pancreas or liver.
- The nearest public measure is 1-year lung survival by collaborative area (above).
- Only 5 % of all lung cancers are found localised (11 % of those with known stage) [R2026 text].

**G3 indicator 2** (cancer mortality −10 %, baseline "13 300/yr")
- 2024: **13 316** cancer deaths (C00–C97) [StatFin 13u5].
- County rates are crude only (167–346 per 100 000). **Do not rank counties on them.**

## Goal 2 context (not Goal 3): colorectal screening
- National participation 2024: **73.5 %** (men 69.2 %, women 77.7 %).
- Trend: 77.3 % (2022) → 74.4 % (2023) → 73.5 % (2024). These are rollout years with a changing age band.
- **0 / 22** counties reached 80 % in 2024. For women it was 5 / 22 in 2024 (16/22 in 2022, 10/22 in 2023).
- Lowest: Helsinki 69.6 %, Kymenlaakso 70.0 %, Vantaa-Kerava 71.3 % [Sotkanet 6103].
- Implied shortfall, if Sotkanet abs_value is the number who attended: about **27 400** more people nationally, of whom about **22 200** would be men [`csv/derived_colorectal_screening_gap_to_target.csv`].
- Breast screening 2024: lowest in Helsinki 74.3 %, Länsi-Uusimaa 76.1 %, Vantaa-Kerava 76.7 % and Itä-Uusimaa 79.8 %; 18/22 counties are at or above 80 % [Sotkanet 3621].
- We have no public split by language or socio-economic group. The roadmap flags language as a national concern; we do not attribute the Uusimaa shortfall to it.
- Bowel 5-yr survival 2024 (dx 2015–2024): 63 % (Päijät-Häme) to 74 % (Central Uusimaa); national 68 % [Sotkanet 3627]. Screening began in 2022, so it cannot explain these cohorts.

## Evidence blocks (each with its own years and geography; not one causal pathway)
| Block | Evidence | Years / geography | Strength |
|---|---|---|---|
| Stage data coverage | Lung stage missing 47.7 %; ≈22–68 % by county | 2019–23, county (chart) | data gap is the finding |
| Referral → specialist (all specialties) | Referrals processed ≤ 3 days: 68.9 % (Etelä-Pohjanmaa) – 88.7 % (Kanta-Häme) [Sotkanet 13]; 18 of 22 areas, four Uusimaa counties missing | 2025, producer | weak for cancer |
| Diagnosis → treatment (lung) | Surgery median 13.5 vs 46.0 d; ≤ 2-month treatment start 27.7–38.7 % | 2018–mid-2022, YTA | moderate, recording caveats |
| Treatment (lung) | Curative 18.5 → 35.6 % crude; gap persists age-standardised | 2019–23, county | moderate–strong |
| Outcome (lung) | 1-yr survival 40.1 → 46.8 % | 2020–22, YTA | moderate |
| Screening (Goal 2) | Colorectal 69.6–76.9 %, 0/22 at target | 2024, county | strong, but Goal 2 |

## Limitations (please read before pitching numbers)
- **Wellbeing-county reform 2023.** Series before 2023 were re-aggregated by THL to today's 21 counties + Helsinki. Referral and queue indicators are reported per **producer**: HUS reports for the whole of Uusimaa, and Helsinki's specialist-care data are missing May 2021 → 2024 (Sotkanet metadata 3336).
- **Survival indicators (Sotkanet 3625–3627)** pool 10 diagnosis years with a 5-year follow-up window. They are age-standardised, but small counties (Kainuu, Keski-Pohjanmaa, Itä-Uusimaa) have wide uncertainty and no CIs are published. Cervical cancer has very small numbers.
- **Screening 2022–2024** = rollout years of the colorectal programme, which currently invites ages 60–70 and expands to 56–74 by 2031 [cancerregistry.fi]. The cohort mix changes year to year, so the trend is not purely behavioural.
- **Lung reports:** see `LUNG.md`.
  - County shares in Taulukko 11 are crude. Age-standardised versions exist only as charts (Kuva 15/16), which we digitised at ±1 pp.
  - "No treatment record" varies 16.4–43.1 % by county.
  - Drug therapy is barely recorded in Varsinais-Suomi (≈1 %, age-standardised, R2024 Taul 3.7), so recording differences contaminate county comparisons.
  - Diagnosis-to-treatment times are published by collaborative area only, for 2018–mid-2022.
- **Registry lag:** Cancer Registry statistics have a 1–2 year lag; the preliminary year misses about 6 % of cases [syoparekisteri.fi tautitilastot page].
- **Primary care waits (Sotkanet 6411):** the indicator covers all causes, not cancer. Avohilmo has large data gaps in Vantaa, Kerava and Helsinki (Sotkanet metadata). **Removed from the pathway table and from hero.json. Do not show it.**
- **Missing publicly:**
  - stage distribution by county for any cancer
  - cancer-specific referral→diagnosis→treatment times by county
  - screening participation by language or socio-economic group
  - lung, pancreas and liver 5-year survival by county as downloadable tables. The Cancer Registry Shiny app may show regional survival; it is websocket-only, was not accessed, and this is unconfirmed.
  - age-standardised cancer mortality by county
  - Findata: not explored in depth; we found no ready-made aggregate cancer tables (Findata grants permits for microdata)
