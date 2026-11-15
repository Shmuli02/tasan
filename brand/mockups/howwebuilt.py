#!/usr/bin/env python3
"""Build the How we built it mockup from verda/extract/samples.json."""
import json, html, math, subprocess, pathlib, sys

ROOT = pathlib.Path('/workspace/junction-new')
BRAND = ROOT / 'brand'
MOCK = BRAND / 'mockups'
SAMPLES = ROOT / 'verda/extract/samples.json'

sys.path.insert(0, str(MOCK))
from icons import icon
import build as B

OPEN_ID = 'SYN-P0051-oncology_note-04'

# Colour-blind-safe marker fills. Text contrast on fill is ≥ 6.9:1 (AA).
# No red/green pairing. Soft pastels on warm paper.
HL = {
    'referral_received':   ('#C5E0DC', '#1A4A48'),
    'ct_done':             ('#C4D6F0', '#1C3A66'),
    'biopsy_done':         ('#DDD0F0', '#4A2C78'),
    'pathology_result':    ('#F0DB9A', '#5A4208'),
    'mdt_decision':        ('#C9D2E2', '#16233F'),
    'treatment_decision':  ('#EEC8B0', '#5A2E12'),
    'treatment_start':     ('#E8C5D8', '#6A2450'),
}
EVENT_ORDER = list(HL.keys())

LOGO = (BRAND / 'logo-horizontal.svg').read_text().replace('<svg ', '<svg class="logo" ', 1)

TABS = [
    ('Overview', 'map'),
    ('Counties', 'building'),
    ('Pathway', 'route'),
    ('Tasan Live', 'activity'),
    ('Simulate', 'sliders'),
    ('Pilot', 'clip'),
    ('How we built it', 'layers'),
]


def topbar():
    t = ''.join(
        f'<div class="tab{" on" if n=="How we built it" else ""}">{icon(i)}{n}'
        f'{"<span class=ex>EXAMPLE</span>" if n=="Tasan Live" else ""}</div>'
        for n, i in TABS
    )
    return (
        f'<header class="topbar">{LOGO}<nav class="tabs">{t}</nav>'
        f'<div class="right"><div class="lang"><span>FI</span><span class="on">EN</span></div>'
        f'<span class="badge b-verda">AI on Verda · EU-hosted</span></div></header>'
    )


def body_pos(text: str) -> int:
    eq, pos = 0, 0
    for line in text.splitlines(True):
        if set(line.strip()) <= set('=') and len(line.strip()) > 20:
            eq += 1
            if eq == 2:
                return pos + len(line)
        pos += len(line)
    return 0


def parse_header(text: str) -> dict:
    meta = {}
    for line in text.splitlines():
        if ':' in line and not line.startswith('='):
            k, _, v = line.partition(':')
            key = k.strip()
            if key in {'corpus_id', 'patient_id', 'document_id', 'document_type',
                       'language', 'note_date', 'display_name'}:
                meta[key] = v.strip()
    return meta


def extracted_events(note):
    ev = note.get('model_events')
    if ev:
        return ev
    return note.get('gold_events') or []


def mark_text(text: str, events, start: int, end: int, with_marks=True) -> str:
    parts, i = [], start
    if with_marks:
        evs = sorted(
            [e for e in events
             if e.get('start', -1) >= 0 and e.get('end', -1) > start and e['start'] < end],
            key=lambda e: e['start'],
        )
        for e in evs:
            s, en = max(e['start'], start), min(e['end'], end)
            parts.append(html.escape(text[i:s]))
            typ = html.escape(e['type'])
            date = html.escape(e.get('date') or '')
            parts.append(
                f'<mark class="hl hl-{typ}" data-type="{typ}" data-date="{date}" '
                f'data-start="{e["start"]}" data-end="{e["end"]}">{html.escape(text[s:en])}</mark>'
            )
            i = en
    parts.append(html.escape(text[i:end]))
    return ''.join(parts).replace('\n', '<br>')


def stamp():
    return '<div class="stamp">SYNTHETIC · NOT A REAL PATIENT</div>'


def sheet_closed(note, x, y, rot, z, openish=False):
    text = note['text']
    bp = body_pos(text)
    body = mark_text(text, extracted_events(note), bp, len(text), with_marks=False)
    v2 = 'v2' in (note.get('corpus_id') or '')
    cls = 'sheet open' if openish else 'sheet'
    return (
        f'<article class="{cls}" style="--x:{x}px;--y:{y}px;--rot:{rot}deg;'
        f'--from-x:210px;--from-y:90px;--from-rot:-2deg;--stagger:{z*45}ms;z-index:{z};'
        f'left:0;top:0" data-note-id="{html.escape(note["note_id"])}">'
        f'<div class="tab-lab">{html.escape(note["doc_type"])}</div>'
        f'<div class="meta-row"><span class="lang">{html.escape(note["lang"].upper())}'
        f' · {html.escape(note["note_date"])}</span>'
        f'{"<span class=v2>v2</span>" if v2 else ""}</div>'
        f'<div class="body">{body}</div>'
        f'{stamp()}'
        f'<div class="nid">{html.escape(note["note_id"])}</div>'
        f'</article>'
    )


def sheet_open(note, x, y, rot, z):
    text = note['text']
    bp = body_pos(text)
    meta = parse_header(text)
    events = extracted_events(note)
    head_body = mark_text(text, events, bp, len(text), with_marks=True)
    v2 = 'v2' in (note.get('corpus_id') or '')

    def cell(k, label=None):
        v = meta.get(k, '')
        return f'<dt>{html.escape(label or k)}</dt><dd>{html.escape(v)}</dd>'

    src = html.escape(note.get('source') or '')
    return (
        f'<article class="sheet open" style="--x:{x}px;--y:{y}px;--rot:{rot}deg;'
        f'--from-x:240px;--from-y:70px;--from-rot:-8deg;--stagger:0ms;z-index:{z};'
        f'left:0;top:0" data-note-id="{html.escape(note["note_id"])}">'
        f'<div class="tab-lab">{html.escape(note["doc_type"])}</div>'
        f'<div class="file-head">'
        f'<div class="banner">SYNTHETIC DOCUMENT — NOT A REAL PATIENT</div>'
        f'<dl>{cell("corpus_id")}{cell("patient_id")}'
        f'{cell("document_id")}{cell("note_date")}'
        f'{cell("language")}{cell("display_name")}</dl>'
        f'</div>'
        f'<div class="body">{head_body}</div>'
        f'{stamp()}'
        f'<div class="nid">{html.escape(note["note_id"])}'
        f'{" · v2 held-out" if v2 else ""} · model_events · {src}'
        f' · offsets into text</div>'
        f'</article>'
    )


def clock_svg(day, of=42, size=88, stroke=9):
    r = (size - stroke) / 2
    c = 2 * math.pi * r
    f = min(day / of, 1)
    col = '#2A7F62' if day < 21 else '#B38A00' if day < 28 else '#D9822B' if day < 42 else '#C2412D'
    ticks = ''
    for d in (21, 28):
        a = 2 * math.pi * d / of - math.pi / 2
        x1 = size / 2 + (r - 5) * math.cos(a)
        y1 = size / 2 + (r - 5) * math.sin(a)
        x2 = size / 2 + (r + 5) * math.cos(a)
        y2 = size / 2 + (r + 5) * math.sin(a)
        ticks += (
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#9AA1AF" stroke-width="2"/>'
        )
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 {size} {size}">'
        f'<circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="#E4DFD4" stroke-width="{stroke}"/>'
        f'<circle cx="{size/2}" cy="{size/2}" r="{r}" fill="none" stroke="{col}" stroke-width="{stroke}" '
        f'stroke-linecap="round" stroke-dasharray="{c*f:.1f} {c:.1f}" transform="rotate(-90 {size/2} {size/2})"/>'
        f'{ticks}'
        f'<text x="50%" y="48%" text-anchor="middle" font-family="Nunito, Inter, sans-serif" '
        f'font-weight="800" font-size="22" fill="#16233F">D{day}</text>'
        f'<text x="50%" y="66%" text-anchor="middle" font-family="Inter, sans-serif" '
        f'font-size="10" fill="#6B7385">of {of} · 6 wk</text>'
        f'</svg>'
    )


def rail(note):
    events = extracted_events(note)
    present = {e['type'] for e in events}
    legs = []
    for typ in EVENT_ORDER:
        bg, fg = HL[typ]
        unused = ' unused' if typ not in present else ''
        legs.append(
            f'<div class="leg{unused}"><i style="background:{bg};color:{fg}"></i>{typ}</div>'
        )
    evs = []
    for e in events:
        bg, fg = HL[e['type']]
        off = f'{e["start"]}–{e["end"]}' if e.get('start', -1) >= 0 else 'no offset'
        evs.append(
            f'<div class="ev"><i style="background:{bg}"></i>'
            f'<span class="t">{html.escape(e["type"])}'
            f'<small>{html.escape(off)}</small></span>'
            f'<span class="d">{html.escape(e.get("date") or "")}</span></div>'
        )
    alert = note['alert']
    if alert:
        chip = '<span class="dchip" style="background:#FCE9D6;color:#A75A12">Alert</span>'
    else:
        chip = '<span class="dchip" style="background:#E2F1EA;color:#2A7F62">No alert</span>'
    src = html.escape(note.get('source') or '')
    model = html.escape(note.get('model_name') or src)
    nid = html.escape(note['note_id'])
    pid = html.escape(note['patient_id'])
    day = note['day_count']
    return (
        '<aside class="rail">'
        '<div class="card" style="flex:none">'
        '<div class="card-head"><div><h2>Event types</h2>'
        '<div class="sub">Marker colour on the open note</div></div></div>'
        f'<div class="legend">{"".join(legs)}</div></div>'
        '<div class="card" style="flex:1">'
        f'<div class="card-head"><div><h2>Extracted events</h2>'
        f'<div class="sub">{nid}</div></div>'
        f'<span class="src">{src}</span></div>'
        f'<div class="evlist">{"".join(evs)}</div>'
        f'<div class="note-sm">From model_events · {model}. '
        'Spans are start/end into text (skip if −1).</div></div>'
        '<div class="card" style="flex:none">'
        '<div class="card-head"><div><h2>Day-28 clock</h2>'
        '<div class="sub">Gold events vs note_date</div></div></div>'
        f'<div class="clockbox">{clock_svg(day)}'
        f'<div class="who"><b>{pid}</b>'
        f'day_count {day} · {chip}<br>'
        'Treatment not started on this note.</div></div></div>'
        '</aside>'
    )


def pipeline():
    def step(ic, title, sub, next_=False):
        return (
            f'<div class="step{" next" if next_ else ""}">'
            f'<span class="ico{" next" if next_ else ""}">{icon(ic)}</span>'
            f'<div class="lab"><h3>{title}</h3><div class="sub">{sub}</div></div></div>'
        )
    arr = '<div class="arrow"></div>'
    return (
        '<section class="card pipe">'
        + step('file', 'Synthetic notes', '10 showcase notes · not real patients')
        + arr
        + step(
            'cpu',
            'Extract on Verda',
            '<b>Qwen3-32B</b> · EU-hosted inference<br>regex_baseline as the floor',
            True,
        )
        + arr
        + step('braces', 'Structured events', '7 types, dates + evidence spans')
        + arr
        + step('clock', 'Day-28 clock', 'Alert when day_count ≥ 28')
        + '</section>'
    )


def fan_positions(n, mode='open'):
    pos = []
    if mode == 'fan':
        for i in range(n):
            t = i / (n - 1)
            rot = -32 + t * 62
            x = 260 + t * 640
            y = 168 + ((t - 0.5) ** 2) * 150
            pos.append((round(x), round(y), round(rot, 1)))
        return pos
    closed_n = n - 1
    for i in range(closed_n):
        t = i / max(closed_n - 1, 1)
        rot = -28 + t * 44
        x = 28 + t * 360
        y = 150 + ((t - 0.4) ** 2) * 130
        pos.append((round(x), round(y), round(rot, 1)))
    return pos


def build_state(data, notes, mode='open'):
    by_id = {n['note_id']: n for n in notes}
    opened = by_id[OPEN_ID]
    others = [n for n in notes if n['note_id'] != OPEN_ID]

    if mode == 'fan':
        order = others + [opened]
        pos = fan_positions(len(order), mode='fan')
        sheets = []
        for i, (note, (x, y, rot)) in enumerate(zip(order, pos)):
            openish = note['note_id'] == OPEN_ID
            sheets.append(sheet_closed(note, x, y, rot, z=i + 1, openish=openish))
        rail_html = ''
    else:
        pos = fan_positions(len(notes), mode='open')
        sheets = [sheet_closed(note, x, y, rot, z=i + 1)
                  for i, (note, (x, y, rot)) in enumerate(zip(others, pos))]
        sheets.append(sheet_open(opened, 455, 36, -1.2, z=20))
        rail_html = rail(opened)

    src_now = html.escape(data.get('source_now') or '')
    msgs = (
        '<div class="bubble me">What extracted these events?</div>'
        '<div class="bubble ai">The ten showcase notes were extracted with <b>Qwen3-32B</b> '
        'on Verda. Inference is EU-hosted. <b>regex_baseline</b> is the non-LLM floor.'
        f'<div class="meta">{icon("shield")} samples.json · source_now {src_now}</div></div>'
        '<div class="bubble me">Are these real patients?</div>'
        '<div class="bubble ai">No. Every note is <b>SYNTHETIC</b> — invented names, dates '
        'and findings, built for the extract eval.</div>'
    )

    body = topbar() + f'''<div class="shell"><main class="main hwb">
<div class="hwb-hdr"><div>
  <div class="kicker">Verda extract · EU-hosted inference</div>
  <h1>How we built it</h1>
</div>
<div class="chips">
  <span class="badge b-ex">SYNTHETIC notes</span>
  <span class="badge b-comp">Qwen3-32B</span>
  <span class="badge b-verda" style="height:22px;font-size:11px;padding:0 10px">EU-hosted</span>
</div></div>
<div class="hero">
  <div class="stage"><div class="stage-floor"></div>
    <div class="sheets">{''.join(sheets)}</div>
  </div>
  {rail_html}
</div>
{pipeline()}
</main>
{B.panel('How we built it', msgs, ['What extracted these events?','Why synthetic notes?','What starts the clock?'])}</div>'''

    cls = f'capture state-{mode}'
    return (
        '<!doctype html><html lang="en"><head><meta charset="utf-8">'
        '<title>Tasan mockup – How we built it</title>'
        '<link rel="stylesheet" href="app.css">'
        '<link rel="stylesheet" href="howwebuilt.css">'
        f'</head><body class="{cls}">{body}</body></html>'
    )


def build():
    data = json.loads(SAMPLES.read_text())
    notes = data['notes']
    (MOCK / 'howwebuilt.html').write_text(build_state(data, notes, 'open'))
    (MOCK / 'howwebuilt-fan.html').write_text(build_state(data, notes, 'fan'))
    print('wrote', MOCK / 'howwebuilt.html', 'and howwebuilt-fan.html')
    print('source_now=', data.get('source_now'), 'source_after_gpu=', data.get('source_after_gpu'))


def render():
    jobs = [
        (MOCK / 'howwebuilt.html', BRAND / 'mockup-howwebuilt-open.png'),
        (MOCK / 'howwebuilt-fan.html', BRAND / 'mockup-howwebuilt.png'),
    ]
    for src, dest in jobs:
        raw = MOCK / (dest.stem + '-raw.png')
        subprocess.run(
            [
                'google-chrome', '--headless=new', '--no-sandbox', '--disable-gpu',
                '--hide-scrollbars', '--force-device-scale-factor=1',
                '--window-size=1920,1080', f'--screenshot={raw}', src.resolve().as_uri(),
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        from PIL import Image
        im = Image.open(raw)
        if im.size != (1920, 1080):
            im = im.resize((1920, 1080), Image.Resampling.LANCZOS)
        if im.mode != 'RGB':
            im = im.convert('RGB')
        im.save(dest)
        raw.unlink(missing_ok=True)
        print('rendered', dest, im.size)


if __name__ == '__main__':
    build()
    if '--render' in sys.argv:
        render()
