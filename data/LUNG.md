# LUNG — regional lung-cancer pathway data (Goal 3 hero: diagnosis → treatment)

Access date 2026-11-14. Public aggregate data only. Every number below is in a CSV under `csv/lung_*.csv` with source URL, table/figure and page.

## Sources (the only two editions that exist)
| Edition | Cohort | Geography | URL |
|---|---|---|---|
| **R2024** *Keuhkosyöpä Suomessa – Katsaus keuhkosyövän hoidon laadusta* (Syöpärekisteri/FICAN/THL, 12/2024), PDF 43 pp | lung cancers C33–C34 diagnosed **1.1.2018–30.6.2022**, N = 13 324, excl. Åland; 6-month follow-up for treatment | YTA (5 collaborative areas) and wellbeing county (HVA) of **residence** | https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf |
| **R2026** *Keuhkosyöpä Suomessa 2019–2023* (HTML factsheet, publ. 23.4.2026) | diagnosed **2019–2023**, N = 14 873; 12-month follow-up | YTA and HVA of residence | https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html |

FICAN lists only these two lung reports (https://fican.fi/toiminta/arviointi-ja-seuranta/syopien-laaturekisterit/).

The registry's interactive app https://tilastot.syoparekisteri.fi/syovat/ is an R Shiny app. It answers HTTP 200 and has CSV-download buttons, but these only work over a live websocket session. We did not scrape it. As far as we know it covers incidence, mortality and survival by region, not treatment or time intervals. We did not confirm that inside the app.

## How hand-transcribed numbers were verified (R2024)
The R2024 tables are vector graphics with **no extractable text**: `pdftotext` returns only captions, and `pdfimages` shows the tables are not images either. So every value was checked three ways:
1. **Manual transcription** from 200-dpi renders (`raw/lung2024_pages/p-NN.png`, `pdftoppm -r 200`). Crops were viewed at full resolution.
2. **Independent OCR** (RapidOCR, `scripts/ocr_pages.py` → `raw/lung2024_pages/p-NN.ocr.txt`). The automatic cross-check in `scripts/build_lung2024_tables.py` found **1 174 of 1 199** transcribed printed numbers verbatim in the OCR text.
   - The other 25 OCR misses are listed in `raw/lung2024_pages/ocr_crosscheck_misses.tsv`. Every one was re-read on the render.
   - All are OCR failures on old-style numerals (e.g. "7" read as "Z", "37,7" as "377", single-digit counts dropped). None is a transcription disagreement.
3. **Internal consistency:**
   - Taulukko 3.3: count/total = printed % for 25/25 cells.
   - Taulukko 4.5: each month's six columns sum to 99.9–100.2.
   - Taulukko 4.6 equals the month-6 values of 4.5 (all 15 match).
   - Taulukko 4.1: the OCR text matched all 45 values. The report prose (printed p. 27) independently states the North 13.5 (0–44) and South 46.0 (33–63) surgery values.

R2026 tables are HTML, parsed with `pandas.read_html`, so there is no transcription. R2026 figures were **digitised by pixel measurement**. Those values are flagged *CHART-DIGITISED ESTIMATE* (±1 pp) and are never presented as published numbers.

## Files
| CSV | Content | Geography / years | n / CI |
|---|---|---|---|
| `lung_report2024_days_dx_to_first_treatment_by_yta.csv` | **Taul 4.1**: median (Q1–Q3) days from diagnosis to first surgery / RT / drug therapy | YTA, dx 2018–6/2022 | IQR only; n per cell not printed |
| `lung_report2024_first_event_cumulative_by_yta.csv` | **Taul 4.5** (+4.6): cumulative % first event (none yet / surgery / non-pall. RT / drug / palliative / death), months 0–6 | YTA | no n per cell |
| `lung_derived_first_active_treatment_by_month_yta.csv` | **DERIVED**: share of *all* patients whose first active treatment started within m months (= surgery + RT + drug columns of 4.5) | YTA | approx. Wilson CI, denominators from Taul 3.3 |
| `lung_report2024_treatment_6m_by_yta.csv` | **Taul 3.3/3.4**: any surgery / RT / drug / palliative / death within 6 mo | YTA | n/N printed; Wilson CI computed |
| `lung_report2024_treatment_agestd_by_yta_sex.csv` | **Taul 3.6**: age-standardised % surgery / drug / RT, by sex | YTA | n + 95 % CI printed |
| `lung_report2024_treatment_agestd_by_wsc_sex.csv` | **Taul 3.7**: same by wellbeing county | 21 HVA + Helsinki | n + 95 % CI printed |
| `lung_report2024_survival_1y_by_yta.csv` | **Taul 5.1**: age-standardised 1-yr relative survival by sex | YTA, follow-up 2020–2022 | 95 % CI printed |
| `lung_report2024_survival_1y_by_treatment_yta.csv` | **Taul 5.3**: 1-yr survival after first treatment, by sex × treatment; RR vs South, p | YTA | n + 95 % CI printed |
| `lung_report2026_treatment_by_wsc.csv` | **Taul 11**: curative / life-prolonging / symptomatic / no record / MDT within 12 mo | HVA, dx 2019–2023 | n/N printed; Wilson CI computed |
| `lung_report2026_treatment_by_yta.csv` | **Taul 10**: same by YTA | YTA | n/N; Wilson computed |
| `lung_report2026_curative_agestd_by_sex_chart_estimate.csv` | **Kuva 15/16 digitised**: AGE-STANDARDISED curative share with 95 % CI, by sex | HVA (Kainuu suppressed) and YTA | CI as drawn; ±1 pp |
| `lung_report2026_stage_info_coverage_national.csv` | **Taul 4**: stage-information source; missing 47.7 % (7 097/14 873) | national | n printed |
| `lung_report2026_stage_missing_by_wsc_chart_estimate.csv` | **Kuva 13 digitised**: % with no stage info | HVA | no n; ±1 pp |

## Key regional numbers (each with source)

### Diagnosis → treatment, time (Goal 3 indicator 3 proxy)
- **Median days from diagnosis to surgery** (R2024 Taul 4.1, PDF p. 28, patients whose *first* treatment within 6 mo was surgery):
  - Pohjois **13.5 (0–44)**, Itä 27.0 (0–43.5), Sisä 29.0 (0–51), Länsi 42.0 (28–55), Etelä **46.0 (33–63)**.
  - The national median is 37 d (0–56) (report text, printed p. 26).
  - Caveats:
    - **Q1 = 0** in three areas: ≥ 25 % of those patients have surgery on the registry diagnosis date. Our guess (the report does not say) is that the diagnosis is dated from the resection specimen. That flatters areas with Q1 = 0.
    - Only about 11 % of patients have surgery first. Pohjois sends the *fewest* to surgery (9.5 % by month 6, Taul 4.5/4.6).
- **Radiotherapy** medians: Itä 25.0 to Länsi 45.0 (Q3 74.5). **Drug therapy** medians: Länsi 34.5 to Sisä 43.0. These do not repeat the North–South surgery contrast; for drug therapy the North is slower (42.0 vs 36.0).
- **Share of ALL patients whose first active treatment started within 2 months of diagnosis** (DERIVED from Taul 4.5):
  - Sisä **38.7 %** (≈36.6–40.8), Itä 38.0 %, Etelä 32.9 %, Pohjois 30.5 %, Länsi **27.7 %** (≈25.9–29.6).
  - By 6 months: Sisä 52.1 % vs Länsi 38.0 %.
  - The same table shows **death before any treatment record within 6 months**: Länsi 32.3 %, Pohjois 29.4 %, Etelä 28.6 %, Sisä 24.9 %, Itä 23.6 %.
  - Recording caveat below: Länsi includes Varsinais-Suomi, whose drug-therapy record is nearly absent.

### Treatment received (curative share = proxy for Goal 3 indicator 1)
- **Crude curative share within 12 mo, 2019–2023** (R2026 Taul 11; Wilson CI computed by us):
  - Lapland **18.5 % (15.8–21.5; 131/710)**, South Karelia 18.9 % (15.1–23.3; 67/355), Kymenlaakso 19.3 % (16.3–22.7; 114/591)
  - vs Vantaa-Kerava **35.6 % (31.9–39.6; 212/595)**, Central Uusimaa 33.7 % (29.6–38.0; 162/481), Helsinki 33.0 % (30.7–35.5; 491/1486)
  - National 27.0 % (4 009/14 873).
  - YTA (Taul 10): North 21.5 % (19.8–23.3) vs South 30.1 % (28.9–31.3).
- **Age-standardised curative share** (R2026 Kuva 16, CHART-DIGITISED, ±1 pp):

  | | Men | Women |
  |---|---|---|
  | Lapland | ≈16.2 % (12.7–20.4) | ≈23.1 % (17.9–29.0) |
  | Vantaa-Kerava | ≈29.8 % (24.2–36.1) | ≈39.7 % (33.1–47.0) |

  - The CIs do not overlap in either sex, so the gap is **not explained by age structure**.
  - YTA (Kuva 15): men North ≈20.1 % vs South ≈27.8 %; women North ≈24.1 % vs South ≈32.7 %.
- **Age-standardised surgery share, 2018–6/2022** (R2024 Taul 3.7, printed CIs):
  - Men: Lapland 9.1 % (6.0–13.7) vs Vantaa-Kerava 9.0 % (5.5–14.1).
  - Women: Lapland 10.4 % (6.3–16.6) vs Vantaa-Kerava 20.5 % (14.4–29.7).
  - So for men the curative gap is **not in surgery**. It must come from curative radiotherapy, which R2024 does not separate from palliative RT in Taul 3.7. That is our inference.

### Survival (Goal 3 indicator 1 context: 1-year only; no public regional 5-year lung survival)
- **Age-standardised 1-year relative survival** (R2024 Taul 5.1, follow-up 2020–2022, printed 95 % CI): Sisä **46.8 % (44.1–49.6)**, Etelä 42.8 % (41.1–44.6), Itä 42.7 % (40.0–45.5), Länsi 41.9 % (39.4–44.5), Pohjois **40.1 % (37.5–43.0)**; national 42.9 % (41.8–43.9).
  - Women 48.8 % vs men 38.9 % nationally.
  - The report says Sisä men are significantly better than the national level.
- **After palliative first treatment** (Taul 5.3): 1-yr survival in Etelä is the lowest (men 11.4 %, women 10.0 %; p < 0.001 for area differences) vs Itä (24.4 %, 26.3 %). This most likely reflects *who* gets labelled palliative (coding practice), not care quality.
- **After surgery**, there are no significant area differences (men p = 0.233, women p = 0.405).

### Data quality by region (this is itself a finding)
- **Stage missing:** national 47.7 % (7 097/14 873; R2026 Taul 4). By county (Kuva 13, digitised ±1 pp) it ranges from ≈22 % (Kanta-Häme) to ≈68 % (Satakunta). Strategy sub-goal 3.2 targets 90 % coverage (S p. 36).
- **No treatment record within 12 mo:** 16.4 % (Kymenlaakso, 97/591) to 43.1 % (Varsinais-Suomi, 619/1437) (Taul 11). 79 % of such patients nationally died within a year (R2026 text), so this is not only paperwork.
- **Drug-therapy recording gaps:** age-standardised drug-therapy share in R2024 Taul 3.7 is
  - Varsinais-Suomi **0.8 % men / 1.0 % women**
  - Vantaa-Kerava 3.7 % / 3.8 %
  - Keski-Uusimaa 3.5 % / 7.3 %
  - compared with 25 % nationally. Clinically implausible; most likely the treatment is given but not coded in HILMO (our inference). **So county drug-therapy, "no record" and "first-treatment" comparisons are contaminated by recording.**
- **MDT recorded:** 32.6 % in Sisä vs 0.2–2.3 % elsewhere (Taul 10). This is a coding practice, not care.

## Age-adjusted vs crude: what exists (asked by judge review M6)
- **Age-standardised by county:** published **only as figures** in R2026 (Kuva 15 YTA, Kuva 16 HVA, by sex). We digitised them (above). In R2024 they are published as **tables** (Taul 3.6 YTA, 3.7 HVA: surgery / drug / RT by sex, with CIs). R2024 has no "curative" group.
- **Age-stratified curative shares by county/area: no public source found.** R2026 gives age breakdowns only nationally. Neither report crosses age group × region for treatment.
- **Stage-, comorbidity-, performance-status-adjusted shares: do not exist publicly.** Stage is missing for 47.7 %, and comorbidity/ECOG are not in the registry extracts used.

### Strongest honest caveat (use verbatim)
> "Curative-treatment shares are crude registry proportions of all lung cancers diagnosed in 2019–2023 among residents of each county with a surgery or curative-radiotherapy record within 12 months. They are not adjusted for stage (missing for 48 % nationally and for up to about two-thirds of patients in some counties), comorbidity or performance status. They depend on how each region records treatment in national registers. The report's age-standardised version (chart only) shows the same Lapland vs Vantaa-Kerava gap for both men and women, so age structure alone does not explain it. Stage mix, fitness for treatment and recording practice could still explain part of it."

## Limitations
- Cohorts differ: R2024 (2018–6/2022, 6-mo follow-up), R2026 (2019–2023, 12-mo follow-up). Do not combine them into one pathway.
- Geography is the patient's **home** YTA/HVA (municipality at diagnosis), not the treating hospital. The 2023 wellbeing-county reform means pre-2023 years are mapped retrospectively.
- Time intervals start at the **registry diagnosis date**, not referral. **No public referral → diagnosis interval exists for lung cancer** at any regional level.
- Small counties (Kainuu, Keski-Pohjanmaa, Itä-Uusimaa, n < 30 per sex for some cells) have wide CIs. Kainuu curative is suppressed in Kuva 16.
- Registry lag: the newest diagnosis year is 2023.
