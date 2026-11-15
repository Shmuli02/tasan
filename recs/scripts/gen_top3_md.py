import json, os
HERE=os.path.dirname(os.path.abspath(__file__)); OUT=os.path.dirname(HERE)
t=json.load(open(os.path.join(OUT,"top3.json")))
L=[open(os.path.join(HERE,"top3_head.md")).read()]
def eur(c):
    return "unsourced, euro figure dropped" if c["low"] is None else f"€{c['low']:,}–€{c['high']:,} ({c['period']})"
for r in t["items"]:
    tag = "TOP 3 · #%d" % r["priority_rank"] if r["top3"] else "OPTIONAL · Goal 2 (secondary)"
    L.append(f"\n## {r['id']}. {r['title']}  \n*{tag} · Pilot: **{r['pilot_county']}** · Goal 3: {', '.join(r['goal3_mapping'])}*\n")
    L.append(f"**\"This already exists\":** {r['already_exists']}\n")
    L.append(f"**Problem:** {r['problem']}\n\n**Action:** {r['action']}\n")
    L.append("**Owner (named roles):**")
    for k,v in r["owner_role"].items():
        if isinstance(v,dict):
            for cty,o in v.items():
                L.append(f"- **{cty}:** " + "; ".join(f"{a.replace('_',' ')}: {b}" for a,b in o.items()))
        elif isinstance(v,list):
            for x in v: L.append(f"- partner: {x}")
        else: L.append(f"- {k.replace('_',' ')}: {v}")
    c=r["cost_range"]
    L.append(f"\n**Cost range:** {eur(c)}")
    for b in c["basis"]: L.append(f"- {b}")
    L.append("\n| KPI | Type | Baseline | Target |\n|---|---|---|---|")
    for k in r["kpis"]:
        L.append(f"| {k['name']} | {k['type']} {k['ref']} | {k.get('baseline','')} | {k.get('target','')} |")
    if r.get("design"):
        L.append("\n**Design column (not KPIs, not costed):**")
        for x in r["design"]: L.append(f"- {x}")
    L.append(f"\n**KPI framing:** {r['kpi_framing']}\n")
    sg=r["stop_go"]
    if sg.get("week1_gate"): L.append(f"**Week-1 gate:** {sg['week1_gate']}\n")
    L.append(f"**Day-{sg['review_day']} stop/go** (decides: {sg.get('decision_owner','county')}). GO if all of:")
    for x in sg["go_if_all"]: L.append(f"- {x}")
    L.append("STOP or redesign if any of: " + "; ".join(sg["stop_or_redesign_if_any"]) + (f". Otherwise: {sg['else']}." if sg.get("else") else "."))
    if sg.get("note"): L.append(f"*{sg['note']}*")
    L.append("\n**Data basis:**")
    for x in r["data_basis"]:
        L.append(f"- {x['fact']} ({x['source']}, {x['url']}; `{x['csv']}`; *{x['verified']}*)")
    L.append(f"\n**Expected effect:** {r['expected_effect']}\n\n**Evidence:**")
    for e in r["evidence"]: L.append(f"- {e['claim']}. [{e['source_title']}]({e['url']})")
    L.append("\n**Roadmap actions:** " + "; ".join(r["roadmap_actions"]))
    L.append("\n**First 90 days:**")
    for s in r["first_90_days"]: L.append(f"1. {s}")
    L.append("\n**Risks:** " + " · ".join(r["risks"]) + "\n")
L.append(open(os.path.join(HERE,"top3_tail.md")).read())
open(os.path.join(OUT,"top3.md"),"w").write("\n".join(L))
print("top3.md written")
