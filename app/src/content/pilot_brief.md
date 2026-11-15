# Tasan pilot brief: one page per county

> ## ⚠ DRAFT – not signed
> Draft for discussion. Nothing has been sent to, discussed with or agreed by either county or OYS.

*JN Care Strategist, 14 Nov 2026 (Helsinki time). Generated from `top3.json` by `scripts/gen_pilot_brief.py`, so do not hand-edit. Office-holders were checked on the counties' public websites on 14 Nov 2026.*

**Common rules.** T3 (the Tasan clock) starts first and measures each county's own baseline in days 1–30, including a registry-completeness check. T1 and T2 are the actions the clock triggers. Every target is a proposed peer benchmark or a Tasan design choice, not a promised effect. **Target-time caveat:** the 42-day reference is THL Ohjaus 21/2016 §4.1: marked outdated, with no lung-specific limit. New cancer-specific targets are due 2026–2028 (roadmap 3.1.2, p.57). Day-28 and 80% are Tasan design choices.

---

## Kymenlaakso: Kymenlaakson hyvinvointialue (Kymenhva)

> ## ⚠ DRAFT – not signed
> Draft for discussion. Nothing has been sent to, discussed with or agreed by either county or OYS.

**Scope (90 days):** T3 Tasan clock: county lung-cancer waiting-time tracker with a day-28 alert and a named nurse navigator who acts on it + T1 Close the missing step in Kymenlaakso's lung pathway: week-1 pathway map, then 3-day CT, reflex biomarkers and pre-agreed HUS surgery slots where missing. Lung cancer (C33–C34) patients resident in the county.

**Why this county:** 591 lung cancers diagnosed in 2019–2023, about 118 a year (Keuhkosyöpä Suomessa 2019–2023, Taulukko 11). The surgery decision and the operation are made at HUS Meilahti (kymenhva.fi), so hand-offs to another organisation are part of every surgical pathway. Crude curative-record share 19.3% (16.3–22.7) vs 27.0% nationally; age-standardised (chart-digitised) men ≈18.0%, women ≈22.7%. No county-level time data exist, so T3 measures them.
**This already exists?** Kymenhva already runs a lung outpatient work-up and a multidisciplinary lung meeting (kymenhva.fi). T1 does not invent a pathway: it closes the missing step that the week-1 map finds.

**Owners (this county only):**
- **Signer:** Johtajaylilääkäri / Chief Medical Officer, Kymenlaakso wellbeing services county (Kymenhva) (role holder verified on kymenhva.fi, 14 Nov 2026)
- **Operational sponsor (T1):** Hallintoylilääkäri, erikoissairaanhoito / Administrative Chief Physician, specialised care, Kymenhva (role holder verified on kymenhva.fi, 14 Nov 2026)
- **Owner of delayed patients (T3):** nurse navigator, line-managed by the Johtajaylihoitaja / Chief Nursing Officer, Kymenhva (role holder verified on kymenhva.fi, 14 Nov 2026)
- **Clinical lead (T1):** ylilääkäri, pulmonology unit, Kymenlaakson keskussairaala, Kotka (name not verified)
- **Data owner (T3):** Kymenhva analytics unit (name not verified)
- **Partners:** HUS Meilahti thoracic surgery (one named slot counterpart, to be agreed); the existing Kymenhva multidisciplinary lung meeting; the HUS-operated laboratory at Kymenlaakso central hospital (lung pathology role to confirm)

**90-day plan:**
- T3 · Days 1–30: data spec on the THL 21/2016 time points; registry-completeness check (drug therapy, curative RT, MDT, no-record cases vs EHR); 12-month retrospective baseline per county; navigator named
- T3 · Days 31–60: weekly feed; day-28 alert switched on; navigator takes alerts
- T3 · Days 61–90: first monthly board report (incl. non-pathway waits); day-90 stop/go
- T1 · Days 1–15: name the clinical lead and the HUS counterpart; week-1 pathway map from T3's dates
- T1 · Days 16–45: agree the fix for the missing step(s) (CT rule, reflex SOP, HUS slot agreement)
- T1 · Days 46–60: brief GPs/radiology; switch on
- T1 · Days 61–90: first 20–30 patients; weekly review with T3; day-90 stop/go

**Cost range (sourced staff cost only):**
- **Base (T3): €20,339–€23,988** for 90 days: 1.0 FTE nurse navigator + 0.5 FTE analyst.
- *Conditional:* €26,202–€31,465 only if the week-1 map shows that T1 needs its own 0.5 FTE pathway coordinator (€5,863–€7,477). Otherwise the T3 navigator covers it.
- No euro figure (unsourced): T1 set-up physician hours (est. 40–80 h), extra CT/EBUS lists, reflex biomarker panel price, dashboard integration.
- Pay sources: KT Kunta- ja hyvinvointialuetyönantajat, 'Hyvinvointialan palkkatilastot' Oct 2025 (https://www.kt.fi/tilastot-ja-julkaisut/hyvinvointialan-palkat): sairaanhoitaja task-based €3,174 / total €4,048 per month; analyytikko €4,663 / €4,891. Employer contributions 23.14% (KT 'Henkilöstökulut', 2026: https://www.kt.fi/tilastot-ja-julkaisut/henkilostokulut). Range = task-based pay (low) to total earnings incl. all supplements (high), × 12 × 1.2314. Oct 2025 pay with 2026 contribution rates; later pay rises are not included.

**KPIs:**

| | KPI | Baseline | Target |
|---|---|---|---|
| T3 | % of lung-cancer patients starting first treatment ≤42 days from referral arrival | not public. Each county's own baseline is measured in days 1–30 from 12 months of EHR dates | ≥80% within 12 months (Tasan design choice, by analogy with the NHS FDS 80% on a different clock; not an official target) |
| T3 | Day-28 alerts actioned within 2 working days | n/a (new) | ≥90% (Tasan design) |
| T3 | Named-coordinator model in use (roadmap 1.2.3 indicator) | not in use for lung pathways in the pilot counties (to confirm in week 1) | in use in both pilot counties |
| T1 | Median referral arrival → treatment decision (days), Kymenlaakso | not public; measured by T3 in days 1–30 | ≥7 days shorter than the county's own baseline by day 90 |
| T1 | % of Kymenlaakso lung-cancer patients treated ≤42 days from referral arrival | not public; measured by T3 in days 1–30 | ≥80% (Tasan design choice) |
| T1 | Crude curative-record share within 12 months (context, registry lag) | 19.3% (CI 16.3–22.7; 114/591), dx 2019–2023 | proposed peer benchmark: national 27.0%. Not a promised effect |

**Design column (not KPIs, not costed):**
- Longer-term design aim (not a KPI, not a promised effect): referral→decision ≤14 days, based on the one-stop clinic precedent 20→4 d (Chung 2025)

**Day-90 stop/go:**
- **T3 GO** if all: ≥85% of lung-cancer pathways have all 4 THL 21/2016 time points (referral arrival, first visit, queue date, first treatment); The county's own 12-month baseline (% ≤42 days from referral arrival; median per step) is presented to the county board; ≥90% of day-28 alerts are actioned by the navigator within 2 working days; The navigator contacts ≥90% of new suspected-lung-cancer patients within 3 working days of referral arrival.
- **T3 STOP/redesign** if any: Time-point completeness <70% after one fix cycle: pause the dashboard and fix recording first. Otherwise: Extend by 90 days with one named fix.
- **T1 GO** if all: The missing step(s) found on the week-1 pathway map are in place (e.g. CT ≤3 working days, reflex panel SOP, pre-agreed HUS slots); ≥20 suspected-lung-cancer patients through the redesigned pathway; Median referral → treatment decision ≥7 days shorter than the county's own baseline (from T3, days 1–30); Waits for non-pathway CT not more than 10% longer than in the same months last year (crowding-out check).
- **T1 STOP/redesign** if any: <10 patients through the pathway; Median referral→decision improved by <3 days; Non-pathway CT waits up >20%. Otherwise: Extend by 90 days with one named fix.

*Thresholds are Tasan design choices. 42 days follows THL 21/2016 (outdated, no lung-specific limit, cancer-specific targets due 2026–28).*

**DRAFT – not signed. Approval for a 90-day pilot:**

Signature: ______________________  Role: Johtajaylilääkäri / Chief Medical Officer, Kymenlaakso wellbeing services county (Kymenhva)  Date: ____ / ____ / 2026

---

## Lapland: Lapin hyvinvointialue

> ## ⚠ DRAFT – not signed
> Draft for discussion. Nothing has been sent to, discussed with or agreed by either county or OYS.

**Scope (90 days):** T3 Tasan clock: county lung-cancer waiting-time tracker with a day-28 alert and a named nurse navigator who acts on it + T2 Every new Lapland lung cancer reviewed by the existing OYS lung-cancer MDT (by video), plus shared access to curative radiotherapy at OYS (RT referral, travel and accommodation, SBRT/chemoradiation slots). Lung cancer (C33–C34) patients resident in the county.

**Why this county:** Age-standardised curative share (chart-digitised, R2026 Kuva 16): men ≈16.2% (12.7–20.4) vs Vantaa-Kerava ≈29.8% (24.2–36.1); women ≈23.1% (17.9–29.0) vs ≈39.7% (33.1–47.0). Men's surgery share is equal (9.1% vs 9.0%, R2024 Taulukko 3.7), so the gap is likely in curative radiotherapy, which is given at OYS (our inference). Not adjusted for stage or fitness.
**This already exists?** Yes. OYS states that the university hospital is responsible for lung-cancer MDTs, surgery and radiotherapy (oys.fi), and Lapland's radiotherapy is given at OYS (lapha.fi). T2 does not create a board: it closes coverage of the existing one to 100% of new Lapland cases, and turns a curative-RT recommendation into a booked slot with travel and accommodation arranged. The registry's 3.0% 'MDT recorded' figure for Lapland is NOT used as proof of a gap: Helsinki shows 0.1%, so it is a recording artefact.

**Owners (this county only):**
- **Signer:** Johtajaylilääkäri / Chief Medical Officer, Lapland wellbeing services county (Lapin hyvinvointialue) (role holder verified on lapha.fi, 14 Nov 2026)
- **Operational sponsor (T2):** Somaattisen erikoissairaanhoidon johtaja / Director of Somatic Specialised Care, Lapin hyvinvointialue (role holder verified on lapha.fi, 14 Nov 2026)
- **Owner of delayed patients (T3):** nurse navigator, line-managed by the vs. hoitotyön johtaja / Acting Director of Nursing, Lapin hyvinvointialue (role holder verified on lapha.fi, 14 Nov 2026)
- **Clinical lead (T2):** keuhkosairauksien ylilääkäri, Lapin keskussairaala, Rovaniemi (name not verified)
- **Data owner (T3):** Lapland analytics unit (name not verified)
- **OYS partners (week-1 gate):** the OYS lung-cancer MDT lead and OYS radiotherapy lead are NOT VERIFIED from public sources (oys.fi, pohde.fi, oulu.fi, Filha, checked 14 Nov 2026). Entry points: service-area director for cancer care, OYS (palvelualuejohtaja, OYS Sisätaudit, syöpähoito ja infektiontorjunta) (pohde.fi); physician-in-chief, respiratory medicine, OYS (not confirmed as MDT lead) (oulu.fi). Co-signer for OYS: Johtajaylilääkäri / Chief Medical Officer, North Ostrobothnia wellbeing services county (Pohde) (pohde.fi)

**Week-1 gate (T2):** By day 7, the OYS lung-cancer MDT lead and the OYS radiotherapy lead are identified and confirm in writing that they will take part (MDT listing rule + video slot). If not confirmed by day 14: STOP the T2 arm and continue T3 only in Lapland.

**90-day plan:**
- T3 · Days 1–30: data spec on the THL 21/2016 time points; registry-completeness check (drug therapy, curative RT, MDT, no-record cases vs EHR); 12-month retrospective baseline per county; navigator named
- T3 · Days 31–60: weekly feed; day-28 alert switched on; navigator takes alerts
- T3 · Days 61–90: first monthly board report (incl. non-pathway waits); day-90 stop/go
- T2 · Days 1–7 (GATE): identify and confirm in writing the OYS lung-cancer MDT lead and the OYS radiotherapy lead. Entry points: service-area director for cancer care, OYS (palvelualuejohtaja, OYS Sisätaudit, syöpähoito ja infektiontorjunta) (pohde.fi); physician-in-chief, respiratory medicine, OYS (oulu.fi). Neither is confirmed as MDT or RT lead
- T2 · Days 1–20: audit of 2025 Lapland cases at the OYS MDT and of curative-RT referrals/starts; agree the 'all new cases' listing rule, video slot and a weekly Lapland SBRT/chemoradiation quota with the OYS MDT and radiotherapy leads
- T2 · Days 21–45: coordinator named; case list fed from pathology; ECOG/G8 fields added
- T2 · Days 46–90: weekly listing; log coverage, intent and slots; day-90 stop/go

**Cost range (sourced staff cost only):**
- **Base (T3 + T2): €23,857–€28,474** for 90 days: T3 €20,339–€23,988 (1.0 FTE navigator + 0.5 FTE analyst) + T2 €3,518–€4,486 (0.3 FTE MDT list coordinator).
- No euro figure (unsourced): MDT physician hours (est. 0.75–1.5 h per case × ~36 cases), baseline audit (16–32 h), video/PACS, dashboard integration.
- Not costed, design only: the curative-RT access arm (slot quota, travel, accommodation). It is sized with the OYS RT lead after the week-1 gate.
- Pay sources: KT Kunta- ja hyvinvointialuetyönantajat, 'Hyvinvointialan palkkatilastot' Oct 2025 (https://www.kt.fi/tilastot-ja-julkaisut/hyvinvointialan-palkat): sairaanhoitaja task-based €3,174 / total €4,048 per month; analyytikko €4,663 / €4,891. Employer contributions 23.14% (KT 'Henkilöstökulut', 2026: https://www.kt.fi/tilastot-ja-julkaisut/henkilostokulut). Range = task-based pay (low) to total earnings incl. all supplements (high), × 12 × 1.2314. Oct 2025 pay with 2026 contribution rates; later pay rises are not included.

**KPIs:**

| | KPI | Baseline | Target |
|---|---|---|---|
| T3 | % of lung-cancer patients starting first treatment ≤42 days from referral arrival | not public. Each county's own baseline is measured in days 1–30 from 12 months of EHR dates | ≥80% within 12 months (Tasan design choice, by analogy with the NHS FDS 80% on a different clock; not an official target) |
| T3 | Day-28 alerts actioned within 2 working days | n/a (new) | ≥90% (Tasan design) |
| T3 | Named-coordinator model in use (roadmap 1.2.3 indicator) | not in use for lung pathways in the pilot counties (to confirm in week 1) | in use in both pilot counties |
| T2 | % of new Lapland lung cancers listed at the OYS MDT before the treatment-intent decision | unknown; audited in week 1 | ≥90% by day 90 (Tasan design; the Victorian registry rose from 59% to 81%) |
| T2 | % of Lapland lung-cancer patients treated ≤42 days from referral arrival | measured by T3 in days 1–30 | ≥80% (Tasan design choice) |
| T2 | Age-standardised curative-treatment share within 12 months, by sex (registry lag) | Men ≈16.2% (95% CI 12.7–20.4); women ≈23.1% (17.9–29.0); dx 2019–2023; chart-digitised ±1 pp | proposed peer benchmark: Pohjois-Pohjanmaa (OYS's home county, same collaborative area) men ≈23.2% (19.7–26.7), women ≈25.3% (21.0–30.7). Not a promised effect |

**Design column (not KPIs, not costed):**
- Curative-RT access arm (design, UNPRICED, not a KPI or cost line yet): direct MDT→OYS radiotherapy referral for curative SBRT/chemoradiation; a reserved weekly Lapland slot quota; Kela travel and patient-hotel accommodation booked by the T3 navigator. To be sized with the OYS radiotherapy lead once identified (week-1 gate). A candidate measure for later: % of curative-RT recommendations starting ≤14 days after the MDT

**Day-90 stop/go:**
- **T3 GO** if all: ≥85% of lung-cancer pathways have all 4 THL 21/2016 time points (referral arrival, first visit, queue date, first treatment); The county's own 12-month baseline (% ≤42 days from referral arrival; median per step) is presented to the county board; ≥90% of day-28 alerts are actioned by the navigator within 2 working days; The navigator contacts ≥90% of new suspected-lung-cancer patients within 3 working days of referral arrival.
- **T3 STOP/redesign** if any: Time-point completeness <70% after one fix cycle: pause the dashboard and fix recording first. Otherwise: Extend by 90 days with one named fix.
- **T2 GO** if all: Week-1 gate passed (OYS MDT and RT leads confirmed); ≥90% of new Lapland lung cancers listed at the existing OYS MDT before the treatment-intent decision (or ≥20 pp above the week-1 audited baseline); Median histology → MDT ≤7 days, and listing does not add >7 days to the treatment decision; Performance/frailty fields (ECOG, G8/CFS) completed in ≥80% of listed cases; A sized proposal for the curative-RT access arm (slot quota, travel, accommodation) is agreed with the OYS RT lead (design, unpriced).
- **T2 STOP/redesign** if any: OYS leads not confirmed by day 14; Coverage <70% at day 90; Listing adds >14 days median to the decision. Otherwise: Extend by 90 days with one named fix.

*Thresholds are Tasan design choices. 42 days follows THL 21/2016 (outdated, no lung-specific limit, cancer-specific targets due 2026–28).*

**DRAFT – not signed. Approval for a 90-day pilot:**

Signature: ______________________  Role: Johtajaylilääkäri / Chief Medical Officer, Lapland wellbeing services county (Lapin hyvinvointialue)  Date: ____ / ____ / 2026

Co-signature, OYS side: ______________________  Johtajaylilääkäri / Chief Medical Officer, North Ostrobothnia wellbeing services county (Pohde)  Date: ____ / ____ / 2026
