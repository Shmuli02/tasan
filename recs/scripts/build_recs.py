#!/usr/bin/env python3
"""Single source of truth for recommendations.json and the longlist part of recommendations.md.
Run: python3 recs/scripts/build_recs.py  (from /workspace/junction-new)"""
import json, os
HERE = os.path.dirname(os.path.abspath(__file__)); OUT = os.path.dirname(HERE)

STRAT = "https://files.hackjunction.app/resources/Kansallinen_syopastrategia_2026_2035_FINAL.pdf"
ROAD = "https://files.hackjunction.app/resources/Kansallinen_syopastrategia_toimeenpanon_tiekartta_2026_2031.pdf"
THL21 = "https://www.julkari.fi/items/0424a55a-f159-406f-8883-5dfdad4d6772"
SOTK = "https://sotkanet.fi/sotkanet/fi/metadata/indicators/"

S = {  # source_id: (title, url)
 "STRAT": ("Kansallinen syöpästrategia 2026–2035 (STM)", STRAT),
 "ROAD": ("Kansallinen syöpästrategia – Toimeenpanon tiekartta 2026–2031", ROAD),
 "THL21": ("THL Ohjaus 21/2016 Hoitoonpääsyn seuranta syövän hoidossa", THL21),
 "JENSEN15": ("Jensen H et al. Diagnostic intervals before and after implementation of cancer patient pathways. BMC Cancer 2015", "https://link.springer.com/article/10.1186/s12885-015-1317-7"),
 "JENSEN16": ("Jensen H et al. Tumour stage and implementation of standardised cancer patient pathways. Br J Gen Pract 2016", "https://bjgp.org/content/bjgp/66/647/e434.full.pdf"),
 "FJALL23": ("Fjällström P et al. Reduction in the diagnostic interval after the introduction of cancer patient pathways for colorectal cancer in northern Sweden. Scand J Prim Health Care 2023", "https://pubmed.ncbi.nlm.nih.gov/37450480/"),
 "SCHMIDT18": ("Schmidt I et al. The national program on standardized cancer care pathways in Sweden: observations half way through. Health Policy 2018", "https://pubmed.ncbi.nlm.nih.gov/30075866/"),
 "OLSSON20": ("Olsson O. Are cancer care pathways associated with longer waiting times? Crowding out in radiology, pathology and surgery. 2020", "https://journals.sagepub.com/doi/10.1177/2053434520978173"),
 "NILSSEN19": ("Nilssen Y et al. Decreasing waiting time for treatment before and during implementation of cancer patient pathways in Norway. Cancer Epidemiol 2019", "https://pubmed.ncbi.nlm.nih.gov/31153048/"),
 "NILSSEN22": ("Nilssen Y et al. Compliance with recommended cancer patient pathway timeframes ... Norway 2015–2016. BMC Cancer 2022", "https://link.springer.com/article/10.1186/s12885-022-09306-9"),
 "CHAPMAN20": ("Chapman D et al. First results from five multidisciplinary diagnostic centre (MDC) projects for non-specific but concerning symptoms. Br J Cancer 2020", "https://www.nature.com/articles/s41416-020-0947-y"),
 "GRONNEMOSE24": ("Grønnemose RB et al. Risk of cancer and serious disease in Danish patients with urgent referral for serious non-specific symptoms, Funen 2014–2021. Br J Cancer 2024", "https://pubmed.ncbi.nlm.nih.gov/38409600/"),
 "DAMHUS24": ("Damhus CS et al. Diagnostic flow for all patients referred with non-specific symptoms of cancer to a diagnostic centre in Denmark. Eur J Gen Pract 2024", "https://pubmed.ncbi.nlm.nih.gov/38179994/"),
 "NICE690": ("NICE HTG690: Quantitative FIT to guide colorectal cancer pathway referral in primary care (2023)", "https://www.nice.org.uk/guidance/HTG690/chapter/recommendations"),
 "BSG22": ("ACPGBI & BSG. FIT in patients with signs or symptoms of suspected CRC: joint ACPGBI/BSG guideline. Gut 2022", "https://www.acpgbi.org.uk/resources/1075/fit_in_patients_with_signs_or_symptoms_of_suspected_crc_a_joint_guideline_from_acpgbi_and_bsg/"),
 "SR_CRC": ("Suomen Syöpärekisteri: Suolistosyövän seulonta", "https://syoparekisteri.fi/seulonta/suolistosyovan-seulonta/"),
 "LARSEN22": ("Larsen MB et al. The impact of pre-notifications and reminders on participation in colorectal cancer screening – RCT. Prev Med 2022", "https://pubmed.ncbi.nlm.nih.gov/36057390/"),
 "BATTAGLIA16": ("Battaglia TA et al. The impact of patient navigation on the delivery of diagnostic breast cancer care (PNRP). Breast Cancer Res Treat 2016", "https://pubmed.ncbi.nlm.nih.gov/27432417/"),
 "VIMAL15": ("Vimalananda VG et al. Electronic consultations (e-consults) to improve access to specialty care: systematic review. J Telemed Telecare 2015", "https://pubmed.ncbi.nlm.nih.gov/25995331/"),
 "GAYE21": ("Gaye M et al. Association of eConsult implementation with access to specialist care in a large urban safety-net system. JAMA Health Forum 2021", "https://pubmed.ncbi.nlm.nih.gov/35977310/"),
 "GULD15": ("Guldbrandt LM et al. The effect of direct access to CT scan in early lung cancer detection: cluster-randomised trial. BMC Cancer 2015", "https://pubmed.ncbi.nlm.nih.gov/26608727/"),
 "CHEEMA17": ("Cheema PK et al. Impact of reflex EGFR/ALK testing on time to treatment of patients with advanced nonsquamous NSCLC. J Oncol Pract 2017", "https://ascopubs.org/doi/10.1200/JOP.2016.014019"),
 "NHSCWT26": ("NHS England. Cancer Waiting Times statistical release, March 2026 (Faster Diagnosis Standard 75% → 80%)", "https://www.england.nhs.uk/statistics/wp-content/uploads/sites/2/2026/10/Cancer-Waiting-Times-Statistical-Release-March-2026-Provider-based-Final.pdf"),
 "EZER17": ("Ezer N et al. Impact of rapid investigation clinic on timeliness of lung cancer diagnosis and treatment. BMC Pulm Med 2017", "https://pubmed.ncbi.nlm.nih.gov/29216855/"),
 "CHUNG25": ("Hiu Nian Chung J et al. Fast-tracked and optimised: the impact of a one-stop lung cancer clinic on patient outcomes. Future Healthc J 2025", "https://pubmed.ncbi.nlm.nih.gov/41209680/"),
 "LIN_VLCR": ("Lin T, Pham J, Paul E et al. Impacts of lung cancer multidisciplinary meeting presentation: drivers and outcomes from a population registry retrospective cohort study", "https://research.monash.edu/en/publications/impacts-of-lung-cancer-multidisciplinary-meeting-presentation-dri/"),
 "STIRLING26": ("Stirling RG et al. Impacts of multidisciplinary lung cancer meeting presentation in a clinical quality registry. JTO Clin Res Rep 2026", "https://pubmed.ncbi.nlm.nih.gov/42006279/"),
 "KT24": ("KT Kunta- ja hyvinvointialuetyönantajat: wellbeing-sector average total earnings Oct 2024 (€4,089/month)", "https://www.kt.fi/uutiset-ja-tiedotteet/2026/kunta-ja-hyvinvointialan-keskiansiot-paivitetty-2024"),
 "KT25": ("KT: Hyvinvointialan palkkatilastot, Oct 2025 (sairaanhoitaja €3,174/€4,048; analyytikko €4,663/€4,891; erikoislääkäri €6,864/€11,000 per month, task-based/total)", "https://www.kt.fi/tilastot-ja-julkaisut/hyvinvointialan-palkat"),
 "KTSIVU": ("KT: Henkilöstökulut, employer contributions wellbeing sector 2026 = 23.14%", "https://www.kt.fi/tilastot-ja-julkaisut/henkilostokulut"),
 "KYMJOHTO": ("Kymenhva: Hyvinvointialueen johto (roles: johtajaylilääkäri / CMO; hallintoylilääkäri, erikoissairaanhoito / administrative chief physician, specialised care; johtajaylihoitaja / chief nursing officer)", "https://kymenhva.fi/toimipisteet-ja-yhteystiedot/yhteystiedot/hyvinvointialueen-johto/"),
 "KYMLUNG": ("Kymenhva: Keuhkosyöpä ja keuhkopussin mesoteliooma (lung meeting; surgery decision and surgery at Meilahti)", "https://kymenhva.fi/palvelut-ja-ajanvaraus/erikoissairaanhoito/poliklinikat-ja-erikoisalat/keuhkosairaudet/keuhkosyopa-ja-mesoteliooma/"),
 "LAPORG": ("Lapin hyvinvointialue: Hallinto ja organisaatio (roles: johtajaylilääkäri / CMO; somaattisen erikoissairaanhoidon johtaja / director of somatic specialised care; vs. hoitotyön johtaja / acting director of nursing)", "https://lapha.fi/tietoameista/hallinto-ja-organisaatio"),
 "LAPSYOPA": ("Lapin hyvinvointialue: Syöpätaudit (radiotherapy given at OYS)", "https://lapha.fi/syopataudit"),
 "OYSLUNG": ("OYS: Keuhkosyöpäpotilaan hoitopolku (university hospital responsible for lung-cancer MDTs, surgery, radiotherapy)", "https://oys.fi/palvelumme/syopataudit/keuhkosyopapotilaan-hoitopolku/"),
 "POHDE": ("Pohde: Pohjois-Suomen yhteistyöalueen tutkimustoimikunta 2025–2029 (includes the johtajaylilääkäri / CMO, Pohde)", "https://pohde.fi/tietoa-meista/paatoksenteko/pohjois-suomen-yhteistyoalueen-tutkimustoimikunta/"),
 "FILHA26": ("Filha: Keuhkosyöpäpäivä 27.11.2026 programme (FICAN North director, OYS, speaking)", "https://www.filha.fi/wp-content/uploads/2026/10/Keuhkosyopapaiva-2026-ohjelma.pdf"),
 "HUSKYM": ("HUS: Kymenlaakson keskussairaalan laboratorio", "https://www.hus.fi/potilaalle/sairaalat-ja-toimipisteet/kymenlaakson-keskussairaalan-laboratorio"),
}
def ev(claim, sid, loc=""):
    t, u = S[sid]
    return {"claim": claim, "source_id": sid, "source_title": t + (f", {loc}" if loc else ""), "url": u}

NAV_COST = ("1 FTE nurse ≈ €46,902–€59,816/yr (sairaanhoitaja task-based €3,174 to total €4,048 per month, KT Oct 2025, "
            "× 12 × 1.2314 employer contributions, KT 2026)")

G3 = {
 "G3-1": "5-year survival of poor-prognosis cancers reaches Nordic level (STRAT p.5)",
 "G3-2": "Cancer mortality −10% (STRAT p.5)",
 "G3-3": "Patients get treatment within target times (THL Ohjaus 21/2016) (STRAT p.5; sub-goal 3.1 p.33)",
}

R = []
def add(**k): R.append(k)

# ---------------- A. LATE DETECTION ----------------
add(id="A1", title="Non-specific serious symptoms (NSSC) fast-track pathway, run by the county's diagnostic unit",
 bottleneck="late_detection", pathway_step="Primary care → diagnostic work-up for vague symptoms (weight loss, fatigue, anaemia, GP 'gut feeling')",
 problem="Organ-specific fast tracks miss patients with vague symptoms. In Denmark, 62.8% of cancer patients after pathway rollout were not referred via a pathway and had longer diagnostic intervals (Jensen 2015). Poor-prognosis cancers (pancreas, liver, lung, stomach) often present vaguely (ROAD p.22).",
 action="Open one NSSC referral route: a GP referral form with criteria, a 1-day CT + lab package at the central hospital, and internal-medicine-led triage. Target: diagnosis or exclusion within 28 days (the NHS Faster Diagnosis Standard benchmark).",
 owners=["County chief medical officer (sponsor)", "Central-hospital internal medicine (clinical lead)", "Radiology (reserved CT slots)", "GPs (referral criteria)", "Nurse coordinator (booking, patient contact)", "ICT/Apotti or Lifecare/Kanta (referral form)"],
 effort="Medium–High", cost_estimate="ESTIMATE: 1 FTE nurse coordinator (" + NAV_COST + ") + reallocated internal-medicine sessions + reserved CT slots (local unit costs needed; not verified).",
 kpis=[{"name":"Treatment within target times (≤6 wk referral→treatment)","type":"goal3","ref":"G3-3"},
       {"name":"Share diagnosed via NSSC route, conversion rate (% cancer)","type":"process","ref":"county-internal"},
       {"name":"Stage I–II share (Goal 2, secondary)","type":"goal2","ref":"STRAT p.5"}],
 expected_effect="Precedents report cancer in 8–20% of referrals. Funen (DK) rose to ~6% of all new cancers found via this route. A Finnish yield is unknown until piloted.",
 evidence=[ev("5 English MDC pilots: 2,961 referrals, 241 cancers (8% conversion), broad range incl. rare cancers", "CHAPMAN20"),
           ev("Funen 2014–2021: 6,698 referrals, 20.2% had cancer; share of all new cancers found via the route rose from 3% to 6%", "GRONNEMOSE24"),
           ev("Farsø DC 2020: 8% of 314 referrals had cancer; >¼ redirected", "DAMHUS24"),
           ev("NHS Faster Diagnosis Standard: 28 days, target 75% to 31 Mar 2026, 80% from 1 Apr 2026", "NHSCWT26")],
 goal3_mapping=["G3-3","G3-1"], goal2_secondary=["70% stage I–II"],
 roadmap_actions=["2.5.2 (p.52–53) symptom-based models, direct test routes","3.1.2 (p.56–57)","Huonon ennusteen syövät (p.22–24)"],
 first_90_days=["Wk 1–3: pick site and clinical lead; adapt Danish/UK NSSC criteria", "Wk 4–6: reserve 2–4 CT slots/wk; create referral template", "Wk 7–9: brief GPs in 3–5 health centres", "Wk 10–13: go live and log referral date, diagnosis date, outcome"],
 risks=["Low conversion if criteria are loose; crowding out other imaging (Olsson 2020)", "Incidental findings increase workload", "Small numbers in Q1: effect not measurable within 90 days"],
 priority={"impact":"High","effort":"Medium-High"})

add(id="A2", title="Symptomatic FIT in primary care to triage lower-GI symptoms",
 bottleneck="late_detection", pathway_step="GP visit with lower-GI symptoms → colonoscopy referral",
 problem="Colonoscopy capacity is shared with the expanding national FIT screening programme (ages 56–74 by 2031). Unprioritised symptomatic referrals queue together.",
 action="Adopt the NICE/BSG rule: quantitative FIT for adults with lower-GI symptoms. FIT ≥10 µg Hb/g → suspected-cancer referral. Below that → safety-netting, and GPs may still refer on clinical concern.",
 owners=["County primary-care medical director", "Lab (quantitative FIT analysis)", "Endoscopy unit (priority slots)", "GPs/nurses (test issue and safety-net)"],
 effort="Low–Medium", cost_estimate="ESTIMATE: test kit + analysis per patient (price must come from the county lab contract; not verified). Uses the existing screening-lab FIT capability (SR_CRC).",
 kpis=[{"name":"Referral→treatment ≤6 wk for CRC","type":"goal3","ref":"G3-3"},{"name":"CRC mortality (part of −10%)","type":"goal3","ref":"G3-2"},
       {"name":"Colonoscopy waiting time; FIT-positive→colonoscopy days","type":"process","ref":"county-internal"}],
 expected_effect="NICE judged FIT-guided referral cost-effective because colonoscopy capacity goes to those most likely to have CRC. We do not cite a quantified Finnish effect.",
 evidence=[ev("FIT ≥10 µg Hb/g → suspected-cancer referral; safety-netting below threshold; FIT must not block referral if concern persists", "NICE690", "rec 1.2–1.3"),
           ev("Joint UK guideline recommends FIT to prioritise symptomatic referrals", "BSG22"),
           ev("Finland's national CRC screening uses FIT, started 2022, covers ages 56–74 from 2031", "SR_CRC")],
 goal3_mapping=["G3-3","G3-2"], goal2_secondary=["70% stage I–II"],
 roadmap_actions=["2.5.2 (p.52–53) primary-care test responsibilities","3.1.2 (p.56–57)"],
 first_90_days=["Wk 1–4: agree threshold and pathway with the gastro unit and lab", "Wk 5–8: EHR order set + safety-net recall list", "Wk 9–13: launch in pilot health centres; track FIT volume and positivity"],
 risks=["False negatives if safety-netting fails", "Return rates of samples may be lower in some groups (NICE research rec 1.5)"],
 priority={"impact":"Medium-High","effort":"Low"})

add(id="A3", title="Lift FIT screening uptake in low-participation municipalities (extra reminder + multilingual outreach)",
 bottleneck="late_detection", pathway_step="Population screening invitation → test return → FIT-positive colonoscopy",
 problem="Strategy target: 80% participation in every county (Goal 2). Participation varies by area (Sotkanet 6103, regional values to come from the data analyst).",
 action="Add a second reminder (letter/SMS) to the screening-centre invitation flow for non-responders. Produce multilingual and plain-language material. A screening nurse calls every FIT-positive person to book colonoscopy.",
 owners=["County screening coordinator", "Screening centre (invitations)", "Screening nurses", "Communications + NGOs for language minorities"],
 effort="Low", cost_estimate="ESTIMATE: postage/SMS per non-responder + design of material. National funding exists for language outreach: roadmap 1.3.1 €400,000 (ROAD p.33).",
 kpis=[{"name":"CRC mortality (part of −10%)","type":"goal3","ref":"G3-2"},
       {"name":"Colorectal screening participation % (Sotkanet 6103)","type":"sotkanet","ref":SOTK+"6103"},
       {"name":"80% participation per county (Goal 2, secondary)","type":"goal2","ref":"STRAT p.5"}],
 expected_effect="In a Danish RCT (59,041 people), a four-stage invitation raised participation from 66.9% to 69.8% (+2.9 pp). FIT screening reduces CRC mortality by 10–40% (IARC, cited by the Cancer Registry).",
 evidence=[ev("Four-stage invitation (pre-notification + 2 reminders): +2.9 pp (66.9%→69.8%); +4.0 pp at ages 50–59", "LARSEN22"),
           ev("FIT screening reduces CRC mortality 10–40% (IARC Handbook 17, as reported by the Finnish Cancer Registry)", "SR_CRC"),
           ev("Roadmap target: participation of non-Finnish/Swedish speakers reaches the majority level", "ROAD", "action 1.3.1 p.33")],
 goal3_mapping=["G3-2"], goal2_secondary=["80% screening participation in every county"],
 roadmap_actions=["1.3.1 (p.33)","2.4.5 (p.50)"],
 first_90_days=["Wk 1–2: pull participation by municipality (Sotkanet 6103, screening registry)", "Wk 3–6: agree a reminder step with the screening centre", "Wk 7–13: send reminders in the lowest-uptake municipalities; compare return rates"],
 risks=["More FIT-positives → colonoscopy demand", "Effect is modest (+3 pp); mortality impact takes years"],
 priority={"impact":"Medium","effort":"Low"})

add(id="A4", title="Record 'first symptom date' and flag repeat consultations in primary care (data + AI safety-net)",
 bottleneck="late_detection", pathway_step="Repeated GP/nurse contacts before referral",
 problem="Strategy: data from first symptom to diagnosis are not collected systematically, and stage-bearing clinical notifications cover only ~40% of cases (STRAT p.30). In MDC data, more GP consultations before referral weakened the association with cancer (Chapman 2020).",
 action="Add a structured 'cancer suspicion / first symptom date' field to the GP referral. Run a monthly EHR query flagging ≥3 contacts in 90 days for red-flag codes (anaemia, weight loss, haematuria) for GP review. This is a pilot of AI-assisted early detection as the strategy envisages.",
 owners=["County CMIO / ICT (EHR field, query)", "Primary-care medical director", "GPs (review flag list)", "Data analyst (evaluation)"],
 effort="Medium", cost_estimate="ESTIMATE: EHR change request (vendor cost unknown, ask the county ICT) + ~0.2 FTE analyst. National support: roadmap 3.5.3 €1.14 M (ROAD p.74).",
 kpis=[{"name":"Treatment within target times (G3-3), extended upstream to first symptom","type":"goal3","ref":"G3-3"},
       {"name":"% referrals with first-symptom date recorded","type":"process","ref":"county-internal"}],
 expected_effect="Mainly a measurement fix that makes delays visible. No direct outcome evidence verified for the flag itself. Mark as experimental.",
 evidence=[ev("First-symptom-to-diagnosis data not collected systematically; stage notifications ~40% coverage", "STRAT", "p.30"),
           ev("Target state: health IT and AI used to support early detection; collect symptom-to-diagnosis data", "STRAT", "p.30"),
           ev("GP 'clinical suspicion' strong predictor; more prior GP consultations → weaker association with cancer", "CHAPMAN20")],
 goal3_mapping=["G3-3"], goal2_secondary=["2.5 symptom-to-diagnosis data"],
 roadmap_actions=["3.5.3 (p.73–74) digital tools and AI","4.1.1 (p.77) structured recording","3.2.2 (p.60)"],
 first_90_days=["Wk 1–4: define field + codes with GPs", "Wk 5–10: ICT build/test", "Wk 11–13: first monthly flag list; audit 50 flagged cases"],
 risks=["Alert fatigue", "Data protection / secondary-use rules (toisiolaki)", "No proven outcome effect yet"],
 priority={"impact":"Medium","effort":"Medium"})

# ---------------- B. PRIMARY → SPECIALIST REFERRAL ----------------
add(id="B1", title="Regional suspected-cancer referral pathway (pakkeforløb-style) for 3–5 common cancers",
 bottleneck="referral", pathway_step="GP referral → specialist acceptance → first diagnostic visit",
 problem="Finland has no cancer-specific pathway times in force. The only reference is THL Ohjaus 21/2016 (6 weeks referral→treatment), which is marked outdated and has no lung-specific limit. Cancer-specific times are due 2026–2028 (ROAD 3.1.2, p.57).",
 action="The county adopts written referral criteria plus a 'syöpäepäily' (suspected cancer) referral flag for lung, colorectal, breast, prostate and one poor-prognosis cancer. The receiving unit books the first diagnostic step within a fixed number of days. Timestamps follow THL 21/2016.",
 owners=["County oncology/central hospital clinical directors", "Primary-care medical director", "Referral-handling unit", "FICAN regional centre (alignment)"],
 effort="Medium", cost_estimate="ESTIMATE: mostly staff time (working groups, GP training). National funding is earmarked for pathways: €5 M/yr covering 2.5.2 and 3.1.2 (ROAD p.55).",
 kpis=[{"name":"% treated ≤6 wk from referral (THL 21/2016)","type":"goal3","ref":"G3-3"},
       {"name":"Referral arrival → first visit (days, median)","type":"process","ref":"THL21 time points"},
       {"name":"Median waiting time, specialised care (Sotkanet 5083, context only)","type":"sotkanet","ref":SOTK+"5083"}],
 expected_effect="Denmark: median diagnostic interval −17 days after pathway rollout (49→32 days unadjusted). Northern Sweden CRC: 47→29 days. Effects concentrate in patients actually referred into pathways.",
 evidence=[ev("Median diagnostic interval 17 days shorter after CPP implementation (adjusted); unadjusted 49→35→32 days", "JENSEN15"),
           ev("Patients not referred via a pathway had longer intervals; stage distribution did not change overall", "JENSEN16"),
           ev("Northern Sweden CRC: median diagnostic interval 47→29 days after SVF, except right-sided colon", "FJALL23"),
           ev("SVF: waiting times shortened for first pathways; crowding out must be managed", "SCHMIDT18"),
           ev("Roadmap expects standardised referral criteria for ≥5 cancers and county pilots in 2026–2028", "ROAD", "2.5.2 p.53")],
 goal3_mapping=["G3-3","G3-1"], goal2_secondary=["Referral criteria in all national pathways (2.5)"],
 roadmap_actions=["2.5.2 (p.52–53)","3.1.2 (p.56–57)","3.1.4 (p.58)"],
 first_90_days=["Wk 1–3: choose 3 cancers; copy Danish/Swedish/Norwegian criteria as drafts", "Wk 4–8: clinical consensus; create referral flag in EHR", "Wk 9–13: launch; weekly report of flagged referrals and days to first visit"],
 risks=["Crowding out non-pathway patients (Olsson 2020)", "Over-referral strains imaging", "Pathway-outside patients may wait longer (Jensen 2015)"],
 priority={"impact":"High","effort":"Medium"})

add(id="B2", title="Named cancer-pathway coordinator (nurse navigator) from referral to first treatment",
 bottleneck="referral", pathway_step="Referral receipt → tests → MDT → treatment start",
 problem="The roadmap notes that if the patient cannot demand urgent care or coordination is poor, total time 'may become very long' (ROAD p.13).",
 action="Appoint 1–2 nurse coordinators at the central hospital. They own every flagged suspected-cancer referral: booking tests, chasing results, one phone number for patient and GP, and escalating breaches of the 6-week target.",
 owners=["Central-hospital nursing director", "Nurse coordinators", "Oncology/surgical units", "GP (receives status)"],
 effort="Low–Medium", cost_estimate=NAV_COST + " → 2 FTE ≈ €93,804–€119,632/yr.",
 kpis=[{"name":"% treated ≤6 wk from referral","type":"goal3","ref":"G3-3"},
       {"name":"Use of named-coordinator model (roadmap 1.2.3 indicator)","type":"roadmap","ref":"ROAD p.32"}],
 expected_effect="Norway introduced a cancer pathway coordinator role with its pathways. US navigation trial: OR 2.12 for timely diagnostic resolution at 365 days, with no difference at 60/180 days. The effect on Finnish waiting times is unverified.",
 evidence=[ev("Norwegian CPPs introduced a cancer pathway coordinator to manage referrals, book appointments and inform patients", "NILSSEN22"),
           ev("Patient navigation: aOR 2.12 (1.36–3.29) for timely diagnostic resolution at 365 days; no significant effect at 60/180 days", "BATTAGLIA16"),
           ev("Roadmap 1.2.3: named coordinating worker model; guidance 2026–2028, county adoption 2029–2031", "ROAD", "p.32")],
 goal3_mapping=["G3-3"], goal2_secondary=[],
 roadmap_actions=["1.2.3 (p.32)","3.1.2 (p.56–57)"],
 first_90_days=["Wk 1–4: role description, redeploy 1 experienced nurse", "Wk 5–8: coordinator list of all flagged referrals; breach escalation rule", "Wk 9–13: report weekly breaches and causes"],
 risks=["Single-person dependency", "Effect unproven in Finland; the US evidence comes from a different context"],
 priority={"impact":"Medium-High","effort":"Low"})

add(id="B3", title="Asynchronous e-consultation (GP ↔ specialist) before or instead of referral",
 bottleneck="referral", pathway_step="GP uncertainty → referral decision",
 problem="Rejected or incomplete referrals and unclear cases add loops. Distances in Finland are long (>400 km to a central hospital for some, ROAD p.13).",
 action="Specialists in key tumour areas answer GP e-consults within 2 working days, converting to a pathway referral when needed.",
 owners=["Specialty units (rota of answering specialists)", "GPs", "ICT (consult message type in EHR)"],
 effort="Low–Medium", cost_estimate="ESTIMATE: specialist time ~ a few hours/week per specialty (not costed). Reuses existing EHR messaging; vendor cost unknown.",
 kpis=[{"name":"% treated ≤6 wk from referral","type":"goal3","ref":"G3-3"},
       {"name":"E-consult response time; % resolved without a visit","type":"process","ref":"county-internal"}],
 expected_effect="NYC safety-net: 13% of requests resolved electronically, wait time −8.2 days (−13.3%). Systematic review: timely specialist input, well received by GPs.",
 evidence=[ev("27 studies: e-consults provide timely specialty access and are well received by PCPs", "VIMAL15"),
           ev("13% of requests resolved electronically; mean wait 61.0→54.1 days (adjusted −8.2 days)", "GAYE21")],
 goal3_mapping=["G3-3"], goal2_secondary=[],
 roadmap_actions=["3.5.3 (p.73–74) digital tools, remote consultations","3.4 (p.39) primary care can consult geriatric-oncology team"],
 first_90_days=["Wk 1–4: pick 2 specialties; define a 2-day response", "Wk 5–13: run and track volume, response time, conversions"],
 risks=["Evidence not cancer-specific", "Specialist time is not freed automatically"],
 priority={"impact":"Medium","effort":"Low"})

add(id="B4", title="Direct GP access to diagnostic imaging (straight-to-test) for selected symptoms",
 bottleneck="referral", pathway_step="GP → imaging without a specialist visit",
 problem="Each extra specialist visit adds days. The roadmap explicitly mentions direct test routes (ROAD p.52).",
 action="Allow GPs to order chest CT or abdominal US directly for defined symptoms, with radiology reporting within 1 week (THL 21/2016 target).",
 owners=["Radiology", "Primary care", "Pathway group (criteria)"],
 effort="Medium", cost_estimate="ESTIMATE: imaging volume shift. Unit costs from the county price list (not verified).",
 kpis=[{"name":"Imaging report ≤1 week (THL 21/2016 sub-target)","type":"goal3","ref":"G3-3"}],
 expected_effect="MIXED evidence: a Danish cluster RCT of direct GP access to low-dose CT did not significantly change stage or time to diagnosis.",
 evidence=[ev("Direct GP access to LDCT: no significant effect on stage or time to diagnosis", "GULD15"),
           ev("THL target: radiology report within 1 week of request in suspected cancer", "THL21", "printed p.13")],
 goal3_mapping=["G3-3"], goal2_secondary=[],
 roadmap_actions=["2.5.2 (p.52) suorat tutkimusreitit"],
 first_90_days=["Only as part of B1 criteria; measure before scaling"],
 risks=["Evidence does not show outcome benefit", "Imaging overuse"],
 priority={"impact":"Low-Medium","effort":"Medium"})

add(id="B5", title="Functional status (G8 / Clinical Frailty Scale) in every suspected-cancer referral for patients ≥75",
 bottleneck="referral", pathway_step="GP referral content → specialist test planning for older patients",
 problem="The number of cancer patients over 75 is growing fast, and functional assessment is often missing (STRAT p.39).",
 action="Add mandatory G8/CFS fields to the referral template for patients aged 75+. Specialists use them to plan tests and avoid futile invasive work-up.",
 owners=["Primary-care GPs/nurses", "ICT (template)", "Geriatrics/oncology"],
 effort="Low", cost_estimate="ESTIMATE: template change + 1-hour training. National: roadmap 3.4.2 €1 M (ROAD p.69).",
 kpis=[{"name":"% treated ≤6 wk (older patients)","type":"goal3","ref":"G3-3"},
       {"name":"Functional status included in referrals (roadmap 3.4.2 indicator)","type":"roadmap","ref":"ROAD p.69"}],
 expected_effect="Supports appropriate, faster decisions. No quantified waiting-time effect verified.",
 evidence=[ev("GP describes functional status with G8/CFS in the referral; this should guide diagnostic planning", "ROAD", "3.4.2 p.69"),
           ev("Goal 3.4 indicators include primary care able to consult a geriatric-oncology team at the diagnostic stage", "STRAT", "p.39")],
 goal3_mapping=["G3-3"], goal2_secondary=[],
 roadmap_actions=["3.4.2 (p.69)","3.4.1 (p.68)"],
 first_90_days=["Wk 1–6: template + guidance", "Wk 7–13: audit completion in 50 referrals"],
 risks=["Form burden for GPs"],
 priority={"impact":"Low-Medium","effort":"Low"})

# ---------------- C. DIAGNOSIS → TREATMENT ----------------
add(id="C1", title="Monthly 'time-to-treatment' dashboard on THL 21/2016 time points, with breach alerts",
 bottleneck="diagnosis_to_treatment", pathway_step="Referral arrival → first visit → treatment decision → first treatment",
 problem="The G3-3 target exists (6 weeks), but there is no public regional reporting. Norway found the treatment decision→start step to be the main delay for all cancers studied.",
 action="Extract the four THL 21/2016 dates from the EHR/Hilmo for 16 cancers. Publish median and % ≤6 weeks per cancer and per municipality monthly to the county board. The coordinator (B2) gets an alert at day 28 without a treatment decision.",
 owners=["County knowledge management / data analyst", "ICT (data extraction)", "Oncology clinical director (owner of action)", "County board (oversight)"],
 effort="Medium", cost_estimate="ESTIMATE: ~0.5 FTE analyst for 3 months + BI tool already licensed (assumption). (ROAD 3.2.2, p.60, funds national FICAN/THL peer review, not county work.)",
 kpis=[{"name":"% treated ≤6 wk from referral, per cancer & area","type":"goal3","ref":"G3-3"},
       {"name":"Treatment decision → first treatment (days)","type":"process","ref":"THL21"}],
 expected_effect="Makes the Goal 3 indicator visible. Norway's national monitoring located bottlenecks (decision→treatment, travel outside the home trust). Outcome effect depends on the actions triggered.",
 evidence=[ev("THL 21/2016 defines time points: referral arrival, first visit, treatment-queue date, first treatment; max 6 weeks referral→first treatment", "THL21", "PDF p.5, printed p.13"),
           ev("Norway 2015–16: decision→treatment was the main delay; travelling outside the home health trust prolonged waits", "NILSSEN22"),
           ev("Roadmap 3.2.2–3.2.3: peer benchmarking and steering mechanisms to react to deviations", "ROAD", "p.60–61")],
 goal3_mapping=["G3-3"], goal2_secondary=[],
 roadmap_actions=["3.1.4 (p.58)","3.2.2 (p.60)","3.2.3 (p.61)","3.5.3 (p.73–74)"],
 first_90_days=["Wk 1–4: data extraction spec (THL 21/2016 codes)", "Wk 5–8: baseline for last 12 months", "Wk 9–13: first board report + alerts"],
 risks=["Recording quality of queue/decision dates", "Small numbers per municipality → suppress cells <5"],
 priority={"impact":"High","effort":"Medium"})

add(id="C2", title="Pathologist-initiated reflex biomarker testing for NSCLC (and other agreed tumours)",
 bottleneck="diagnosis_to_treatment", pathway_step="Histology → molecular result → first systemic treatment",
 problem="Roadmap: molecular tests are done in many labs, answers are not ready fast enough for treatment planning, and there are notable regional differences (ROAD p.88).",
 action="Pathology automatically orders the agreed biomarker panel at diagnosis of non-squamous NSCLC, without waiting for an oncologist request. Results go via electronic channels.",
 owners=["County pathology lab", "Thoracic oncology", "Lab procurement (send-out contract)", "MTB/regional centre"],
 effort="Low–Medium", cost_estimate="ESTIMATE: no extra tests per eligible patient (testing moves earlier). Some extra tests may follow in patients who would not have been tested. Panel price from the lab contract (not verified). National: roadmap 4.3.3 €400,000 (ROAD p.88).",
 kpis=[{"name":"% treated within target times (lung)","type":"goal3","ref":"G3-3"},
       {"name":"Lung cancer 5-yr survival to Nordic level","type":"goal3","ref":"G3-1"},
       {"name":"Biopsy → molecular result (days)","type":"process","ref":"county-internal"}],
 expected_effect="Toronto: median time to treatment 34→22 days (excluding intentional delays), time to optimal first-line therapy 36→24 days, fewer failed tests.",
 evidence=[ev("Reflex EGFR/ALK: time to optimal first-line therapy 36→24 days (p=.036); TTT 34→22 days excluding intentional delays; failed EGFR tests 14%→4%", "CHEEMA17"),
           ev("Molecular testing done in several labs, low utilisation, answers not fast enough; regional differences", "ROAD", "4.3.3 p.87–88"),
           ev("G3-1 targets lung cancer 5-yr survival +>14 pp to Nordic level", "STRAT", "p.5")],
 goal3_mapping=["G3-3","G3-1"], goal2_secondary=[],
 roadmap_actions=["4.3.2 (p.87)","4.3.3 (p.87–88)","4.3.4 (p.88)"],
 first_90_days=["Wk 1–4: agree reflex criteria and panel with oncology", "Wk 5–8: lab SOP; send-out logistics", "Wk 9–13: go live; measure turnaround time"],
 risks=["Cost shift to the pathology budget", "Tissue adequacy", "Possible conflict of interest perception (AZ is a sponsor): use guideline-based panels"],
 priority={"impact":"Medium-High","effort":"Low"})

add(id="C3", title="Fixed weekly MDT slots with pre-reserved treatment-start capacity",
 bottleneck="diagnosis_to_treatment", pathway_step="Diagnosis complete → MDT decision → surgery/oncology slot",
 problem="Norway found the decision→treatment interval to be the main delay. THL issued 2025 guidance on cancer MDT meetings (THL21 annex 2).",
 action="Schedule MDTs weekly per tumour group (remote participation for regional hospitals). Each MDT ends with a booked treatment date. Keep 'pathway' surgical/oncology slots that are released if unused 72 h ahead.",
 owners=["Surgery and oncology unit heads", "MDT coordinators", "Theatre planning"],
 effort="Medium", cost_estimate="ESTIMATE: capacity reallocation, not new money. Risk of idle slots (cost unknown).",
 kpis=[{"name":"Treatment decision → first treatment ≤ target; % ≤6 wk overall","type":"goal3","ref":"G3-3"}],
 expected_effect="Targets the step Norway identified as the main delay. No verified effect size for slot reservation itself.",
 evidence=[ev("Decision→treatment main source of delay for all cancers studied (Norway)", "NILSSEN22"),
           ev("THL time-points guidance incl. 2025 annex on multidisciplinary planning meetings", "THL21", "Liite 2 (2025)"),
           ev("Adjuvant therapy should start ≤4 weeks after surgery", "THL21", "printed p.13")],
 goal3_mapping=["G3-3"], goal2_secondary=[],
 roadmap_actions=["3.1.2 (p.56–57)","Huonon ennusteen syövät: hoitoketjut ja yhteistyö (p.24)"],
 first_90_days=["Wk 1–4: map current MDT cadence and decision→treatment days (from C1)", "Wk 5–13: pilot in one tumour group"],
 risks=["Crowding out of benign surgery (Olsson 2020)"],
 priority={"impact":"Medium","effort":"Medium"})

add(id="C4", title="Bring treatment and follow-up closer to home for remote residents (remote visits, shared care with local hospitals)",
 bottleneck="diagnosis_to_treatment", pathway_step="Treatment start/continuation for patients living far from the centre",
 problem="Outcomes are worse beyond 50 km from the treatment unit, and palliative radiotherapy use is lower beyond 100 km (ROAD p.13). Norway: travelling outside the home trust prolonged waits.",
 action="Use remote oncology visits and give oral therapy and follow-up in the nearest hospital or health centre where clinically safe. Arrange patient travel at the time of the MDT.",
 owners=["Oncology unit", "Local hospitals/health centres", "Kela travel coordination", "ICT (remote visits)"],
 effort="Medium", cost_estimate="ESTIMATE: offset partly by lower travel reimbursement (not quantified).",
 kpis=[{"name":"% treated ≤6 wk by distance band","type":"goal3","ref":"G3-3"},{"name":"Mortality gap by area","type":"goal3","ref":"G3-2"}],
 expected_effect="Equity effect for remote areas. Magnitude unverified.",
 evidence=[ev("Worse outcomes >50 km; less palliative RT >100 km; recommends remote/decentralised care", "ROAD", "p.13"),
           ev("Travelling outside the resident health trust prolonged waiting time", "NILSSEN22")],
 goal3_mapping=["G3-3","G3-2"], goal2_secondary=[],
 roadmap_actions=["3.5.3 (p.73–74)","Alueellinen eriarvoisuus (p.12–13)"],
 first_90_days=["Wk 1–6: identify patients >100 km in C1 data", "Wk 7–13: remote-visit pilot for follow-ups"],
 risks=["Safety of decentralised therapy needs local competence"],
 priority={"impact":"Medium","effort":"Medium"})

# national-level (not county-start) noted separately
add(id="N1", title="(National, supportive) Symptom-awareness campaign targeting groups with delayed help-seeking",
 bottleneck="late_detection", pathway_step="Symptom → first contact",
 problem="Rural residents are diagnosed at a later stage and seek care more slowly (ROAD p.12).",
 action="The county joins the national FICAN/Cancer Society campaign (roadmap 1.3.2) with local channels in low-uptake areas.",
 owners=["FICAN, Cancer Society (national)", "County communications"], effort="Low (for county)",
 cost_estimate="National: €400,000 (ROAD p.34). County: staff time.",
 kpis=[{"name":"Cancer mortality −10% (long-term)","type":"goal3","ref":"G3-2"},{"name":"70% stage I–II (Goal 2, secondary)","type":"goal2","ref":"STRAT p.5"}],
 expected_effect="NOT VERIFIED by us. The roadmap cites UK Be Clear on Cancer as a model, but we did not fetch an effect study.",
 evidence=[ev("Roadmap 1.3.2 national symptom-awareness plan modelled on Be Clear on Cancer", "ROAD", "p.34")],
 goal3_mapping=["G3-2"], goal2_secondary=["70% stage I–II"], roadmap_actions=["1.3.2 (p.34)"],
 first_90_days=["Coordinate with FICAN; no county launch before national plan (2026–2028)"],
 risks=["Increases demand on primary care", "Effect evidence not verified"], priority={"impact":"Low-Medium","effort":"Low"})

import sys; sys.path.insert(0, HERE)
from top3_defs import top_items, OUTDATED
for r in R:
    r.update(top3=False, priority_rank=None, nonpriority=True, optional_goal2=False, owner_role=None, cost_range=None, stop_go=None, already_exists=None, kpi_framing=None, pilot_county=None, data_basis=[])
TOP = top_items(ev, NAV_COST)
for t in TOP: t["nonpriority"] = False
R = TOP + R
for r in R:
    r["project"] = "Tasan"
    r["goal3_indicators_text"] = [G3[g] for g in r["goal3_mapping"]]
    assert r["goal3_mapping"], r["id"]

doc = {"project": "Tasan", "hero_gap": "Lung cancer: diagnosis→treatment time and curative-treatment share vary by region (Goal 3: G3-3, G3-1)", "top3_ids": [t["id"] for t in TOP if t["top3"]], "optional_goal2_ids": [t["id"] for t in TOP if t.get("optional_goal2")], "target_times_caveat": OUTDATED, "generated": "2026-11-14", "author": "JN Care Strategist",
       "note": "Longlist. All cost figures marked ESTIMATE are our reasoning, not sourced prices. Page refs: STRAT=strategy PDF, ROAD=roadmap PDF.",
       "goal3_indicators": G3, "sources": {k: {"title": v[0], "url": v[1]} for k, v in S.items()},
       "bottlenecks": {"late_detection": "Late detection", "referral": "Primary → specialist referral", "diagnosis_to_treatment": "Diagnosis → treatment"},
       "recommendations": R}
json.dump(doc, open(os.path.join(OUT, "recommendations.json"), "w"), ensure_ascii=False, indent=2)

# markdown longlist
L = []
for b, bn in doc["bottlenecks"].items():
    L.append(f"\n## Bottleneck: {bn}\n")
    for r in [x for x in R if x["bottleneck"] == b and x.get("nonpriority")]:
        L.append(f"### {r['id']}. {r['title']}\n")
        L.append(f"*Tags:* `bottleneck={b}` `goal3={','.join(r['goal3_mapping'])}` `impact={r['priority']['impact']}` `effort={r['priority']['effort']}`\n")
        L.append(f"- **Pathway step:** {r['pathway_step']}\n- **Problem:** {r['problem']}\n- **Action:** {r['action']}")
        L.append(f"- **Who does what:** " + "; ".join(r['owners']))
        L.append(f"- **Effort / cost:** {r['effort']}. {r['cost_estimate']}")
        L.append("- **KPIs moved:** " + "; ".join(f"{k['name']} [{k['type']}: {k['ref']}]" for k in r['kpis']))
        L.append(f"- **Expected effect:** {r['expected_effect']}")
        L.append("- **Evidence:**")
        for e in r['evidence']:
            L.append(f"  - {e['claim']}. [{e['source_title']}]({e['url']})")
        L.append("- **Goal 3 mapping:** " + "; ".join(r['goal3_indicators_text']) + (f" · *Goal 2 (secondary):* {', '.join(r['goal2_secondary'])}" if r['goal2_secondary'] else ""))
        L.append("- **Roadmap actions:** " + "; ".join(r['roadmap_actions']))
        L.append("- **First 90 days:** " + " → ".join(r['first_90_days']))
        L.append("- **Risks / limitations:** " + "; ".join(r['risks']) + "\n")
head = open(os.path.join(HERE, "summary_head.md")).read()
open(os.path.join(OUT, "recommendations.md"), "w").write(head + "\n" + "\n".join(L) + "\n")
json.dump({k: doc[k] for k in ("project","hero_gap","top3_ids","optional_goal2_ids","target_times_caveat","goal3_indicators")} | {"items": TOP, "sources": {k: doc["sources"][k] for k in sorted({e["source_id"] for t in TOP for e in t["evidence"]} | {"KT25","KTSIVU","KYMJOHTO","KYMLUNG","LAPORG","LAPSYOPA","OYSLUNG","POHDE","FILHA26","HUSKYM"})}}, open(os.path.join(OUT, "top3.json"), "w"), ensure_ascii=False, indent=2)
print(len(R), "recommendations written;", len(TOP), "priority items")
exec(open(os.path.join(HERE, "gen_top3_md.py")).read())
exec(open(os.path.join(HERE, "gen_pilot_brief.py")).read())
