# SOURCES

Access date for everything: **2026-11-14** (Europe/Helsinki). Raw copies are in `raw/`. Scripts are in `scripts/` (`scripts/run_all.sh` reproduces everything).

## 1. THL Sotkanet (REST API 1.1)

- API: `https://sotkanet.fi/rest/1.1/json?indicator=<id>&years=...&genders=...`; metadata: `https://sotkanet.fi/sotkanet/en/metadata/indicators/<id>`. Regions: wellbeing services counties (HYVINVOINTIALUE, 21 + Helsinki + Åland; Åland excluded from spreads) + whole country (code 358). The API requires a User-Agent header (403 without).

| ID | Indicator | Data source (per metadata) | Years fetched (region data) | data-updated | CSV |
|---|---|---|---|---|---|
| 13 | Referrals for specialised health care received processed within 3 days, % of referrals received | Access to specialised health care (THL) | 2014–2025 | 2026-06-05 | `csv/sotkanet_13_esh_referrals_processed_within_3d.csv` |
| 186 | Mortality per 100 000 inhabitants | Deaths (Statistics Finland) | 2010–2025 | 2026-05-25 | `csv/sotkanet_186_mortality_all_cause_per_100000.csv` |
| 245 | Cancer index, age-standardised (up to 2019) | Morbidity indices (THL) | 2010–2019 | 2022-04-25 | `csv/sotkanet_245_cancer_index_agestd_old.csv` |
| 2676 | Waiting time for elective outpatient medical visit (physician) in primary health care exceeds 7 days from assessment of the need for treatment, % appointments kept (March) (up to 2024) | Primary health care (THL) | 2015–2024 | 2024-05-02 | `csv/sotkanet_2676_phc_physician_wait_over_7d_march_old.csv` |
| 3175 | Waiting time of over 3 months since assessment of the need for treatment for a non-emergency appointment with a primary health care doctor in outpatient care, % of completed appointments (status in March) (up to 2024) | Primary health care (THL) | 2015–2024 | 2024-05-02 | `csv/sotkanet_3175_phc_physician_wait_over_3m_march_old.csv` |
| 3336 | Patients waiting over 6 months during the year for access to specialised health care per 10 000 inhabitants | Access to specialised health care (THL) | 2014–2025 | 2026-06-05 | `csv/sotkanet_3336_esh_waiting_over_6m_per_10000.csv` |
| 3620 | Proportion of women invited to cervical cancer screening (smear test) who attended, % | Screening statistics (Finnish Cancer Registry) | 2010–2024 | 2026-06-12 | `csv/sotkanet_3620_screening_cervical_attendance.csv` |
| 3621 | Proportion of women invited to breast cancer screening (mammography) who attended, % | Screening statistics (Finnish Cancer Registry) | 2010–2024 | 2026-06-12 | `csv/sotkanet_3621_screening_breast_attendance.csv` |
| 3625 | Five-year relative survival rate of breast cancer patients, % | Cancer statistics (Finnish Cancer Registry) | 2015–2024 | 2026-06-12 | `csv/sotkanet_3625_survival5y_breast.csv` |
| 3626 | Five-year relative survival rate of cervical cancer patients, % | Cancer statistics (Finnish Cancer Registry) | 2015–2024 | 2026-06-12 | `csv/sotkanet_3626_survival5y_cervical.csv` |
| 3627 | Five-year relative survival rate of bowel cancer patients, % | Cancer statistics (Finnish Cancer Registry) | 2015–2024 | 2026-06-12 | `csv/sotkanet_3627_survival5y_bowel.csv` |
| 5033 | Referrals for specialised health care received after processing for more than 21 days, % of the referrals received | Access to specialised health care (THL) | 2014–2025 | 2026-06-05 | `csv/sotkanet_5033_esh_referrals_processed_over_21d.csv` |
| 5073 | Referrals received for specialised health care per 1000 inhabitants | Access to specialised health care (THL) | 2017–2024 | 2025-04-04 | `csv/sotkanet_5073_esh_referrals_per_1000.csv` |
| 5083 | Wait time for patients awaiting specialised health care as of 31 December, median | Access to specialised health care (THL) | 2017–2022 | 2023-04-18 | `csv/sotkanet_5083_esh_median_wait_dec31.csv` |
| 5093 | Entitled to special refunds on medicines for cancer 31.12., age-standardised population share(%) | Statistics on reimbursement entitlements in respect of medicines (Kela) | 2017–2025 | 2026-03-09 | `csv/sotkanet_5093_kela_cancer_med_refund_agestd.csv` |
| 5395 | Entitled to special refunds on medicines for cancer 31.12., as % of total population | Statistics on reimbursement entitlements in respect of medicines (Kela) | 2017–2025 | 2026-03-20 | `csv/sotkanet_5395_kela_cancer_med_refund_crude.csv` |
| 5643 | Cancer index, age-standardised | National Health Index (Kela and THL) | 2017–2024 | 2026-06-11 | `csv/sotkanet_5643_cancer_index_agestd.csv` |
| 5644 | Cancer index, not age-standardised | National Health Index (Kela and THL) | 2017–2024 | 2026-06-11 | `csv/sotkanet_5644_cancer_index_crude.csv` |
| 6103 | Proportion of invited to colorectal cancer screening who attended, % | Screening statistics (Finnish Cancer Registry) | 2022–2024 | 2026-06-12 | `csv/sotkanet_6103_screening_colorectal_attendance.csv` |
| 6410 | Waiting time of over 3 months since assessment of the need for treatment for a non-emergency appointment with a primary health care doctor in outpatient care, % of completed appointments | Primary health care (THL) | 2021–2025 | 2026-05-13 | `csv/sotkanet_6410_phc_physician_wait_over_3m.csv` |
| 6411 | Waiting time for elective outpatient medical visit (physician) in primary health care exceeds 7 days from assessment of the need for treatment, % appointments kept | Primary health care (THL) | 2021–2025 | 2026-05-13 | `csv/sotkanet_6411_phc_physician_wait_over_7d.csv` |
| 10024 | (EU) Standardised death rate due to cancer per 100 000 persons | Unit F5: Education, health and social protection (Eurostat) | – | 2019-01-03 | `n/a (no county data)` |

Notes/limitations (from Sotkanet metadata):
- 13, 5033, 3336, 5073 (specialist-care access): data are **producer-based, not by residence**. HUS reports for all of Uusimaa. Helsinki specialist-care access data are missing May 2021 → start of 2025 (metadata 3336). All specialties, not cancer-specific.
- 6411/6410/2676/3175 (primary care waits): Avohilmo gaps in Vantaa (since 2019), Helsinki and Kerava (since 2021); in 2024 Vantaa is still missing ~20 % of visits and Kerava ~30 % (metadata 6411).
- 3625–3627 survival: 'year' = statistical year; patients diagnosed in that year and the 9 preceding years, followed during the year and the 4 preceding years; age-standardised to the national patient age structure. No CIs published.
- 6103 colorectal screening: programme rollout started 2022 (ages 60–70 now; 56–74 by 2031, https://cancerregistry.fi/screening/colorectal-cancer-screening/). `abs_value` is assumed to be the number who attended (used in the derived shortfall).
- 5643/5644 'Cancer index' = Kela/THL National Health Index component (not incidence per se); 10024 has no county data (EU/Nordic only, up to 2015).
- 186 = all-cause mortality (context only).

## 2. Statistics Finland, StatFin cause-of-death table 13u5
- API: https://pxdata.stat.fi/PXWeb/api/v1/fi/StatFin/ksyyt/13u5.px (POST json-stat2). Table: 'Kuolleet ja yleinen kuolleisuusluku tilaston peruskuolemansyyn (aikasarjaluokitus) mukaan hyvinvointialueittain, 1969–2025'. Causes fetched: 04-21 all cancers (C00–C97), 07 colon, 08 rectum/anus, 10 pancreas, 11 larynx/trachea/lung, 13 breast. Years 2019–2025. → `csv/statfin_13u5_cancer_deaths_by_wsc.csv`, raw `raw/statfin_13u5_cancer_deaths.json`.
- **Limitation: crude rates only, NOT age-standardised** → do not compare counties on rate. Deaths are by place of residence.

## 3. THL specialist-care queues cube (eshjono / jonotilanne)
- Cube: https://sampo.thl.fi/pivot/prod/fi/eshjono/jonotilanne/fact_eshjono_jonotilanne (dimensions JSON `.dimensions.json`, data `.json?row=…&column=…&filter=…`). Summary page: https://sampo.thl.fi/pivot/prod/fi/eshjono/jonotilanne/summary_hvaraportti. Filter: erikoisala 65 *Syöpätaudit* (sid 862186). Dates: 31.12.2023, 31.12.2024, 31.12.2025, 30.09.2026. Measures: waiting for treatment (n, >90 d n/%, >180 d %), waiting for assessment (n, >90 d %). → `csv/thl_eshjono_oncology_waits_by_wsc.csv`
- Limitations: non-urgent care only (most cancer treatment is urgent → not captured); unverified monthly data; producer-based; tiny counts (1–283 per county) → unstable %.

## 4. Finnish Cancer Registry / THL / FICAN lung-cancer quality reports
- *Keuhkosyöpä Suomessa 2019–2023 – rekisteripohjainen katsaus* (HTML factsheet, published 23.4.2026): https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html — Taulukko 11 (treatment groups & MDT by wellbeing county; N=14 873 lung cancers C33–C34 diagnosed 2019–2023, 12-mo follow-up) → `csv/lung_report2026_treatment_by_wsc.csv` (Wilson 95 % CIs added by us); Taulukko 4 (stage-information coverage) → `csv/lung_report2026_stage_info_coverage_national.csv`; Kuva 13 image saved `raw/lung_figs/Kuva_13.png` (county stage coverage, chart only). News: https://kehitys.fican.fi/keuhkosyovan-toteamisessa-on-eroja-hyvinvointialueiden-valilla-tietojen-kattavuudessa-edelleen-parannettavaa/
- *Keuhkosyöpä Suomessa – Katsaus keuhkosyövän hoidon laadusta* (PDF, Nov 2024): https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf — Taulukko 4.1 (days from diagnosis to first treatment by collaborative area; cohort 1/2018–6/2022, N=13 324), printed p. 27 → `csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv` (**manually transcribed** from the table image; image `raw/lung_figs/lung2024_t41-28.png`).
- Limitations: crude shares; recording completeness differs by county ('no treatment record' 16–43 %); MDT recorded almost only in Sisä-Suomi.

## 5. National cancer strategy and roadmap
- Strategy: https://files.hackjunction.app/resources/Kansallinen_syopastrategia_2026_2035_FINAL.pdf (64 pp.) — Goals/indicators p. 5 (Kuva 1), Goal 3 section pp. 32–42.
- Roadmap 2026–2031: https://files.hackjunction.app/resources/Kansallinen_syopastrategia_toimeenpanon_tiekartta_2026_2031.pdf (111 pp.) — regional inequality p. 12, screening target p. 48, Goal 3 section from p. 54 (target-time measure p. 57).
- Resource link list: https://files.hackjunction.app/resources/Sy%C3%B6p%C3%A4strategiat%20ja%20sy%C3%B6p%C3%A4data_linkkikokoelma.pdf
- Identical (md5) to copies in `/workspace/junction-new/pitch/sources/`.

## 6. Treatment target times
- THL Ohjaus 21/2016 *Hoitoonpääsyn seuranta syövän hoidossa* — item https://www.julkari.fi/items/0424a55a-f159-406f-8883-5dfdad4d6772 ; PDF https://www.julkari.fi/server/api/core/bitstreams/de33d584-bdce-40a1-b100-df48c4906a49/content (watermarked 'Vanhentunut'; see TREATMENT_TARGETS.md). Sections 4.1 (PDF p. 14) and 4.3.2 (PDF pp. 19–20).
- THL Työpaperi 3/2017 *Hoitoonpääsyn seuranta syövän hoidossa – Kehittämishankkeen loppuraportti*: https://www.julkari.fi/items/c296653c-356e-4742-a029-ddab51cd0aab (PDF https://www.julkari.fi/server/api/core/bitstreams/c0c8c67d-3b8b-4016-ad52-b40682713441/content).
- FICAN statement 28.2.2025 (quoted via search extract, not downloaded): https://fican.fi/wp-content/uploads/2026/08/FICANin-lausunto-luonnoksesta-hyvinvointialueiden-tehtavia-koskeviksi-valtakunnallisiksi-tavoitteiksi-vuosille-2025-2029-28.02.2025.pdf
- HUS waiting-time page (oncology median 7 d on 30.9.2026; via search extract): https://www.hus.fi/potilaalle/opas-potilaalle/oikeutesi-potilaana/hoitoonpaasy-erikoissairaanhoidossa

## 7. Other context pages
- Cancer Registry statistics pages (publication lag, ~6 % missing in preliminary statistics): https://syoparekisteri.fi/tilastot/tautitilastot/ ; interactive app https://tilastot.syoparekisteri.fi/syovat/ (R Shiny, not scraped) ; clinical-notification statistics https://syoparekisteri.fi/tilastot/kliinisten-ilmoitusten-tilasto/ (not extracted).
- Colorectal screening programme description: https://cancerregistry.fi/screening/colorectal-cancer-screening/

## 8. Derived files (our computations)
- `csv/spreads_by_indicator_year.csv` — min/max/gap/ratio/ranking across counties (excl. Åland) for each Sotkanet indicator, year and sex (`scripts/spreads.py`).
- `csv/derived_colorectal_screening_gap_to_target.csv` — implied invitees, gap to 80 %, extra attendees needed (`scripts/derived_metrics.py`).
- `combined.json` — all CSVs combined; `key_findings.json` — headline numbers for the demo app.

## Not found / not used
- No public county-level stage distribution, cancer-specific waiting times, poor-prognosis survival tables, age-standardised county cancer mortality, or screening participation by language/socio-economic group.
- Findata: not explored in depth; no ready-made aggregate cancer tables found.
- NORDCAN (national Nordic comparison only) not fetched.

## Added 2026-11-14 (lung deep-dive, Goal 3 hero)
- **Keuhkosyöpä Suomessa (2024)** https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf
  - Tables are vector graphics and were **manually transcribed** from 200-dpi renders (`raw/lung2024_pages/`).
  - Cross-checked with independent OCR (RapidOCR; 1 174/1 199 numbers matched verbatim, the 25 misses were re-read visually) and with internal sums.
  - Tables used: Taul 3.3/3.4 (PDF p.18–19), 3.6 (p.23), 3.7 (p.25–26), 4.1 (p.28), 4.5/4.6 (p.34–35), 5.1 (p.36), 5.3 (p.39).
  - Output: `csv/lung_report2024_*.csv` (`scripts/build_lung2024_tables.py`).
  - Derived output: `csv/lung_derived_first_active_treatment_by_month_yta.csv` (`scripts/derived_lung_first_treatment_by_month.py`).
- **Keuhkosyöpä Suomessa 2019–2023 (2026)** https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html
  - Taulukko 10 (YTA) → `csv/lung_report2026_treatment_by_yta.csv`.
  - Kuva 15/16 (age-standardised curative share by sex, YTA/HVA) **digitised** → `csv/lung_report2026_curative_agestd_by_sex_chart_estimate.csv` (`scripts/digitise_lung2026_agestd_curative.py`).
  - Kuva 13 (stage-missing by HVA) **digitised** → `csv/lung_report2026_stage_missing_by_wsc_chart_estimate.csv` (`scripts/kuva13_stage_missing_estimate.py`).
  - All figure images are in `raw/lung_figs/img2026_*.png`.
  - Digitised values are ±1 pp estimates, not published numbers.
- THL Ohjaus 21/2016 §4.3.2 diagrams were re-checked on renders (`raw/thl_figs/p-19.png`, `p-20.png`). Verification flags are in `TREATMENT_TARGETS.md`.
- FICAN Länsi-Suomi patient page (generic 4–6 weeks): https://fican.fi/lantinen-syopakeskus/syovan-hoito/tietoa-potilaalle/hoitoonpaasyajat/
- FICAN list of lung quality reports (only 2 editions): https://fican.fi/toiminta/arviointi-ja-seuranta/syopien-laaturekisterit/
- New outputs: `LUNG.md`, `DATA_GAPS.md` + `csv/data_gaps.csv`, `hero.json` (`scripts/build_hero_json.py`).

## facts.json (AI analyst grounding pack), added 2026-11-14
- `facts.json` is built by `scripts/build_facts.py` and validated by `scripts/check_facts.py`. It holds 81 atomic facts plus `usage_rules`.
- No new external sources were fetched. All values come from the CSVs, `hero.json` and raw texts already listed above:
  - strategy and roadmap PDFs
  - THL Ohjaus 21/2016
  - THL Työpaperi 3/2017
  - both lung reports
  - Sotkanet 3621/3627/6103
  - StatFin 13u5
- One newly used value from an existing file: lung-cancer deaths 2024 = 2 317 (StatFin 13u5, cause 11 C32–C34, includes larynx).
- `check_facts.py` re-reads every numeric value from `csv/*.csv`, `hero.json` or the raw report text (133 checks). It fails on any mismatch, duplicate id, missing source_url, or screening/stage labelled Goal 3.

## App data (data/app), added 2026-11-14
- No new external fetches. New derived CSVs:
  - `csv/lung_report2026_national_by_year.csv`: Taulukko 5 of the 2026 report (new patients, procedures, MDT, deaths by year 2019–2023, national). Produced by `scripts/build_lung_report_csv.py`.
  - `csv/lung_report2026_curative_agestd_national_chart_estimate.csv`: the national dashed reference lines in Kuva 15 (sex-specific: men ≈24.9, women ≈30.0) and Kuva 16 (≈27 in both panels), digitised ±1 pp. Produced by `scripts/digitise_lung2026_agestd_national.py`.
- Sotkanet 13 (2025) is used for the referral step only, flagged as not cancer-specific: https://sotkanet.fi/sotkanet/en/metadata/indicators/13
- `app/*.json` is built by `scripts/build_app_data.py` and checked by `scripts/check_app_data.py`. The schemas are in `app/README.md`.
