#!/usr/bin/env python3
"""Render a Tasan one-page pilot brief (markdown, optional PDF) from a JSON file
that follows recs/pilot_brief_template.json.

Usage: render_pilot_brief.py <brief.json> [--pdf]
Writes <brief>.md next to the JSON; with --pdf also <brief>.pdf (designed A4 layout, page 2 = appendix if set; needs Google Chrome/Chromium).
"""
import json, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

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

def to_pdf(d, base, src_dir):
    """Designed A4 PDF via brief_pdf (headless Chrome). """
    from brief_pdf import to_html, html_to_pdf
    appendix = None
    if d.get("appendix"):
        ap = os.path.join(src_dir, d["appendix"])
        if os.path.exists(ap):
            appendix = open(ap, encoding="utf-8").read()
    import tempfile
    with tempfile.NamedTemporaryFile("w", suffix=".html", encoding="utf-8", delete=False) as f:
        f.write(to_html(d, appendix))
    try:
        html_to_pdf(f.name, base + ".pdf")
    finally:
        os.unlink(f.name)

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
        to_pdf(d, base, os.path.dirname(os.path.abspath(src))); print("wrote", base + ".pdf")
