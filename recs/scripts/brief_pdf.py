"""Designed HTML/PDF layout for Tasan pilot briefs (brand: tasan-tokens.css).

to_html(d, appendix_md=None) -> HTML string (A4, page 1 = the one-page ask,
optional page 2 = conditional appendix rendered from markdown).
html_to_pdf(html_path, pdf_path) prints it with headless Chrome/Chromium.
"""
import html, os, re, shutil, subprocess, tempfile

ASSETS = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
URL_RE = re.compile(r"https?://[^\s)<>\]]+[^\s)<>\].,;:]")

LOGO = ('<svg viewBox="0 0 120 64" class="logo-mark" aria-hidden="true"><rect x="0" y="8" width="120" height="48" rx="24" fill="#16233F"/>'
        '<rect x="14" y="30" width="92" height="4" rx="2" fill="#F4F1EA"/><circle cx="60" cy="32" r="10" fill="#3A9A9A"/></svg>')

CHECK = '<svg viewBox="0 0 12 12" class="ico"><circle cx="6" cy="6" r="6" fill="#2A7F62"/><path d="M3.3 6.2l1.8 1.7 3.6-3.8" stroke="#fff" stroke-width="1.5" fill="none" stroke-linecap="round" stroke-linejoin="round"/></svg>'
QMARK = '<svg viewBox="0 0 12 12" class="ico"><circle cx="6" cy="6" r="5.25" fill="none" stroke="#D9822B" stroke-width="1.5" stroke-dasharray="2 1.6"/><circle cx="6" cy="6" r="1.4" fill="#D9822B"/></svg>'


def e(s):
    return html.escape(str(s or ""), quote=True)


def short_url(u):
    u = re.sub(r"^https?://(www\.)?", "", u)
    return u if len(u) <= 58 else u[:55] + "…"


def linkify(escaped):
    return URL_RE.sub(lambda m: f'<a href="{m.group(0)}">{short_url(m.group(0))}</a>', escaped)


def split_label(s, sep=": "):
    """'Clock: the 4 THL…' -> ('Clock', 'the 4 THL…')."""
    if sep in s:
        a, b = s.split(sep, 1)
        if len(a) < 70:
            return a.strip(), b.strip()
    return "", s


def eur(x):
    return f"€{x:,.0f}"


class Notes:
    """Numbered sources & notes collected while rendering, printed in the footer."""

    def __init__(self):
        self.items = []

    def add(self, text):
        text = (text or "").strip()
        if not text:
            return ""
        if text not in self.items:
            self.items.append(text)
        return f'<sup class="fn">{self.items.index(text) + 1}</sup>'

    def html(self):
        lis = "".join(f"<li>{linkify(e(t))}</li>" for t in self.items)
        return f'<ol class="notes">{lis}</ol>'


# ---------------------------------------------------------------- chart

def comparison_svg(cmp):
    focus, ref = cmp["focus"], cmp["reference"]
    W, row_h, label_w, pad_r = 380, 14, 46, 34
    groups = cmp["groups"]
    vmax = max(max((v.get("ci") or [0, v["value"]])[1], v["value"]) for g in groups for v in g["values"].values())
    vmax = 10 * (int(vmax / 10) + 1)
    plot_w = W - label_w - pad_r
    x = lambda v: label_w + plot_w * v / vmax
    out, y = [], 4
    for g in groups:
        out.append(f'<text x="0" y="{y + row_h + 1}" class="c-grp">{e(g["label"])}</text>')
        for area in (focus, ref):
            v = g["values"].get(area)
            if not v:
                continue
            cls = "c-focus" if area == focus else "c-ref"
            out.append(f'<rect x="{label_w}" y="{y}" width="{x(v["value"]) - label_w:.1f}" height="{row_h - 4}" rx="2" class="{cls}"/>')
            if v.get("ci"):
                lo, hi = v["ci"]
                cy = y + (row_h - 4) / 2
                out.append(f'<path d="M{x(lo):.1f} {cy}H{x(hi):.1f}M{x(lo):.1f} {cy - 3}v6M{x(hi):.1f} {cy - 3}v6" class="c-ci"/>')
            tx = x(max(v["value"], (v.get("ci") or [0, 0])[1])) + 4
            out.append(f'<text x="{tx:.1f}" y="{y + row_h - 5.5}" class="c-val {cls}-t">{v["value"]:.1f}%</text>')
            y += row_h
        y += 6
    for t in range(0, vmax + 1, 10):
        out.insert(0, f'<line x1="{x(t):.1f}" x2="{x(t):.1f}" y1="0" y2="{y - 4}" class="c-grid"/>'
                      f'<text x="{x(t):.1f}" y="{y + 5}" class="c-axis">{t}%</text>')
    H = y + 8
    legend = (f'<div class="c-legend"><span><i class="sw c-focus"></i>{e(focus)}</span>'
              f'<span><i class="sw c-ref"></i>{e(ref)}</span><span><i class="sw-ci"></i>95% CI</span></div>')
    return legend + f'<svg viewBox="0 0 {W} {H}" class="chart">{"".join(out)}</svg>'


# ---------------------------------------------------------------- page parts

def header(eyebrow, right):
    return f"""<header class="band">
  <div class="brand">{LOGO}<span class="wordmark">tasan</span><span class="eyebrow">{e(eyebrow)}</span></div>
  <div class="band-r">{right}</div>
</header>"""


def draft_ribbon(text):
    t = re.sub(r"^DRAFT\s*[–-]\s*", "", text)
    return f'<div class="ribbon"><b>DRAFT</b><span>{e(t[:1].upper() + t[1:])}</span></div>'


def page_brief(d):
    n = Notes()
    p, a, c, z = d["problem"], d["action"], d["cost_range"], d["az_role"]
    eyebrow, _, title = d["title"].partition(" – ")
    if not title:
        eyebrow, title = "Pilot brief", d["title"]
    eyebrow = eyebrow.replace(d.get("project", "Tasan"), "").strip() or "Pilot brief"
    county = title

    # problem
    src_label = p["source"]
    fn_src = n.add(src_label)
    chart = comparison_svg(p["comparison"]) if p.get("comparison") else f'<p class="metric">{e(p["metric"])}</p>'
    if p.get("comparison"):
        cmp_title = f'<div class="card-k">{e(p["comparison"]["measure"])}{fn_src}</div>'
    else:
        cmp_title = ""
    ph = p.get("people_headline")
    people = ""
    if ph:
        fn_people = n.add(p.get("people_estimate"))
        people = f"""<div class="stat">
      <div class="stat-v">{e(ph["value"])}<small>{e(ph["unit"])}</small>{fn_people}</div>
      <div class="stat-l">{e(ph["label"])}</div></div>"""
    fn_cost = n.add("Cost basis: " + c["basis"] + " Sources: " + "; ".join(c["sources"]))
    cost = f"""<div class="stat">
      <div class="stat-v">€{c["low_eur"] / 1000:.0f}–{c["high_eur"] / 1000:.0f}k<small>for {e(c["period"])}</small>{fn_cost}</div>
      <div class="stat-l">{eur(c["low_eur"])}–{eur(c["high_eur"])}: nurse navigator 1.0 FTE + analyst 0.5 FTE. {e(c.get("excludes", ""))}</div></div>"""

    problem = f"""<section class="problem">
  <div class="card problem-card">
    <div class="sec-k">The problem</div>
    <p class="lede">{e(p["line"])}</p>
    {cmp_title}
    {chart}
    <p class="micro">{e(p["caveat"])}</p>
  </div>
  <div class="stats">{people}{cost}</div>
</section>"""

    # action
    comps = []
    for i, comp in enumerate(a.get("components", []), 1):
        lbl, body = split_label(comp)
        comps.append(f'<div class="step"><div class="step-n">{i}</div><div class="step-t">{e(lbl)}</div><div class="step-b">{e(body)}</div></div>')
    action = f"""<section>
  <div class="sec-k">The action</div>
  <p class="lede">{e(a["summary"])}</p>
  <div class="steps">{"".join(comps)}</div>
</section>"""

    # timeline
    tl = ""
    if d.get("timeline"):
        segs = []
        for i, t in enumerate(d["timeline"]):
            lbl, body = split_label(t)
            segs.append(f'<div class="seg seg{i}"><div class="seg-bar"><span>{e(lbl)}</span></div><div class="seg-b">{e(body)}</div></div>')
        tl = f"""<section>
  <div class="sec-k">90 days <span class="sec-sub">Day-28 alert starts at go-live · stop/go on day 90</span></div>
  <div class="timeline">{"".join(segs)}<div class="seg-end"><div class="diamond"></div><span>Stop / Go</span></div></div>
</section>"""

    # KPIs + stop/go
    rows = "".join(
        f'<tr><td class="kpi-n">{e(k["name"])}{"&nbsp;<span class=dc>D</span>" if k.get("design_choice") else ""}</td>'
        f'<td>{e(k["baseline_method"])}</td><td><span class="target">{e(k["target"])}</span></td></tr>' for k in d["kpis"])
    fn_kpi = n.add(d.get("kpi_caveat"))
    s = d["stop_go"]
    go_text = re.sub(r"^Go( \(extend\))? if ", "", s["go"])
    kpi_stop = f"""<section class="two">
  <div>
    <div class="sec-k">KPIs <span class="sec-sub"><span class="dc">D</span> = Tasan design choice{fn_kpi}</span></div>
    <table class="kpis"><thead><tr><th>KPI</th><th>Baseline</th><th>Target</th></tr></thead><tbody>{rows}</tbody></table>
  </div>
  <div>
    <div class="sec-k">Day-90 stop / go</div>
    <div class="decider">Decided by <b>{e(s["decider"])}</b></div>
    <div class="go"><b>Go</b>{e(go_text)}</div>
    <div class="stop"><b>Stop</b>{e(s["stop"])}</div>
  </div>
</section>"""

    # owners + AZ
    owners = []
    for o in d["owners"]:
        lbl, role = split_label(o["role"])
        ok = "not verified" not in (o.get("verified") or "")
        fn = n.add(o["source"]) if o.get("source") else ""
        owners.append(f'<li>{CHECK if ok else QMARK}<div><div class="own-l">{e(lbl)}</div>'
                      f'<div class="own-r">{e(role)}{fn}</div><div class="own-v {"" if ok else "warn"}">{e(o.get("verified"))}</div></div></li>')
    fn_az = n.add(z["compliance_framework"] + " " + z["compliance_source"])
    could, _, rest = z["summary"].partition(". No ")
    if rest:
        items = [x.strip().rstrip(".") for x in re.split(r"[,;]", "No " + rest) if x.strip()]
        no = [x for x in items if x.lower().startswith("no ")]
        yes = [x for x in items if not x.lower().startswith("no ")]
        az_body = (f'<p class="az-could">{e(could)}.{fn_az}</p><div class="guard">'
                   + "".join(f'<span class="g-no">{e(x[:1].upper() + x[1:])}</span>' for x in no)
                   + "".join(f'<span class="g-yes">{e(x[:1].upper() + x[1:])}</span>' for x in yes) + "</div>")
    else:
        az_body = f"<p>{e(z['summary'])}{fn_az}</p>"
    people_az = f"""<section class="two">
  <div>
    <div class="sec-k">Owners <span class="sec-sub">roles only</span></div>
    <ul class="owners">{"".join(owners)}</ul>
  </div>
  <div class="az">
    <div class="sec-k">AstraZeneca's role <span class="sec-sub">compliance-safe</span></div>
    {az_body}
    <p class="micro">{e(z.get("note"))}</p>
  </div>
</section>"""

    # precedent + caveats
    pre = []
    for pr in d.get("precedents", []):
        fn = n.add(pr["source"] + " (" + pr["date"] + ")")
        pre.append(f'<p><b>Precedent · {e(pr["name"])}.</b> {e(pr["description"])}{fn}</p>')
    cav = "".join(f"<li>{e(x)}</li>" for x in d.get("caveats", []))
    context = f"""<section class="context">
  <div>{"".join(pre)}</div>
  <div><b>Caveats</b><ul>{cav}</ul></div>
</section>"""

    sig = d["signer"]
    fn_sig = n.add(sig.get("source"))
    sign = f"""<section class="sign">
  <div class="sig-role"><div class="sec-k">Signature</div>{e(sig["role"])}{fn_sig}</div>
  <div class="sig-line"><span>Signature</span></div>
  <div class="sig-line short"><span>Date</span></div>
</section>"""

    right = (f'<div class="band-k">Prepared</div><div class="band-v">{e(d["date_prepared"])}</div>')
    foot = f'{e(d["status_label"])} Prepared {e(d["date_prepared"])} by the Tasan team (Junction 2026).'
    page1 = f"""<div class="page p1">
{header("Pilot brief · 90 days", right)}
<main>
{draft_ribbon(d["status_label"])}
<div class="title-row"><div><div class="kicker">{e(eyebrow)}</div><h1>{e(county)}</h1></div>
  <div class="title-meta">Lung-cancer pathway clock<br>Day-28 alert · nurse navigator</div></div>
{problem}
{action}
{tl}
{kpi_stop}
{sign}
<footer><div class="foot"><span>{foot} This page is the complete ask; owners, AstraZeneca's role and numbered sources are on page 2.</span><span class="pg">1</span></div></footer>
</main></div>"""
    page2 = f"""<div class="page p2">
{header("Pilot brief · owners & sources", right)}
<main>
{draft_ribbon(d["status_label"])}
<div class="title-row"><div><div class="kicker">{e(eyebrow)} · {e(county)}</div><h1 class="h1-sm">Who owns it, and how AstraZeneca can help</h1></div></div>
{people_az}
{context}
<section class="sources"><div class="sec-k">Sources &amp; notes <span class="sec-sub">numbers match the superscripts on both pages</span></div>{n.html()}</section>
<footer><div class="foot"><span>{foot}</span><span class="pg">2</span></div></footer>
</main></div>"""
    return page1 + page2


# ---------------------------------------------------------------- appendix (small markdown subset)

def md_inline(s):
    s = e(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)\*(?!\w)", r"<i>\1</i>", s)
    return linkify(s)


def md_blocks(md):
    """Yield (kind, payload) for paragraphs, headings, quotes and (nested) lists."""
    blocks, cur = [], []
    for line in md.splitlines() + [""]:
        if line.strip() == "":
            if cur:
                blocks.append(cur)
                cur = []
        else:
            cur.append(line.rstrip())
    for b in blocks:
        if b[0].startswith("# "):
            yield "h1", b[0][2:]
        elif all(l.startswith(">") for l in b):
            yield "quote", " ".join(l.lstrip("> ").strip() for l in b)
        elif all(re.match(r"\s*- ", l) for l in b):
            yield "list", b
        else:
            # paragraph possibly followed by list lines
            para = [l for l in b if not re.match(r"\s*- ", l)]
            lst = [l for l in b if re.match(r"\s*- ", l)]
            yield "p", " ".join(para)
            if lst:
                yield "list", lst


def md_list(lines):
    out, depth = [], -1
    for l in lines:
        d = (len(l) - len(l.lstrip())) // 2
        while depth < d:
            out.append("<ul>"); depth += 1
        while depth > d:
            out.append("</li></ul>"); depth -= 1
        if out[-1] not in ("<ul>",):
            out.append("</li>")
        out.append("<li>" + md_inline(l.strip()[2:]))
    out.append("</li>")
    while depth >= 0:
        out.append("</ul>"); depth -= 1
    return "".join(out).replace("<ul></li>", "<ul>")


def page_appendix(md, d):
    parts, callouts, title, ribbon = [], [], "Appendix", ""
    for kind, x in md_blocks(md):
        if kind == "h1":
            title = x
        elif kind == "quote":
            callouts.append(f'<div class="callout">{md_inline(x)}</div>')
        elif kind == "list":
            parts.append(f'<div class="ap-list">{md_list(x)}</div>')
        else:
            m = re.match(r"^\*\*([^*]+?)\*\*\s*(.*)$", x)
            if m and not ribbon and m.group(1).startswith("DRAFT"):
                ribbon = m.group(1)
                continue
            if m:
                parts.append(f'</div><div class="ap-sec"><h3>{e(m.group(1).rstrip("."))}</h3><p>{md_inline(m.group(2))}</p>')
            else:
                parts.append(f"<p>{md_inline(x)}</p>")
    kicker, _, h1 = title.partition(": ")
    right = '<div class="band-k">Status</div><div class="band-v warn">Conditional</div>'
    return f"""<div class="page appendix">
{header("Pilot brief · appendix", right)}
<main>
{draft_ribbon(ribbon or d["status_label"])}
<div class="title-row"><div><div class="kicker">{e(kicker if h1 else "Appendix")}</div><h1>{e(h1 or title)}</h1></div>
  <div class="title-meta">Not part of the one-page ask<br>Starts only if the week-1 gate passes</div></div>
{"".join(callouts)}<div class="ap-body"><div class="ap-sec">{"".join(parts)}</div></div>
<footer><div class="foot"><span>{e(ribbon or d["status_label"])} Prepared {e(d["date_prepared"])} by the Tasan team (Junction 2026).</span><span class="pg">3</span></div></footer>
</main></div>"""


# ---------------------------------------------------------------- document

def css():
    a = ASSETS.replace("\\", "/")
    return f"""
@font-face{{font-family:Nunito;src:url("file://{a}/Nunito-VariableFont_wght.ttf");font-weight:200 900}}
@font-face{{font-family:InterB;src:url("file://{a}/inter-latin-wght-normal.woff2");font-weight:100 900}}
@font-face{{font-family:InterB;src:url("file://{a}/inter-latin-wght-italic.woff2");font-weight:100 900;font-style:italic}}
@page{{size:A4;margin:0}}
:root{{--navy:#16233F;--navy7:#22325A;--teal:#3A9A9A;--teal7:#2A7676;--teal1:#DDEFEE;--paper:#F4F1EA;--card-alt:#FBFAF6;
--line:#E4DFD4;--line2:#EEEAE1;--ink:#141B2B;--ink2:#3E4759;--ink3:#6B7385;--ink4:#9AA1AF;
--alert:#D9822B;--alert-bg:#FCE9D6;--ok:#2A7F62;--ok-bg:#E2F1EA;--crit:#C2412D;--crit-bg:#F8E0DA}}
*{{box-sizing:border-box;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
html,body{{margin:0;padding:0}}
body{{font-family:InterB,Inter,"Helvetica Neue",Arial,sans-serif;font-size:7.6pt;line-height:1.38;color:var(--ink2);
font-feature-settings:"tnum" 1,"cv11" 1}}
.page{{width:210mm;height:297mm;overflow:hidden;position:relative;page-break-after:always;background:#fff}}
.page:last-child{{page-break-after:auto}}
a{{color:var(--teal7);text-decoration:none}}
b{{color:var(--ink);font-weight:650}}
/* band */
.band{{background:var(--paper);height:15mm;padding:0 12mm;display:flex;align-items:center;justify-content:space-between;border-bottom:1.2pt solid var(--teal)}}
.brand{{display:flex;align-items:center;gap:2.2mm}}
.logo-mark{{height:6.4mm}}
.wordmark{{font-family:Nunito;font-weight:800;font-size:16pt;color:var(--navy);letter-spacing:-.02em;margin-top:-1pt}}
.eyebrow{{margin-left:3mm;padding-left:3mm;border-left:1px solid var(--line);font-size:7pt;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);font-weight:600}}
.band-r{{text-align:right}}
.band-k{{font-size:6pt;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);font-weight:600}}
.band-v{{font-family:Nunito;font-weight:800;font-size:10pt;color:var(--navy)}}
.band-v.warn{{color:var(--alert)}}
main{{padding:4mm 12mm 0}}
/* ribbon + title */
.ribbon{{display:flex;gap:2.5mm;align-items:center;background:var(--alert-bg);border-left:3pt solid var(--alert);border-radius:0 4px 4px 0;padding:1.3mm 3mm;font-size:7.2pt;color:#7a4410}}
.ribbon b{{color:#fff;background:var(--alert);border-radius:3px;padding:.4mm 1.6mm;font-size:6.6pt;letter-spacing:.1em}}
.title-row{{display:flex;justify-content:space-between;align-items:flex-end;margin:3.4mm 0 3mm}}
.kicker{{font-size:7pt;letter-spacing:.14em;text-transform:uppercase;color:var(--teal7);font-weight:700}}
h1{{font-family:Nunito;font-weight:850;font-size:21pt;line-height:1.05;color:var(--navy);margin:.6mm 0 0;letter-spacing:-.015em}}
.appendix h1{{font-size:15.5pt;max-width:140mm}}
.title-meta{{text-align:right;font-size:7.2pt;color:var(--ink3);line-height:1.45;font-weight:500}}
/* sections */
section{{margin-bottom:3.2mm}}
.sec-k{{font-size:6.6pt;letter-spacing:.13em;text-transform:uppercase;color:var(--teal7);font-weight:750;margin-bottom:1.3mm;display:flex;align-items:baseline;gap:2mm}}
.sec-sub{{letter-spacing:0;text-transform:none;color:var(--ink4);font-weight:500;font-size:6.6pt}}
.lede{{font-size:8.6pt;line-height:1.35;color:var(--ink);margin:0 0 2mm;font-weight:500}}
.micro{{font-size:6.3pt;color:var(--ink3);margin:1mm 0 0;line-height:1.35}}
.card{{border:1px solid var(--line);border-radius:6px;padding:3mm 3.4mm;background:#fff}}
sup.fn{{font-size:5.4pt;color:var(--teal7);font-weight:700;margin-left:.4mm;vertical-align:super;line-height:0}}
/* problem */
.problem{{display:grid;grid-template-columns:1fr 58mm;gap:3mm}}
.problem-card{{background:var(--card-alt)}}
.card-k{{font-size:6.6pt;font-weight:650;color:var(--ink2);margin:0 0 .8mm}}
.chart{{width:100%;display:block}}
.c-grp{{font-size:7.4px;font-weight:650;fill:var(--ink)}}
.c-focus{{fill:var(--navy)}} .c-ref{{fill:var(--teal)}}
.c-focus-t{{fill:var(--navy);font-weight:750}} .c-ref-t{{fill:var(--teal7);font-weight:650}}
.c-val{{font-size:7px}}
.c-ci{{stroke:var(--alert);stroke-width:1.1;fill:none}}
.c-grid{{stroke:var(--line2);stroke-width:.6}}
.c-axis{{font-size:5.6px;fill:var(--ink4);text-anchor:middle}}
.c-legend{{display:flex;gap:3.5mm;font-size:6.4pt;color:var(--ink2);margin-bottom:.6mm}}
.c-legend span{{display:flex;align-items:center;gap:1.1mm}}
.sw{{display:inline-block;width:2.6mm;height:2mm;border-radius:1px}}
.sw.c-focus{{background:var(--navy)}} .sw.c-ref{{background:var(--teal)}}
.sw-ci{{display:inline-block;width:3mm;height:0;border-top:1.1pt solid var(--alert)}}
.stats{{display:flex;flex-direction:column;gap:3mm}}
.stat{{flex:1;background:var(--navy);color:#C9D2E3;border-radius:6px;padding:3mm 3.4mm;display:flex;flex-direction:column;justify-content:center}}
.stat-v{{font-family:Nunito;font-weight:850;font-size:22pt;line-height:1;color:#fff;letter-spacing:-.01em}}
.stat-v small{{font-family:InterB;font-size:7pt;font-weight:600;color:#7FD0CF;margin-left:1.6mm;letter-spacing:0}}
.stat-v sup.fn{{color:#7FD0CF}}
.stat-l{{font-size:6.6pt;line-height:1.38;margin-top:1.6mm}}
/* steps */
.steps{{display:grid;grid-template-columns:repeat(4,1fr);gap:2.4mm}}
.step{{border:1px solid var(--line);border-top:2pt solid var(--teal);border-radius:0 0 6px 6px;padding:2.2mm 2.6mm 2.4mm;background:#fff}}
.step-n{{font-family:Nunito;font-weight:850;font-size:11pt;color:var(--teal);line-height:1}}
.step-t{{font-weight:700;color:var(--navy);font-size:7.8pt;margin:.8mm 0 .6mm}}
.step-b{{font-size:6.8pt;line-height:1.36}}
/* timeline */
.timeline{{display:flex;align-items:flex-start}}
.seg{{flex:1}}
.seg-bar{{height:5mm;display:flex;align-items:center;padding-left:2.4mm;color:#fff;font-weight:700;font-size:7pt;clip-path:polygon(0 0,calc(100% - 2.2mm) 0,100% 50%,calc(100% - 2.2mm) 100%,0 100%,2.2mm 50%)}}
.seg0 .seg-bar{{background:var(--navy7);clip-path:polygon(0 0,calc(100% - 2.2mm) 0,100% 50%,calc(100% - 2.2mm) 100%,0 100%);border-radius:3px 0 0 3px}}
.seg1 .seg-bar{{background:var(--navy)}} .seg2 .seg-bar{{background:var(--teal7)}}
.seg-bar span{{padding-left:1.6mm}}
.seg0 .seg-bar span{{padding-left:0}}
.seg-b{{font-size:6.8pt;padding:1.3mm 3.5mm 0 1.4mm;line-height:1.36}}
.seg-end{{width:15mm;display:flex;flex-direction:column;align-items:center;gap:1mm;padding-top:.6mm}}
.diamond{{width:3.6mm;height:3.6mm;background:var(--alert);transform:rotate(45deg);border-radius:1px}}
.seg-end span{{font-size:6.4pt;font-weight:700;color:var(--alert);white-space:nowrap}}
/* two-col */
.two{{display:grid;grid-template-columns:1.32fr 1fr;gap:4mm}}
table.kpis{{width:100%;border-collapse:collapse;font-size:6.8pt}}
.kpis th{{text-align:left;font-size:6pt;letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);font-weight:650;border-bottom:1px solid var(--line);padding:0 1.6mm 1mm 0}}
.kpis td{{border-bottom:1px solid var(--line2);padding:1.3mm 1.6mm 1.3mm 0;vertical-align:top;line-height:1.33}}
.kpis tr:last-child td{{border-bottom:none}}
.kpi-n{{font-weight:650;color:var(--ink);width:27%}}
.kpis td:last-child{{width:28%}}
.target{{display:inline-block;background:var(--teal1);color:var(--teal7);font-weight:700;border-radius:3px;padding:.3mm 1.3mm}}
.dc{{display:inline-block;font-size:5.2pt;font-weight:800;color:var(--ink3);border:.7pt solid var(--ink4);border-radius:2px;padding:0 .7mm;line-height:1.35;vertical-align:1px}}
.decider{{font-size:6.8pt;margin-bottom:1.4mm}}
.go,.stop{{border-radius:5px;padding:1.8mm 2.4mm 1.8mm 2.4mm;font-size:6.8pt;line-height:1.36;margin-bottom:1.6mm;display:grid;grid-template-columns:8mm 1fr;align-items:start}}
.go{{background:var(--ok-bg);border-left:2.2pt solid var(--ok)}} .go b{{color:var(--ok)}}
.stop{{background:var(--crit-bg);border-left:2.2pt solid var(--crit)}} .stop b{{color:var(--crit)}}
.go b,.stop b{{font-family:Nunito;font-weight:850;font-size:8.6pt;line-height:1.1}}
ul.owners{{list-style:none;margin:0;padding:0}}
.owners li{{display:grid;grid-template-columns:4.2mm 1fr;gap:1.2mm;padding:1.1mm 0;border-bottom:1px solid var(--line2)}}
.owners li:last-child{{border-bottom:none}}
.ico{{width:3.2mm;height:3.2mm;margin-top:.3mm}}
.own-l{{font-size:6pt;letter-spacing:.08em;text-transform:uppercase;color:var(--ink3);font-weight:650}}
.own-r{{font-size:6.9pt;color:var(--ink);font-weight:550;line-height:1.32}}
.own-v{{font-size:6.1pt;color:var(--ok)}} .own-v.warn{{color:var(--alert)}}
.az{{background:var(--paper);border-radius:6px;padding:2.6mm 3.2mm}}
.az p{{margin:0 0 1.2mm;font-size:6.9pt;line-height:1.38}}
/* context */
.context{{display:grid;grid-template-columns:1.32fr 1fr;gap:4mm;font-size:6.6pt;line-height:1.36;border-top:1px solid var(--line);padding-top:2mm}}
.context p{{margin:0}}
.context ul{{margin:.5mm 0 0;padding-left:3.2mm}}
/* signature */
.sign{{display:grid;grid-template-columns:1.25fr 1fr 34mm;gap:5mm;align-items:end;border:1px dashed var(--ink4);border-radius:6px;padding:2.4mm 3.4mm 2.6mm;margin-bottom:2.6mm}}
.sig-role{{font-size:6.8pt;color:var(--ink);font-weight:550;line-height:1.32}}
.sig-role .sec-k{{margin-bottom:.6mm}}
.sig-line{{border-bottom:1px solid var(--ink2);height:8mm;position:relative}}
.sig-line span{{position:absolute;bottom:-3.6mm;left:0;font-size:5.8pt;color:var(--ink3);letter-spacing:.08em;text-transform:uppercase}}
/* footer */
footer{{position:absolute;left:12mm;right:12mm;bottom:7mm}}
.notes-k{{font-size:5.8pt;letter-spacing:.12em;text-transform:uppercase;color:var(--ink3);font-weight:700;margin-bottom:.6mm}}
ol.notes{{margin:0;padding-left:4.2mm;columns:2;column-gap:7mm;font-size:6.9pt;line-height:1.42;color:var(--ink2)}}
ol.notes li{{break-inside:avoid;margin-bottom:1.3mm;padding-left:.6mm}}
ol.notes li::marker{{color:var(--teal7);font-weight:700}}
.foot{{border-top:1px solid var(--line);padding-top:1.4mm;font-size:6pt;color:var(--ink4);display:flex;justify-content:space-between;gap:6mm}}\n.pg{{font-family:Nunito;font-weight:800;color:var(--navy);font-size:8pt}}
.h1-sm{{font-size:15.5pt}}
.sources{{border-top:1px solid var(--line);padding-top:2.6mm;margin-top:4mm}}

/* page-1 roomier type */
.p1 .step-b,.p1 .seg-b,.p1 .go,.p1 .stop,.p1 .decider{{font-size:7.3pt}}
.p1 table.kpis{{font-size:7.2pt}}
.p1 .kpis td:last-child{{width:33%}}
.p1 .kpi-n{{width:25%}}
.p1 .stat-l{{font-size:7pt}}
.p1 section{{margin-bottom:4mm}}
.p1 .steps{{gap:2.6mm}} .p1 .step{{padding:2.6mm 3mm 3mm}}
.sign{{padding-bottom:5.2mm}}
/* page 2 */
.p2 .two,.p2 .context{{font-size:8.2pt}}
.p2 .own-r{{font-size:8.4pt}} .p2 .own-l{{font-size:6.6pt}} .p2 .own-v{{font-size:7pt}}
.p2 .owners li{{padding:2mm 0;grid-template-columns:5mm 1fr}} .p2 .ico{{width:3.8mm;height:3.8mm}}
.p2 .az{{padding:3.6mm 4mm}} .p2 .az p{{font-size:8.2pt;line-height:1.45}}
.az-could{{color:var(--ink)}}
.guard{{display:flex;flex-wrap:wrap;gap:1.4mm;margin:1mm 0 2.4mm}}
.guard span{{border-radius:20px;padding:.7mm 2.4mm .7mm 2mm;font-size:7pt;font-weight:600}}
.g-no{{background:#fff;color:var(--crit);border:.7pt solid #EBC0B6}} .g-no::before{{content:"✕  ";font-weight:800}}
.g-yes{{background:var(--ok-bg);color:var(--ok)}} .g-yes::before{{content:"✓  ";font-weight:800}}
.p2 .context{{font-size:8pt;line-height:1.45;padding-top:3.4mm;margin-top:2mm}}
.p2 .context ul{{padding-left:4mm}}
.p2 .sources{{margin-top:5mm;padding-top:4mm}}
.p2 ol.notes{{font-size:7.6pt;line-height:1.48}}
.p2 ol.notes li{{margin-bottom:2mm}}
.ap-sec{{break-inside:avoid;margin-bottom:3mm}}
.ap-body h3{{margin-top:0!important}}
.ap-sec:empty{{display:none}}
/* appendix */
.ap-body{{columns:2;column-gap:7mm;font-size:7.9pt;line-height:1.45}}
.ap-body h3{{font-size:6.8pt;letter-spacing:.13em;text-transform:uppercase;color:var(--teal7);font-weight:750;margin:3.2mm 0 .8mm;break-after:avoid}}
.ap-body p{{margin:0 0 1.4mm}}
.ap-body ul{{margin:0 0 1.4mm;padding-left:3.6mm}}
.ap-body li{{margin-bottom:.6mm}}
.ap-body li::marker{{color:var(--teal)}}
.ap-list{{break-inside:avoid-column}}
.callout{{column-span:all;background:var(--alert-bg);border-left:3pt solid var(--alert);border-radius:0 6px 6px 0;padding:2.6mm 3.6mm;margin:0 0 2mm;font-size:8.2pt;color:#5b3510}}
.callout b{{color:#7a4410}}
"""


def to_html(d, appendix_md=None):
    pages = page_brief(d) + (page_appendix(appendix_md, d) if appendix_md else "")
    return (f'<!doctype html><html lang="en"><head><meta charset="utf-8"><title>{e(d["title"])}</title>'
            f"<style>{css()}</style></head><body>{pages}</body></html>")


CHROME_CANDIDATES = [
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Chromium.app/Contents/MacOS/Chromium",
    "google-chrome", "chromium", "chromium-browser",
]


def html_to_pdf(html_path, pdf_path):
    chrome = next((c for c in CHROME_CANDIDATES if os.path.exists(c) or shutil.which(c)), None)
    if not chrome:
        raise SystemExit("PDF needs Google Chrome or Chromium installed")
    with tempfile.TemporaryDirectory() as prof:
        subprocess.run([chrome, "--headless=new", "--disable-gpu", "--no-pdf-header-footer",
                        f"--user-data-dir={prof}", f"--print-to-pdf={os.path.abspath(pdf_path)}",
                        "file://" + os.path.abspath(html_path)],
                       check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=120)
