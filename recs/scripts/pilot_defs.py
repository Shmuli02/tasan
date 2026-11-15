# Owners, sourced cost ranges and day-90 stop/go for Tasan T3/T1/T2 (+G2-1). Imported by build_recs.py.
# RULE (RECS_REVIEW fix 4): every euro figure is computed from a fetched source. Anything without a source
# is given as effort only (hours/FTE) and marked "unsourced, euro figure dropped".
SIVU = 0.2314                      # employer contributions, wellbeing sector 2026 = 23.14 % (KT, Henkilöstökulut page)
NURSE_TASK, NURSE_TOT = 3174, 4048 # sairaanhoitaja €/month, Oct 2025: task-based pay / total earnings (KT hyvinvointialan palkat 2025)
AN_TASK, AN_TOT = 4663, 4891       # analyytikko €/month, Oct 2025 (same table)
K = 1 + SIVU
NY = (round(12*NURSE_TASK*K), round(12*NURSE_TOT*K))   # nurse FTE-year, low = task pay, high = total earnings
AM = (round(AN_TASK*K), round(AN_TOT*K))                 # analyst FTE-month

SRC = ("Sources: KT Kunta- ja hyvinvointialuetyönantajat, 'Hyvinvointialan palkkatilastot' Oct 2025 "
       "(https://www.kt.fi/tilastot-ja-julkaisut/hyvinvointialan-palkat): sairaanhoitaja task-based €3,174 / total €4,048 per month; "
       "analyytikko €4,663 / €4,891. Employer contributions 23.14% (KT 'Henkilöstökulut', 2026: https://www.kt.fi/tilastot-ja-julkaisut/henkilostokulut). "
       "Range = task-based pay (low) to total earnings incl. all supplements (high), × 12 × 1.2314. Oct 2025 pay with 2026 contribution rates; later pay rises are not included.")

def ln(item, fte, months, per_year=None, per_month=None):
    if per_year: lo, hi = round(fte*per_year[0]*months/12), round(fte*per_year[1]*months/12)
    else: lo, hi = round(fte*per_month[0]*months), round(fte*per_month[1]*months)
    return {"item": item, "low": lo, "high": hi, "basis": f"{fte} FTE × {months} months"}

def cost(lines, period, unsourced):
    return {"low": sum(l["low"] for l in lines), "high": sum(l["high"] for l in lines), "currency": "EUR", "period": period,
            "basis": [f"{l['item']}: €{l['low']:,}–€{l['high']:,} ({l['basis']})" for l in lines] + [SRC]
                     + [f"Unsourced, euro figure dropped: {u}" for u in unsourced],
            "lines": lines, "unsourced_effort": list(unsourced)}

V = "role holder verified on the county's website, 14 Nov 2026"
NV = "role exists by function; role holder not verified"

def pilot_fields():
    P = {}
    P["T3"] = dict(
      owner_role={"signer": "Johtajaylilääkäri (chief medical officer) of the pilot county",
                  "owner_of_delayed_patients": "Named nurse navigator (1 FTE), line-managed by the county's chief nursing officer",
                  "data_owner": "County knowledge-management / analytics unit (" + NV + ")",
                  "partners": ["ICT / EHR vendor contact for date extraction", "County board (monthly review)"],
                  "by_county": {
                    "Kymenlaakso": {"signer": "Johtajaylilääkäri / Chief Medical Officer, Kymenlaakso wellbeing services county (Kymenhva) (" + V + ")",
                                    "owner_of_delayed_patients": "Nurse navigator, line-managed by the Johtajaylihoitaja / Chief Nursing Officer, Kymenhva (" + V + ")",
                                    "data_owner": "Kymenhva analytics unit (" + NV + ")"},
                    "Lapland": {"signer": "Johtajaylilääkäri / Chief Medical Officer, Lapland wellbeing services county (Lapin hyvinvointialue) (" + V + ")",
                                "owner_of_delayed_patients": "Nurse navigator, line-managed by the vs. hoitotyön johtaja / Acting Director of Nursing, Lapin hyvinvointialue (" + V + ")",
                                "data_owner": "Lapland analytics unit (" + NV + ")"}}},
      cost_range=cost([ln("Nurse navigator", 1.0, 3, per_year=NY), ln("Analyst (EHR/Hilmo extraction, 12-month baseline, weekly feed)", 0.5, 3, per_month=AM)],
                      "90-day pilot, per county",
                      ["dashboard integration with the county EHR/BI platform (no quote obtained; the Tasan prototype is reused)"]),
      stop_go={"review_day": 90, "decision_owner": "Johtajaylilääkäri of each county",
               "go_if_all": ["≥85% of lung-cancer pathways have all 4 THL 21/2016 time points (referral arrival, first visit, queue date, first treatment)",
                             "The county's own 12-month baseline (% ≤42 days from referral arrival; median per step) is presented to the county board",
                             "≥90% of day-28 alerts are actioned by the navigator within 2 working days",
                             "The navigator contacts ≥90% of new suspected-lung-cancer patients within 3 working days of referral arrival"],
               "stop_or_redesign_if_any": ["Time-point completeness <70% after one fix cycle: pause the dashboard and fix recording first"],
               "else": "Extend by 90 days with one named fix",
               "note": "Thresholds (85/90/70%, day 28, 3 days) are Tasan design choices, not official targets."})
    P["T1"] = dict(
      owner_role={"signer": "Johtajaylilääkäri / Chief Medical Officer, Kymenlaakso wellbeing services county (Kymenhva) (" + V + ")",
                  "operational_sponsor": "Hallintoylilääkäri, erikoissairaanhoito / Administrative Chief Physician, specialised care, Kymenhva (" + V + ")",
                  "clinical_lead": "Ylilääkäri, pulmonology (keuhkosairauksien yksikkö), Kymenlaakson keskussairaala, Kotka (" + NV + ")",
                  "partners": ["HUS thoracic surgery, Meilahti: per kymenhva.fi the surgery decision and operation for Kymenlaakso patients are made there; one named HUS counterpart for slots (" + NV + ")",
                               "Kymenhva multidisciplinary lung meeting (moniammatillinen keuhkokokous), which already exists per kymenhva.fi",
                               "HUS operates the laboratory at Kymenlaakso central hospital (hus.fi). Which unit runs lung pathology and biomarkers is to be confirmed in week 1"]},
      cost_range=cost([ln("Pathway coordinator nurse (if the week-1 map shows no one owns the clock; otherwise covered by the T3 navigator)", 0.5, 3, per_year=NY)],
                      "90-day pilot, CONDITIONAL (only if the week-1 map shows no one owns the clock; otherwise the T3 navigator covers it, and T1's base staff cost is €0)",
                      ["set-up physician time, est. 40–80 hours for SOPs (no sourced hourly tariff)",
                       "extra CT/EBUS lists, if the map shows a capacity gap (no tariff obtained)",
                       "reflex biomarker panel price (no public price; most tests are moved earlier, not added)"]),
      stop_go={"review_day": 90, "decision_owner": "Johtajaylilääkäri, Kymenhva",
               "go_if_all": ["The missing step(s) found on the week-1 pathway map are in place (e.g. CT ≤3 working days, reflex panel SOP, pre-agreed HUS slots)",
                             "≥20 suspected-lung-cancer patients through the redesigned pathway",
                             "Median referral → treatment decision ≥7 days shorter than the county's own baseline (from T3, days 1–30)",
                             "Waits for non-pathway CT not more than 10% longer than in the same months last year (crowding-out check)"],
               "stop_or_redesign_if_any": ["<10 patients through the pathway", "Median referral→decision improved by <3 days", "Non-pathway CT waits up >20%"],
               "else": "Extend by 90 days with one named fix",
               "note": "Thresholds are Tasan design choices."})
    P["T2"] = dict(
      owner_role={"signer": "Johtajaylilääkäri / Chief Medical Officer, Lapland wellbeing services county (Lapin hyvinvointialue) (" + V + ")",
                  "operational_sponsor": "Somaattisen erikoissairaanhoidon johtaja / Director of Somatic Specialised Care, Lapin hyvinvointialue (" + V + ")",
                  "clinical_lead": "Head of pulmonology (keuhkosairauksien ylilääkäri), Lapin keskussairaala, Rovaniemi (" + NV + ")",
                  "partners": ["OYS lung-cancer MDT lead: NOT VERIFIED from public sources (checked oys.fi, pohde.fi, oulu.fi, Filha on 14 Nov 2026). To be identified and confirmed in week 1 (gate). Per oys.fi, the university hospital is responsible for lung-cancer MDTs, surgery and radiotherapy",
                               "OYS radiotherapy lead: NOT VERIFIED (same check). Accountable line: service-area director for cancer care, OYS (palvelualuejohtaja, OYS Sisätaudit, syöpähoito ja infektiontorjunta), role per https://pohde.fi/tietoa-meista/pohjois-pohjanmaan-hyvinvointialue/hyvinvointialueen-palvelut/sote-palvelut/oys-sairaalapalvelujen-ja-ensihoidon-toimialue/ and the Pohde news of 25.6.2025, checked 14 Nov 2026",
                               "Respiratory medicine entry point: physician-in-chief, respiratory medicine, OYS (not confirmed as MDT lead); role holder verified on the University of Oulu researcher profile (oulu.fi), 14 Nov 2026",
                               "Johtajaylilääkäri / Chief Medical Officer, North Ostrobothnia wellbeing services county (Pohde) co-signs for the OYS side (role holder verified on the pohde.fi committee list 2025–2029, 14 Nov 2026)",
                               "FICAN North (director, OYS, per the Filha Keuhkosyöpäpäivä 27.11.2026 programme)",
                               "Lapland cancer patients receive radiotherapy at OYS (lapha.fi)",
                               "Kela (travel reimbursement) and the OYS patient hotel (accommodation), booked by the T3 navigator"]},
      cost_range=cost([ln("MDT list coordinator nurse (case list, images, minutes)", 0.3, 3, per_year=NY)],
                      "90-day pilot",
                      ["MDT physician time, est. 0.75–1.5 physician-hours per case × ~36 cases per quarter (no sourced hourly tariff)",
                       "baseline audit, est. 16–32 physician-hours",
                       "video/PACS link (assumed to exist; not priced)"]),
      stop_go={"review_day": 90, "decision_owner": "Johtajaylilääkäri, Lapin hyvinvointialue, with the OYS MDT lead",
               "week1_gate": "By day 7, the OYS lung-cancer MDT lead and the OYS radiotherapy lead are identified and confirm in writing that they will take part (MDT listing rule + video slot). If not confirmed by day 14: STOP the T2 arm and continue T3 only in Lapland.",
               "go_if_all": ["Week-1 gate passed (OYS MDT and RT leads confirmed)", "≥90% of new Lapland lung cancers listed at the existing OYS MDT before the treatment-intent decision (or ≥20 pp above the week-1 audited baseline)",
                             "Median histology → MDT ≤7 days, and listing does not add >7 days to the treatment decision",
                             "Performance/frailty fields (ECOG, G8/CFS) completed in ≥80% of listed cases",
                             "A sized proposal for the curative-RT access arm (slot quota, travel, accommodation) is agreed with the OYS RT lead (design, unpriced)"],
               "stop_or_redesign_if_any": ["OYS leads not confirmed by day 14", "Coverage <70% at day 90", "Listing adds >14 days median to the decision"],
               "else": "Extend by 90 days with one named fix",
               "note": "Curative share cannot be judged at day 90 (registry lag). Thresholds are Tasan design choices."})
    P["G2-1"] = dict(
      owner_role={"signer": "Screening programme lead of each county (Helsinki; Kymenhva) (" + NV + ")"},
      cost_range={"low": None, "high": None, "currency": "EUR", "period": "one screening round",
                  "basis": ["Unsourced, euro figure dropped: postage/SMS per non-responding man"], "unsourced_effort": ["postage/SMS"]},
      stop_go={"review_day": 90, "go_if_all": ["Return rate among reminded men ≥ +2 pp vs the matched previous round"], "stop_or_redesign_if_any": ["No measurable difference"]})
    return P
