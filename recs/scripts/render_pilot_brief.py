#!/usr/bin/env python3
"""Render a Tasan one-page pilot brief (markdown, optional PDF) from a JSON file
that follows recs/pilot_brief_template.json.

Usage: render_pilot_brief.py <brief.json> [--pdf]
Writes <brief>.md next to the JSON; with --pdf also <brief>.pdf (needs weasyprint + markdown).
"""
import json, sys, os

def eur(x): return f"€{x:,.0f}"

def render(d):
    L = []
    L.append(f"**{d['status_label']}**  \n")
    L.append(f"# {d['title']}\n")
    p = d["problem"]
    L.append(f"**Problem.** {p['line']} {p['metric']} *Source:* {p['source']}. *Caveat:* {p['caveat']}"
             + (f" {p['people_estimate']}" if p.get("people_estimate") else "") + "\n")
    a = d["action"]
    L.append(f"**Action.** {a['summary']}\n")
    for c in a.get("components", []): L.append(f"- {c}")
    L.append("")
    L.append("**Owners (roles only).** " + "; ".join(o['role'] + (f" ({o['verified']}: {o['source']})" if o.get('source') else f" ({o['verified']})") for o in d["owners"]) + ".\n")
    c = d["cost_range"]
    L.append(f"**Cost.** {eur(c['low_eur'])}–{eur(c['high_eur'])} for {c['period']}. *Basis:* {c['basis']} "
             f"*Sources:* {'; '.join(c['sources'])}. {c.get('excludes','')}\n")
    L.append("**KPIs** (D = Tasan design choice)\n")
    L.append("| KPI | Baseline | Target | D |\n|---|---|---|---|")
    for k in d["kpis"]:
        L.append(f"| {k['name']} | {k['baseline_method']} | {k['target']} | {'yes' if k['design_choice'] else 'no'} |")
    L.append("")
    L.append(f"*{d['kpi_caveat']}*\n")
    if d.get("timeline"): L.append("**90 days.** " + " ".join(d["timeline"]) + "\n")
    s = d["stop_go"]
    L.append(f"**Day-90 stop/go** ({s['decider']}). {s['go']} {s['stop']}\n")
    z = d["az_role"]
    L.append(f"**AstraZeneca's role (compliance-safe).** {z['summary']} *Framework:* {z['compliance_framework']} {z['compliance_source']}. {z.get('note','')}\n")
    for pr in d.get("precedents", []):
        L.append(f"**Precedent.** {pr['name']} ({pr['date']}): {pr['description']} {pr['source']}\n")
    if d.get("caveats"): L.append("**Caveats.** " + " ".join(d["caveats"]) + "\n")
    L.append(f"**Signature** — {d['signer']['role']}: ______________________  Date: ________  \n")
    L.append(f"*{d['status_label']}* Prepared {d['date_prepared']} by the Tasan team (Junction 2026).")
    return "\n".join(L) + "\n"

CSS = """@page{size:A4;margin:11mm 12mm}
body{font-family:'DejaVu Sans',Arial,sans-serif;font-size:8.6pt;line-height:1.25;color:#111}
h1{font-size:14pt;margin:2px 0 4px}
p{margin:0 0 3.5px} ul{margin:0 0 3px 13px;padding:0} li{margin:0}
table{border-collapse:collapse;width:100%;margin:1px 0 3px}
td,th{border:1px solid #999;padding:1px 3px;text-align:left;vertical-align:top}
th{background:#eee} a{color:#111;text-decoration:none}"""

def to_pdf(md_text, out):
    import markdown
    from weasyprint import HTML
    html = markdown.markdown(md_text, extensions=["tables"])
    HTML(string=f"<html><head><meta charset='utf-8'><style>{CSS}</style></head><body>{html}</body></html>").write_pdf(out)

if __name__ == "__main__":
    src = sys.argv[1]
    d = json.load(open(src, encoding="utf-8"))
    assert d.get("status") == "draft", "only drafts may be rendered"
    assert "name" not in d.get("signer", {}) and all("name" not in o for o in d.get("owners", [])), "roles only, no personal names"
    md = render(d)
    base = os.path.splitext(src)[0]
    open(base + ".md", "w", encoding="utf-8").write(md)
    print("wrote", base + ".md")
    if "--pdf" in sys.argv:
        to_pdf(md, base + ".pdf"); print("wrote", base + ".pdf")
