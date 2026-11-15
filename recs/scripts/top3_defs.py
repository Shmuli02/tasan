# Tasan top-3 (+ optional Goal 2) definitions. Imported by build_recs.py.
# Order (coordinator decision, 14 Nov 19:39): T3 clock = #1; T1 and T2 are what the clock triggers and measures.
from pilot_defs import pilot_fields
LUNG24 = ("Syöpärekisteri/FICAN: Keuhkosyöpä Suomessa (12/2024), Taulukko 4.1 (printed p.27) and text p.26–28",
          "https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf",
          "data/csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv")
LUNG26 = ("Syöpärekisteri/THL/FICAN: Keuhkosyöpä Suomessa 2019–2023 (publ. 23.4.2026), Taulukko 11",
          "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
          "data/csv/lung_report2026_treatment_by_wsc.csv")
LUNG24AS = ("Keuhkosyöpä Suomessa (12/2024), Taulukko 3.7 (age-standardised % treated within 6 months by wellbeing county and sex, printed CIs), printed p.24–25",
            "https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf",
            "data/csv/lung_report2024_treatment_agestd_by_wsc_sex.csv")
LUNG26AS = ("Keuhkosyöpä Suomessa 2019–2023 (23.4.2026), Kuva 16, AGE-STANDARDISED curative share by county and sex (CHART-DIGITISED by the data team, ±1 pp; not a published number)",
            "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
            "data/csv/lung_report2026_curative_agestd_by_sex_chart_estimate.csv")
FRAGILE = ("Context only, not a KPI: median diagnosis→surgery 13.5 d (Pohjois-Suomi) vs 46.0 d (Etelä-Suomi), Taulukko 4.1. FRAGILE: in Pohjois-, Itä- and Sisä-Suomi "
           "the lower quartile is 0 days (≥25% have surgery on the registry diagnosis date, probably because diagnosis is dated from the resection specimen; our guess). "
           "Only ~1 in 10 patients have surgery first; the clock starts at diagnosis, not referral; 1/2018–6/2022; 5 collaborative areas.")
S6103 = ("THL Sotkanet 6103 (Finnish Cancer Registry screening statistics), 2024",
         "https://sotkanet.fi/sotkanet/en/metadata/indicators/6103",
         "data/csv/sotkanet_6103_screening_colorectal_attendance.csv")
KYMLUNG = ("Kymenhva: Keuhkosyöpä ja keuhkopussin mesoteliooma (patient page)",
           "https://kymenhva.fi/palvelut-ja-ajanvaraus/erikoissairaanhoito/poliklinikat-ja-erikoisalat/keuhkosairaudet/keuhkosyopa-ja-mesoteliooma/", "web page, fetched 14 Nov 2026")
OYSLUNG = ("OYS: Keuhkosyöpäpotilaan hoitopolku", "https://oys.fi/palvelumme/syopataudit/keuhkosyopapotilaan-hoitopolku/", "web page, fetched 14 Nov 2026")

def d(fact, src, verified="re-checked by JN Care Strategist against the csv/raw text, 14 Nov 2026"):
    return {"fact": fact, "source": src[0], "url": src[1], "csv": src[2], "verified": verified}

OUTDATED = ("CAVEAT: the 42-day / 6-week figure is the generic limit in THL Ohjaus 21/2016 §4.1 (referral arrival → first treatment), "
            "the reference the strategy names for Goal 3 (S p.5). That PDF is watermarked 'Vanhentunut' (outdated) and has no lung-specific limit. "
            "Cancer-specific access times are due 2026–2028 (roadmap 3.1.2, R p.57). Day-28 alert and the 80% target are Tasan design choices, not official targets.")
TIME_CAVEAT = ("Table 4.1 medians cover only patients whose FIRST treatment within 6 months was surgery (~1 in 10: N 1,627 nationally), "
               "diagnosed 1/2018–6/2022, by collaborative area (YTA) of residence, clock from diagnosis (not referral). National median 37 d (IQR 0–56). "
               "Radiotherapy and drug-therapy medians do not repeat the pattern.")
SHARE_CAVEAT = ("Crude share with a curative-treatment RECORD within 12 months (2019–2023). It is not 5-year survival and not age- or stage-adjusted "
                "(stage missing for 47.7%). Wilson 95% CIs were computed by the data team, not printed in the report. Shares are by home county. "
                "Treatment groups are not mutually exclusive. Where used, the age-standardised version is the data team's digitisation of the 2026 report's Kuva 16 (±1 pp).")

def top_items(ev, NAV_COST=None):
    P = pilot_fields()
    T = []
    T.append(dict(id="T3", priority_rank=1, top3=True, pilot_county="Kymenlaakso and Lapland (one per collaborative area); scalable to all 22 areas",
     title="Tasan clock: county lung-cancer waiting-time tracker with a day-28 alert and a named nurse navigator who acts on it",
     bottleneck="diagnosis_to_treatment", pathway_step="Referral arrival → first visit → treatment decision → first treatment (THL 21/2016 time points)",
     problem="Goal 3's own wording, 'Potilaat pääsevät hoitoon tavoiteaikojen puitteissa' (S p.5), cannot be checked for any county: THL 2017 says national follow-up of cancer patients' access to care 'has been missing', and we found no later public regional series. The only public lung timing is a diagnosis clock for surgical patients in 5 collaborative areas, 2018–mid-2022.",
     action="Week 1: the county extracts referral arrival, first visit, queue date and first treatment for every lung cancer of the last 12 months. That gives the county's own baseline in days 1–30. From week 5 the dates feed the Tasan dashboard weekly. If there is no treatment decision 28 days after referral arrival, an alert goes to the named nurse navigator. The navigator removes the blocker (test booking, result chasing, MDT slot, HUS/OYS slot) and is the single contact for patient and GP. A monthly board view shows % within 42 days, the median per step, and waits for non-pathway patients (to detect crowding out). The clock tells each county whether its problem is speed (→ T1) or who reaches curative treatment (→ T2). DATA-QUALITY TASK (days 1–30): before any baseline is published, check registry completeness against the EHR. In the 2024 report the age-standardised drug-therapy share is implausibly low in Varsinais-Suomi (0.8% men / 1.0% women), Vantaa-Kerava (3.7% / 3.8%) and Keski-Uusimaa (3.5% / 7.3%) vs ~25% nationally. Lapland is also low (10.0% / 15.3%; CIs below the national level). The likely cause is HILMO coding gaps (data team's inference). So the pilot checks drug, curative-RT and MDT codes, and the no-record cases, against the hospital's own records.",
     already_exists="Hospitals hold the dates, and some have coordinators: roadmap 1.2.3 is still at 'survey existing models' (R p.32). What does not exist is a public, comparable, county-level clock for the Goal 3 target. Tasan is that missing public clock, not the first navigator in Finland.",
     owners=["Johtajaylilääkäri of each pilot county (signer)", "Nurse navigator, 1 FTE per county (owner of delayed patients)", "County analytics unit (data)", "ICT (EHR/Hilmo extraction)", "County board (monthly review)"],
     effort="Low–Medium",
     kpis=[{"name":"% of lung-cancer patients starting first treatment ≤42 days from referral arrival","type":"goal3","ref":"G3-3","baseline":"not public. Each county's own baseline is measured in days 1–30 from 12 months of EHR dates","target":"≥80% within 12 months (Tasan design choice, by analogy with the NHS FDS 80% on a different clock; not an official target)","note":OUTDATED},
           {"name":"Day-28 alerts actioned within 2 working days","type":"process","ref":"county-internal","baseline":"n/a (new)","target":"≥90% (Tasan design)"},
           {"name":"Named-coordinator model in use (roadmap 1.2.3 indicator)","type":"roadmap","ref":"ROAD p.32","baseline":"not in use for lung pathways in the pilot counties (to confirm in week 1)","target":"in use in both pilot counties"}],
     kpi_framing="Measures the Goal 3 wording directly. All thresholds are Tasan design choices. The 42 days comes from an outdated THL document with no lung limit.",
     expected_effect="Makes G3-3 measurable per county. Monitoring alone does not shorten waits: the effect comes from the navigator acting and from T1/T2. Navigation evidence is mixed (benefit at 365 days, none at 60/180 days).",
     evidence=[ev("THL 21/2016 time points and the max 6 weeks referral→first treatment (document marked outdated)", "THL21", "PDF p.5; printed p.13"),
               ev("Norway: decision→treatment was the main source of delay; CPPs introduced a pathway coordinator role", "NILSSEN22"),
               ev("Patient navigation: aOR 2.12 for timely diagnostic resolution at 365 days (no effect at 60/180 days)", "BATTAGLIA16"),
               ev("Pathway prioritisation can lengthen waits for others, so non-pathway waits must be monitored", "OLSSON20"),
               ev("Roadmap 1.2.3 named coordinator (p.32); 3.1.4 pathway-time indicators (p.58); 3.2.2 national peer review run by FICAN/THL (p.60), which Tasan data could later feed", "ROAD", "p.32, p.58, p.60")],
     data_basis=[d("Age-standardised drug-therapy share within 6 months: Varsinais-Suomi 0.8% (0.2–2.0) men / 1.0% women; Vantaa-Kerava 3.7% / 3.8%; Keski-Uusimaa 3.5% / 7.3%; Lapland 10.0% (7.0–14.4) / 15.3% (9.9–22.9); national 25.3% / 25.0% (Taulukko 3.6). Implausible, so recording gaps are likely (inference)", LUNG24AS),
                 d("THL 2017: 'Kansallinen seuranta syöpään sairastuneiden hoitoonpääsystä on puuttunut'", ("THL Työpaperi 3/2017", "https://www.julkari.fi/items/c296653c-356e-4742-a029-ddab51cd0aab", "data/raw/thl_hoitoonpaasy_loppuraportti_2017.txt"), verified="quote present in the analyst's raw text (confirmed by FINDINGS_REVIEW m11); source page not re-opened by JN Care Strategist"),
                 d(FRAGILE, LUNG24)],
     goal3_mapping=["G3-3"], goal2_secondary=[],
     roadmap_actions=["3.1.4 (p.58) pathway-time indicators","1.2.3 (p.32) named coordinator","3.2.2–3.2.3 (p.60–61) national peer review and reaction mechanisms (Tasan data can feed them; that is not county funding)","3.5.3 (p.73–74) digital tools"],
     first_90_days=["Days 1–30: data spec on the THL 21/2016 time points; registry-completeness check (drug therapy, curative RT, MDT, no-record cases vs EHR); 12-month retrospective baseline per county; navigator named", "Days 31–60: weekly feed; day-28 alert switched on; navigator takes alerts", "Days 61–90: first monthly board report (incl. non-pathway waits); day-90 stop/go"],
     risks=["Queue/decision dates and drug-therapy codes may be poorly recorded (see data-quality task)", "Suppress cells <5 patients", "A tracker without capacity changes only documents delay", OUTDATED],
     priority={"impact":"High","effort":"Low-Medium"}))
    T.append(dict(id="T1", priority_rank=2, top3=True, pilot_county="Kymenlaakso (Kymenhva; Etelä-Suomi collaborative area)",
     title="Close the missing step in Kymenlaakso's lung pathway: week-1 pathway map, then 3-day CT, reflex biomarkers and pre-agreed HUS surgery slots where missing",
     bottleneck="diagnosis_to_treatment", pathway_step="Suspected lung cancer referral → CT/bronchoscopy/biopsy → biomarkers → lung meeting → HUS surgery decision → first treatment",
     problem="Kymenlaakso diagnosed 591 lung cancers in 2019–2023, about 118 a year (csv denominator). Its surgical patients depend on another organisation: the surgery decision and the operation are made at HUS Meilahti in Helsinki (kymenhva.fi). Each hand-off between the Kotka pathway and HUS is a point where days can be lost. The county sits in Etelä-Suomi, the collaborative area with the longest median diagnosis→surgery time (46.0 d). That figure is fragile (see data basis) and is area-level context only, not a Kymenlaakso number. Kymenlaakso's crude curative-record share is 19.3% (CI 16.3–22.7) vs 27.0% nationally. Age-standardised (chart-digitised): men ≈18.0% (14.1–22.8), women ≈22.7% (17.2–29.3). South Karelia is similar (18.9% crude) but smaller.",
     action="Week 1: map the current pathway (CT → bronchoscopy/EBUS/biopsy → pathology → biomarkers → Kymenhva lung meeting → HUS Meilahti surgery decision) using T3's dates. Then close only the step(s) that the map shows are missing, from a fixed menu: CT within 3 working days of referral; one diagnostic day; a reflex biomarker panel ordered by pathology for non-squamous NSCLC; surgical cases sent to HUS within 7 days of the lung meeting, into pre-agreed slots; T3's navigator owns the clock.",
     already_exists="Kymenhva already runs a lung outpatient work-up and a multidisciplinary lung meeting (kymenhva.fi). T1 does not invent a pathway: it closes the missing step that the week-1 map finds.",
     owners=["Johtajaylilääkäri, Kymenhva (signer)", "Hallintoylilääkäri, erikoissairaanhoito (sponsor)", "Pulmonology ylilääkäri, Kymenlaakson keskussairaala (clinical lead)", "Radiology", "Pathology/biomarker lab (HUS-operated lab; to confirm)", "HUS Meilahti thoracic surgery (slots)"],
     effort="Medium",
     kpis=[{"name":"Median referral arrival → treatment decision (days), Kymenlaakso","type":"process","ref":"supports G3-3","baseline":"not public; measured by T3 in days 1–30","target":"≥7 days shorter than the county's own baseline by day 90"},
           {"name":"% of Kymenlaakso lung-cancer patients treated ≤42 days from referral arrival","type":"goal3","ref":"G3-3","baseline":"not public; measured by T3 in days 1–30","target":"≥80% (Tasan design choice)","note":OUTDATED},
           {"name":"Crude curative-record share within 12 months (context, registry lag)","type":"goal3","ref":"G3-1 (proxy)","baseline":"19.3% (CI 16.3–22.7; 114/591), dx 2019–2023","baseline_source":"data/csv/lung_report2026_treatment_by_wsc.csv","target":"proposed peer benchmark: national 27.0%. Not a promised effect","note":SHARE_CAVEAT}],
     design=["Longer-term design aim (not a KPI, not a promised effect): referral→decision ≤14 days, based on the one-stop clinic precedent 20→4 d (Chung 2025)"],
     kpi_framing="T1's time KPIs come only from T3's own measured Kymenlaakso baseline (days 1–30). No collaborative-area time figure (13.5 vs 46 d) is used as a KPI: that figure is fragile. The curative share is context, with the national level as a proposed peer benchmark, not a promised effect.",
     expected_effect="Rapid-investigation and one-stop lung clinics shortened time to treatment by about 2–3 weeks in comparable settings. Reflex testing cut time to optimal therapy by ~12 days. No Finnish county evidence is available.",
     evidence=[ev("Rapid Investigation Clinic: time to first treatment −24 days (95% CI 12–35), adjusted; median 78→65 days", "EZER17"),
               ev("One-stop lung cancer clinic: referral→decision to treat 20→4 days; outpatient visits 2.4→1", "CHUNG25"),
               ev("Reflex EGFR/ALK: time to optimal first-line therapy 36→24 days", "CHEEMA17"),
               ev("Norway: place of residence associated with lung surgery waits", "NILSSEN19"),
               ev("Roadmap: molecular answers not fast enough, regional differences", "ROAD", "4.3.3 p.87–88")],
     data_basis=[d("Kymenlaakso 591 lung cancers 2019–2023 (≈118/yr); curative-record share 19.3% (114/591, CI 16.3–22.7); South Karelia 18.9%; national 27.0% (4,009/14,873, verified in raw 2026 text). " + SHARE_CAVEAT, LUNG26),
                 d("Surgery decision and operation for Kymenlaakso patients at HUS Meilahti; treatment recommendations made in Kymenhva's multidisciplinary lung meeting", KYMLUNG, verified="read on kymenhva.fi, 14 Nov 2026"),
                 d("Kymenlaakso age-standardised curative share ≈18.0% men (14.1–22.8), ≈22.7% women (17.2–29.3)", LUNG26AS),
                 d(FRAGILE, LUNG24)],
     goal3_mapping=["G3-3","G3-1"], goal2_secondary=[],
     roadmap_actions=["2.5.2 (p.52–53) referral criteria, Nordic pathway models","3.1.2 (p.56–57) pathways incl. access times 2026–2028","4.3.2–4.3.3 (p.87–88) molecular diagnostics"],
     first_90_days=["Days 1–15: name the clinical lead and the HUS counterpart; week-1 pathway map from T3's dates", "Days 16–45: agree the fix for the missing step(s) (CT rule, reflex SOP, HUS slot agreement)", "Days 46–60: brief GPs/radiology; switch on", "Days 61–90: first 20–30 patients; weekly review with T3; day-90 stop/go"],
     risks=["Crowding out other imaging (Olsson 2020)", "Small monthly n (~10) makes medians noisy", "The map may find the delay sits at HUS. The fix then needs an HUS-side owner", OUTDATED],
     priority={"impact":"High","effort":"Medium"}))
    T.append(dict(id="T2", priority_rank=3, top3=True, pilot_county="Lapland (Lapin hyvinvointialue; Pohjois-Suomi collaborative area)",
     title="Every new Lapland lung cancer reviewed by the existing OYS lung-cancer MDT (by video), plus shared access to curative radiotherapy at OYS (RT referral, travel and accommodation, SBRT/chemoradiation slots)",
     bottleneck="diagnosis_to_treatment", pathway_step="Diagnosis → treatment-intent decision (curative vs palliative)",
     problem="HERO NUMBER (age-standardised, chart-digitised, ±1 pp): curative-treatment share in Lapland ≈16.2% for men (95% CI 12.7–20.4) vs ≈29.8% in Vantaa-Kerava (24.2–36.1); women ≈23.1% (17.9–29.0) vs ≈39.7% (33.1–47.0). The CIs do not overlap in either sex, so age structure does not explain the gap (crude: 18.5% vs 35.6%). Age-standardised SURGERY share for men is the same: Lapland 9.1% (6.0–13.7) vs Vantaa-Kerava 9.0% (5.5–14.1) (2024 report, Taulukko 3.7). So for men the gap is likely in curative radiotherapy. That is the data team's inference: the 2024 report does not separate curative from palliative RT. For women the surgery share also differs (10.4% vs 20.5%). Lapland's radiotherapy is given at OYS in Oulu (lapha.fi), hundreds of kilometres from much of Lapland. Distance worsens outcomes (roadmap p.12–13), and Norwegian data link travel to lower treatment odds.",
     action="Two parts. (1) Review: week-1 audit of which 2025 Lapland lung cancers were discussed at the existing OYS lung-cancer MDT (answers mentor Q4). Then a rule that every new Lapland lung cancer is listed before the treatment-intent decision, with Lapland's clinician on video and ECOG/G8/CFS attached. (2) Curative-RT access (design arm, unpriced; see design): a direct MDT→OYS radiotherapy referral for curative SBRT or chemoradiation, with a reserved weekly slot quota for Lapland patients. Travel (Kela) and patient-hotel accommodation are booked by T3's navigator at the same time, and the decision is not left to the patient alone. Local follow-up is in Rovaniemi.",
     already_exists="Yes. OYS states that the university hospital is responsible for lung-cancer MDTs, surgery and radiotherapy (oys.fi), and Lapland's radiotherapy is given at OYS (lapha.fi). T2 does not create a board: it closes coverage of the existing one to 100% of new Lapland cases, and turns a curative-RT recommendation into a booked slot with travel and accommodation arranged. The registry's 3.0% 'MDT recorded' figure for Lapland is NOT used as proof of a gap: Helsinki shows 0.1%, so it is a recording artefact.",
     owners=["Johtajaylilääkäri, Lapin hyvinvointialue (signer)", "Somaattisen erikoissairaanhoidon johtaja (sponsor)", "Pulmonology ylilääkäri, Lapin keskussairaala (clinical lead)", "OYS lung-cancer MDT lead, Pohde (partner)", "MDT list coordinator", "ICT (video/PACS)"],
     effort="Medium",
     kpis=[{"name":"% of new Lapland lung cancers listed at the OYS MDT before the treatment-intent decision","type":"process","ref":"supports G3-1","baseline":"unknown; audited in week 1","target":"≥90% by day 90 (Tasan design; the Victorian registry rose from 59% to 81%)"},
           {"name":"% of Lapland lung-cancer patients treated ≤42 days from referral arrival","type":"goal3","ref":"G3-3","baseline":"measured by T3 in days 1–30","target":"≥80% (Tasan design choice)","note":OUTDATED},
           {"name":"Age-standardised curative-treatment share within 12 months, by sex (registry lag)","type":"goal3","ref":"G3-1 (proxy)","baseline":"Men ≈16.2% (95% CI 12.7–20.4); women ≈23.1% (17.9–29.0); dx 2019–2023; chart-digitised ±1 pp","baseline_source":"data/csv/lung_report2026_curative_agestd_by_sex_chart_estimate.csv (R2026 Kuva 16)","target":"proposed peer benchmark: Pohjois-Pohjanmaa (OYS's home county, same collaborative area) men ≈23.2% (19.7–26.7), women ≈25.3% (21.0–30.7). Not a promised effect","note":"Age-standardised but NOT stage-, comorbidity- or fitness-adjusted. Chart-digitised estimate, not a published number. Recording practice can still explain part of it."}],
     design=["Curative-RT access arm (design, UNPRICED, not a KPI or cost line yet): direct MDT→OYS radiotherapy referral for curative SBRT/chemoradiation; a reserved weekly Lapland slot quota; Kela travel and patient-hotel accommodation booked by the T3 navigator. To be sized with the OYS radiotherapy lead once identified (week-1 gate). A candidate measure for later: % of curative-RT recommendations starting ≤14 days after the MDT"],
     target_times_caveat=OUTDATED,
     kpi_framing="Target-time caveat: the 42-day KPI follows THL Ohjaus 21/2016, which is marked outdated, has no lung-specific limit, and will be replaced by cancer-specific targets due 2026–2028 (roadmap 3.1.2, p.57). The 80% is a Tasan design choice. Lead KPI is MDT coverage (process). The outcome KPI is the age-standardised, sex-specific curative share, with Pohjois-Pohjanmaa as a proposed peer benchmark, not a promised effect. MDT evidence is observational. 'The gap is in curative RT' is an inference.",
     expected_effect="In population registries, MDT-presented lung patients more often receive surgery and guideline-concordant treatment, with lower mortality. These are observational studies, so selection bias is possible.",
     evidence=[ev("Victorian registry 2011–2020 (n=9,628): non-MDM patients less often had surgery (22.1% vs 31.2%); MDM associated with HR 0.75", "LIN_VLCR"),
               ev("Victorian registry 2011–2023 (n=18,597): MDM presentation 59.1%→80.6%; guideline-concordant NSCLC treatment 56.2% vs 44.5%; propensity-matched HR 0.88", "STIRLING26"),
               ev("Norway: travelling outside the resident health trust reduced the odds of lung surgery", "NILSSEN22"),
               ev("Roadmap: outcomes worse >50 km from the treatment unit; long distances in the north; remote services recommended", "ROAD", "p.12–13")],
     data_basis=[d("Age-standardised curative share: Lapland men ≈16.2% (12.7–20.4), women ≈23.1% (17.9–29.0); Vantaa-Kerava men ≈29.8% (24.2–36.1), women ≈39.7% (33.1–47.0); Pohjois-Pohjanmaa men ≈23.2% (19.7–26.7), women ≈25.3% (21.0–30.7)", LUNG26AS, verified="re-checked against the csv, 14 Nov 2026 (values are the data team's chart digitisation)"),
                 d("Age-standardised surgery within 6 months, men: Lapland 9.1% (6.0–13.7) vs Vantaa-Kerava 9.0% (5.5–14.1); women 10.4% (6.3–16.6) vs 20.5% (14.4–29.7). Any RT, men: Lapland 21.5% (16.6–27.7) vs Vantaa-Kerava 32.3% (25.5–40.6), curative and palliative not separated", LUNG24AS),
                 d("Crude: Lapland 18.5% (131/710, CI 15.8–21.5) vs Vantaa-Kerava 35.6%; no treatment record in Lapland 33.8%. " + SHARE_CAVEAT, LUNG26),
                 d("Lapland cancer patients receive radiotherapy at OYS", ("Lapin hyvinvointialue: Syöpätaudit", "https://lapha.fi/syopataudit", "web page, fetched 14 Nov 2026"), verified="read on lapha.fi, 14 Nov 2026"),
                 d("OYS: university hospital responsible for lung-cancer MDTs, surgery and radiotherapy", OYSLUNG, verified="read on oys.fi, 14 Nov 2026")],
     goal3_mapping=["G3-1","G3-2"], goal2_secondary=[],
     roadmap_actions=["3.1.2 (p.56–57) regional pathways, YTA division of work","3.4.2 (p.69) functional status in referral","3.5.3 (p.73–74) remote/digital","3.2.2–3.2.3 (p.60–61) peer review"],
     first_90_days=["Days 1–7 (GATE): identify and confirm in writing the OYS lung-cancer MDT lead and the OYS radiotherapy lead. Entry points: service-area director for cancer care, OYS (palvelualuejohtaja, OYS Sisätaudit, syöpähoito ja infektiontorjunta) (pohde.fi); physician-in-chief, respiratory medicine, OYS (oulu.fi). Neither is confirmed as MDT or RT lead", "Days 1–20: audit of 2025 Lapland cases at the OYS MDT and of curative-RT referrals/starts; agree the 'all new cases' listing rule, video slot and a weekly Lapland SBRT/chemoradiation quota with the OYS MDT and radiotherapy leads", "Days 21–45: coordinator named; case list fed from pathology; ECOG/G8 fields added", "Days 46–90: weekly listing; log coverage, intent and slots; day-90 stop/go"],
     risks=["Part of the gap may be stage mix, fitness or recording (33.8% no record; Lapland drug-therapy coding also low). Age-standardised only", "The curative-RT inference is unproven until curative and palliative RT are separated in OYS data", "OYS MDT and radiotherapy leads not yet identified: week-1 gate", OUTDATED, "Curative share only measurable with registry lag", "MDT evidence is observational"],
     priority={"impact":"High","effort":"Medium"}))
    T.append(dict(id="G2-1", priority_rank=4, top3=False, optional_goal2=True, pilot_county="City of Helsinki and Kymenlaakso",
     title="(Goal 2, secondary) Extra reminder for men in the colorectal FIT screening programme",
     bottleneck="late_detection", pathway_step="Screening invitation → test return",
     problem="No county reaches the 80% participation target (Goal 2, S p.5). Men 2024: Helsinki 65.2%, Kymenlaakso 65.6%, national 69.2%. 2022–2024 are rollout years (changing age band). This is Goal 2 context only and does not explain the lung pattern.",
     action="The screening centre adds a second reminder (letter/SMS) for non-responding men, with plain-language text.",
     already_exists="Programmes already send invitations and one reminder in some areas. This adds a targeted extra reminder only.",
     owners=["County screening programme lead", "Screening centre", "Communications"],
     effort="Low",
     kpis=[{"name":"Colorectal screening participation, men (Sotkanet 6103)","type":"goal2","ref":"https://sotkanet.fi/sotkanet/en/metadata/indicators/6103","baseline":"Helsinki men 65.2%, Kymenlaakso men 65.6% (2024)","baseline_source":"data/csv/sotkanet_6103_screening_colorectal_attendance.csv","target":"+2.7 pp in the next round (Danish RCT effect for men); 80% is the strategy target"},
           {"name":"Colorectal cancer mortality (contributes to G3-2, long-term)","type":"goal3","ref":"G3-2","baseline":"—","target":"long-term"}],
     kpi_framing="Goal 2, secondary. Not on the pitch lead.",
     expected_effect="Danish RCT: an extra reminder raised participation by 2.7 pp among men.",
     evidence=[ev("Extra reminder +2.7 pp for men (95% CI 1.1–4.2)", "LARSEN22"), ev("FIT screening reduces CRC mortality 10–40% (IARC, per Finnish Cancer Registry)", "SR_CRC")],
     data_basis=[d("Men 2024: Helsinki 65.2%, Kymenlaakso 65.6%, national 69.2%; total national 73.5%; 0/22 counties ≥80% in 2024", S6103)],
     goal3_mapping=["G3-2"], goal2_secondary=["80% screening participation in every county (S p.5)"],
     roadmap_actions=["1.3.1 (p.33)","2.4.5 (p.50)"],
     first_90_days=["Days 1–30: agree a reminder step with the screening centre", "Days 31–90: send; compare return rates with the previous round"],
     risks=["Modest effect", "Rollout-year cohort changes confound trends", "More FIT-positives → colonoscopy demand"],
     priority={"impact":"Medium","effort":"Low"}))
    for t in T:
        t.setdefault("design", [])
        t.setdefault("target_times_caveat", OUTDATED if t["id"] != "G2-1" else None)
        t.update(P[t["id"]])
        c = t["cost_range"]
        if c["low"] is None:
            t["cost_estimate"] = "Unsourced, euro figure dropped. " + "; ".join(c["basis"])
        else:
            t["cost_estimate"] = (f"€{c['low']:,}–€{c['high']:,} ({c['period']}, sourced staff cost only). Unsourced effort, euro figure dropped: "
                                  + "; ".join(c["unsourced_effort"]) + ".")
    return T
