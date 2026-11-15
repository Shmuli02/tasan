# data/app — chart-ready JSON for the Tasan app

Built by `scripts/build_app_data.py` and validated by `scripts/check_app_data.py` (3 374 checks; it exits with status 1 on any failure). Both run at the end of `scripts/run_all.sh`.

## Inputs and conventions
- **Inputs (read-only):**
  - `csv/*.csv`
  - `hero.json` (people_number)
  - `facts.json`
  - Nothing new was fetched.
- **Format:** compact UTF-8. Flat arrays of records. `null` means not available, and each null comes with a `null_reason` / `*_null_reason`.
- **`measure_type`** is one of:
  - `published`: number printed in the source;
  - `computed_by_tasan`: our arithmetic, such as Wilson CIs, ranks, per-year values and derived 2-month shares;
  - `chart_estimate`: read from figure pixels, ±1 pp, so say "about";
  - `no_public_data`.
- **Sources:** every value carries `fact_ids` (ids from facts.json; can be empty when no atomic fact exists) **and/or** `source_url` + `source_table` (always present).
- **Area level:** fields prefixed `yta_`, and the `*_yta_*` fields, are **AREA-LEVEL (collaborative area), not county**. They are linked to counties through the R2026 Taulukko 11 Yhteistyöalue column. They come from the older 2024 report cohort (dx 1/2018–6/2022).
- **Goal labels:** Goal 3 (strategy p.5) has exactly 3 indicators: survival of poor-prognosis cancers, cancer mortality −10%, and treatment within target times. Screening is **Goal 2 context** and is never labelled Goal 3.

## counties.json
`{generated, note, national{…, src}, counties[22]}`

Each county record has:
- **Identity:** `region, region_name_fi, region_code (01–21, 90 Helsinki), yta_code, yta_name`
- **Crude curative share:**
  - `curative_crude_pct, curative_n, curative_N, curative_ci95_low/high` — crude curative share, 2019–2023, Taulukko 11, published. The CI is Wilson, computed_by_tasan.
  - `curative_rank` (1 = highest; standard competition ranking, so ties share the best rank), `curative_rank_tied`, `curative_rank_of`, `curative_vs_national_pp`
- **Case volume:** `cases_2019_2023`, `cases_per_year` (= /5)
- **Age-standardised curative share:** `curative_agestd_{men,women}_pct` + `_ci95_low/high` — chart_estimate from Kuva 16. Kainuu is null, with a reason.
- **Stage:** `stage_missing_pct` — chart_estimate from Kuva 13.
- **People gap:** `people_gap_per_year` — from hero.json people_number, computed_by_tasan; 0 = at or above the national share.
- **Area-level values:** `yta_level_flag` = "area-level, not county", plus:
  - `yta_surv1y_pct` + CI (R2024 Taulukko 5.1)
  - `yta_dx_to_surgery_median_days/q1/q3` (Taulukko 4.1)
  - `yta_treated_within_2m_pct` (derived from Taulukko 4.5)
- **Goal 2 block:** `goal2_colorectal_screening_2024_{total,men,women}_pct`, `goal2_screening_target_pct` = 80 (Sotkanet 6103).
- **`src`:** `{field_group: {measure_type, fact_ids, source_url, source_table, csv, caveat?, null_reason?}}`

## curative_agestd_ranked.json (Builder ask 1)
`{method, caveat, records[]}`

Each record has: `sex (men|women), region, region_code, level, value_pct, ci95_low, ci95_high, rank, rank_of, measure_type, fact_ids, source_url, source_table, null_reason?, note?`

`level` is one of:
- `county`: 22 per sex; Kainuu is null because it is suppressed in the figure.
- `yta`
- `national_reference_sex_specific`: Kuva 15 line; men ≈24.9, women ≈30.0.
- `national_reference_figure16_line`: ≈27 in both panels, which equals crude 27.0%.

All values are chart estimates (±1 pp). The method is described in the file.

## yta.json
Sections (arrays):
- `membership`
- `timing_medians` — Taulukko 4.1: `treatment`, `median_days`, `q1_days`, `q3_days`
- `first_event_curves` — Taulukko 4.5: `month`, `event`, `cumulative_pct`
- `treated_by_month` — derived: `month 1–6`, `treated_pct` + CI
- `survival_1y` — Taulukko 5.1: by sex, with CI
- `curative_crude` — R2026 Taulukko 10: `n`, `N`, `CI`
- `curative_agestd` — Kuva 15 chart estimate

Each record has `yta_code` + `measure_type` + source.

## pathway.json
`{goal3_indicators[3], steps[6], note}`

Each step has: `order, id, label_en, label_fi, targets[], public_data, no_public_data, cancer_specific?, best_metric{name, level, years, measure_type, source_url, source_table, values[{area, area_code, value,…}], caveat}, secondary_metric?, null_reason, fact_ids`

The steps are:
1. symptoms/primary care
2. referral
3. diagnosis
4. MDT
5. treatment_start
6. follow_on_treatment

Each entry in `targets[]` has: `label, value, unit, clock_start, status ("verified verbatim" | "diagram (primary source only)" | "verified absent"), fact_id, source_url, source_table`. Lung has no specific target.

## pathway_by_county.json (Builder ask 3)
Fields per county record:
- `referral_value` — Sotkanet 13: % of referrals processed within 3 days, 2025. All specialties, producer-based, **not cancer-specific**. Null for 01–04.
- `diagnosis_value` — always null, with a reason. It is supplemented by `diagnosis_stage_missing_pct` (chart_estimate).
- `treatment_start_value` — always null, with a reason. It is supplemented by `treatment_start_yta_*` values and `treatment_start_yta_flag` = "YTA-level, not county".
- `curative_share_pct` + CI
- `target_compliance_value` — always null, with a reason.

## timeseries.json (Builder ask 2)
`{series[], records[]}`, in long format.

Each record has: `series_id, region, region_code, sex, year, value, unit, measure_type, fact_ids, source_url, source_table, caveat`

| series_id | Coverage |
|---|---|
| `colorectal_screening_attendance` | Sotkanet 6103, 2022–24, counties + national, by sex |
| `breast_screening_attendance` | Sotkanet 3621, 2010–24 |
| `bowel_survival_5y` | Sotkanet 3627; no 2018 in source |
| `cancer_deaths_all` | StatFin 13u5, national, 2019–25 |
| `lung_larynx_deaths` | C32–34, national |
| `cancer_deaths_all_by_county` | counts; do not rank |
| `lung_new_patients` | R2026 Taulukko 5, national, 2019–23; serves as lung incidence (patients by year of follow-up start) |
| `lung_procedure_recorded_pct`, `lung_mdt_recorded_pct`, `lung_died_12m_pct` | R2026 Taulukko 5, national |

## Gaps (null on purpose)
- County-level lung timing
- Time to diagnosis
- 6-week compliance anywhere
- Surgery → adjuvant times
- County lung survival
- Lung data after 2023
- Kainuu age-standardised value
- Sotkanet 13 for the 4 Uusimaa counties
- Lung incidence by county per year (only 5-year totals by county)
