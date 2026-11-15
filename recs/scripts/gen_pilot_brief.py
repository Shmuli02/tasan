import json, os
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.dirname(HERE)
t=json.load(open(os.path.join(OUT,"top3.json"))); I={r["id"]: r for r in t["items"]}
f=lambda x: f"€{x:,}"
T3c, T1c, T2c = I["T3"]["cost_range"], I["T1"]["cost_range"], I["T2"]["cost_range"]
PAY=[b for b in T3c["basis"] if b.startswith("Sources:")][0]
OWN={
 "Kymenlaakso": ["**Signer:** Johtajaylilääkäri / Chief Medical Officer, Kymenlaakso wellbeing services county (Kymenhva) (role holder verified on kymenhva.fi, 14 Nov 2026)",
                 "**Operational sponsor (T1):** Hallintoylilääkäri, erikoissairaanhoito / Administrative Chief Physician, specialised care, Kymenhva (role holder verified on kymenhva.fi, 14 Nov 2026)",
                 "**Owner of delayed patients (T3):** nurse navigator, line-managed by the Johtajaylihoitaja / Chief Nursing Officer, Kymenhva (role holder verified on kymenhva.fi, 14 Nov 2026)",
                 "**Clinical lead (T1):** ylilääkäri, pulmonology unit, Kymenlaakson keskussairaala, Kotka (name not verified)",
                 "**Data owner (T3):** Kymenhva analytics unit (name not verified)",
                 "**Partners:** HUS Meilahti thoracic surgery (one named slot counterpart, to be agreed); the existing Kymenhva multidisciplinary lung meeting; the HUS-operated laboratory at Kymenlaakso central hospital (lung pathology role to confirm)"],
 "Lapland": ["**Signer:** Johtajaylilääkäri / Chief Medical Officer, Lapland wellbeing services county (Lapin hyvinvointialue) (role holder verified on lapha.fi, 14 Nov 2026)",
             "**Operational sponsor (T2):** Somaattisen erikoissairaanhoidon johtaja / Director of Somatic Specialised Care, Lapin hyvinvointialue (role holder verified on lapha.fi, 14 Nov 2026)",
             "**Owner of delayed patients (T3):** nurse navigator, line-managed by the vs. hoitotyön johtaja / Acting Director of Nursing, Lapin hyvinvointialue (role holder verified on lapha.fi, 14 Nov 2026)",
             "**Clinical lead (T2):** keuhkosairauksien ylilääkäri, Lapin keskussairaala, Rovaniemi (name not verified)",
             "**Data owner (T3):** Lapland analytics unit (name not verified)",
             "**OYS partners (week-1 gate):** the OYS lung-cancer MDT lead and OYS radiotherapy lead are NOT VERIFIED from public sources (oys.fi, pohde.fi, oulu.fi, Filha, checked 14 Nov 2026). Entry points: service-area director for cancer care, OYS (palvelualuejohtaja, OYS Sisätaudit, syöpähoito ja infektiontorjunta) (pohde.fi); physician-in-chief, respiratory medicine, OYS (not confirmed as MDT lead) (oulu.fi). Co-signer for OYS: Johtajaylilääkäri / Chief Medical Officer, North Ostrobothnia wellbeing services county (Pohde) (pohde.fi)"]}
WHY={"Kymenlaakso": "591 lung cancers diagnosed in 2019–2023, about 118 a year (Keuhkosyöpä Suomessa 2019–2023, Taulukko 11). The surgery decision and the operation are made at HUS Meilahti (kymenhva.fi), so hand-offs to another organisation are part of every surgical pathway. Crude curative-record share 19.3% (16.3–22.7) vs 27.0% nationally; age-standardised (chart-digitised) men ≈18.0%, women ≈22.7%. No county-level time data exist, so T3 measures them.",
     "Lapland": "Age-standardised curative share (chart-digitised, R2026 Kuva 16): men ≈16.2% (12.7–20.4) vs Vantaa-Kerava ≈29.8% (24.2–36.1); women ≈23.1% (17.9–29.0) vs ≈39.7% (33.1–47.0). Men's surgery share is equal (9.1% vs 9.0%, R2024 Taulukko 3.7), so the gap is likely in curative radiotherapy, which is given at OYS (our inference). Not adjusted for stage or fitness."}
COST={"Kymenlaakso": [f"**Base (T3): {f(T3c['low'])}–{f(T3c['high'])}** for 90 days: 1.0 FTE nurse navigator + 0.5 FTE analyst.",
                      f"*Conditional:* {f(T3c['low']+T1c['low'])}–{f(T3c['high']+T1c['high'])} only if the week-1 map shows that T1 needs its own 0.5 FTE pathway coordinator ({f(T1c['low'])}–{f(T1c['high'])}). Otherwise the T3 navigator covers it.",
                      "No euro figure (unsourced): T1 set-up physician hours (est. 40–80 h), extra CT/EBUS lists, reflex biomarker panel price, dashboard integration."],
      "Lapland": [f"**Base (T3 + T2): {f(T3c['low']+T2c['low'])}–{f(T3c['high']+T2c['high'])}** for 90 days: T3 {f(T3c['low'])}–{f(T3c['high'])} (1.0 FTE navigator + 0.5 FTE analyst) + T2 {f(T2c['low'])}–{f(T2c['high'])} (0.3 FTE MDT list coordinator).",
                  "No euro figure (unsourced): MDT physician hours (est. 0.75–1.5 h per case × ~36 cases), baseline audit (16–32 h), video/PACS, dashboard integration.",
                  "Not costed, design only: the curative-RT access arm (slot quota, travel, accommodation). It is sized with the OYS RT lead after the week-1 gate."]}
COUNTIES=[("Kymenlaakso","Kymenlaakson hyvinvointialue (Kymenhva)",["T3","T1"],"Johtajaylilääkäri / Chief Medical Officer, Kymenlaakso wellbeing services county (Kymenhva)",""),
          ("Lapland","Lapin hyvinvointialue",["T3","T2"],"Johtajaylilääkäri / Chief Medical Officer, Lapland wellbeing services county (Lapin hyvinvointialue)","")]
DRAFT="> ## ⚠ DRAFT – not signed\n> Draft for discussion. Nothing has been sent to, discussed with or agreed by either county or OYS."
L=["# Tasan pilot brief: one page per county", "", DRAFT, "",
   "*JN Care Strategist, 14 Nov 2026 (Helsinki time). Generated from `top3.json` by `scripts/gen_pilot_brief.py`, so do not hand-edit. Office-holders were checked on the counties' public websites on 14 Nov 2026.*", "",
   "**Common rules.** T3 (the Tasan clock) starts first and measures each county's own baseline in days 1–30, including a registry-completeness check. T1 and T2 are the actions the clock triggers. Every target is a proposed peer benchmark or a Tasan design choice, not a promised effect. **Target-time caveat:** the 42-day reference is THL Ohjaus 21/2016 §4.1: marked outdated, with no lung-specific limit. New cancer-specific targets are due 2026–2028 (roadmap 3.1.2, p.57). Day-28 and 80% are Tasan design choices.", ""]
for name, org, ids, who, title in COUNTIES:
    L += ["---", "", f"## {name}: {org}", "", DRAFT, ""]
    L.append("**Scope (90 days):** " + " + ".join(f"{i} {I[i]['title']}" for i in ids) + ". Lung cancer (C33–C34) patients resident in the county.\n")
    L.append("**Why this county:** " + WHY[name])
    L.append("**This already exists?** " + I[ids[1]]["already_exists"] + "\n")
    L.append("**Owners (this county only):**"); L += [f"- {x}" for x in OWN[name]]
    if name=="Lapland": L.append(f"\n**Week-1 gate (T2):** {I['T2']['stop_go']['week1_gate']}")
    L.append("\n**90-day plan:**")
    for i in ids:
        for s in I[i]["first_90_days"]: L.append(f"- {i} · {s}")
    L.append("\n**Cost range (sourced staff cost only):**"); L += [f"- {x}" for x in COST[name]]
    L.append("- Pay " + PAY[0].lower() + PAY[1:])
    L.append("\n**KPIs:**\n\n| | KPI | Baseline | Target |\n|---|---|---|---|")
    for i in ids:
        for k in I[i]["kpis"]: L.append(f"| {i} | {k['name']} | {k.get('baseline','')} | {k.get('target','')} |")
    des=[d for i in ids for d in I[i].get("design",[])]
    if des:
        L.append("\n**Design column (not KPIs, not costed):**"); L += [f"- {d}" for d in des]
    L.append("\n**Day-90 stop/go:**")
    for i in ids:
        sg=I[i]["stop_go"]
        L.append(f"- **{i} GO** if all: " + "; ".join(sg["go_if_all"]) + ".")
        L.append(f"- **{i} STOP/redesign** if any: " + "; ".join(sg["stop_or_redesign_if_any"]) + f". Otherwise: {sg.get('else','extend 90 days')}.")
    L.append("\n*Thresholds are Tasan design choices. 42 days follows THL 21/2016 (outdated, no lung-specific limit, cancer-specific targets due 2026–28).*\n")
    L.append("**DRAFT – not signed. Approval for a 90-day pilot:**\n")
    L.append(f"Signature: ______________________  Role: {who}  Date: ____ / ____ / 2026\n")
    if name=="Lapland":
        L.append("Co-signature, OYS side: ______________________  Johtajaylilääkäri / Chief Medical Officer, North Ostrobothnia wellbeing services county (Pohde)  Date: ____ / ____ / 2026\n")
open(os.path.join(OUT,"pilot_brief.md"),"w").write("\n".join(L))
print("pilot_brief.md written")
