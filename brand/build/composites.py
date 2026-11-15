#!/usr/bin/env python3
"""Re-render cover, social card, and brand sheet only."""
import json, csv, math, subprocess, pathlib
from PIL import Image

ROOT = pathlib.Path('/workspace/junction-new')
B, T = ROOT / 'brand', ROOT / 'brand' / 'build'
NAVY, TEAL, OFF = '#16233F', '#3A9A9A', '#F4F1EA'
TEAL_TEXT, MUTED = '#2A7676', '#5A6273'
FONT = (B / 'fonts' / 'Nunito-VariableFont_wght.ttf').as_uri()
facts = {f['id']: f for f in json.load(open(ROOT / 'data/facts.json'))['facts']}
PN_TEXT = facts['people_number_national']['statement_en']
TAG_EN = 'Same cancer, different postcode.'
TAG_FI = 'Sama syöpä, eri postinumero.'
SCALE = ['#16233F', '#2D6B7D', '#4F9C9C', '#86BFB9', '#BCDCD6', '#E6F2EF']  # tokens --tz-map-6..1
BINS = [21.0, 24.0, 27.0, 30.0, 33.0]
SCALE_LABELS = ['<21%', '21–24%', '24–27%', '27–30%', '30–33%', '≥33%']
LABEL = 'Computed by Tasan · illustrative, not published or causal · crude, not age- or stage-adjusted · not lives saved'
SRC = (
    'people_number_national · Keuhkosyöpä Suomessa 2019–2023, Taulukko 11 '
    '(Finnish Cancer Registry / THL / FICAN) · Tasan arithmetic on county counts. '
    'Map: same table, crude curative-treatment share by wellbeing county. Hatched: no public data (Åland).'
)

def logo_svg(word=NAVY, pill=NAVY, bar=OFF, dot=TEAL):
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 330 64">'
        f'<rect x="0" y="8" width="120" height="48" rx="24" fill="{pill}"/>'
        f'<rect x="14" y="30" width="92" height="4" rx="2" fill="{bar}"/>'
        f'<circle cx="60" cy="32" r="10" fill="{dot}"/>'
        f'<text x="140" y="47" font-family="Nunito, \'Varela Round\', Arial, sans-serif" '
        f'font-size="46" font-weight="600" fill="{word}" letter-spacing="1">tasan</text></svg>'
    )

LOGO, LOGO_WHITE = logo_svg(), logo_svg(word=OFF, pill=OFF, bar=NAVY, dot=TEAL)
MARK = (B / 'mark.svg').read_text()
FAV = (B / 'favicon.svg').read_text()

def page(body, w, h, bg='transparent'):
    return f'''<!doctype html><html><head><meta charset="utf-8"><style>
@font-face{{font-family:Nunito;src:url("{FONT}");font-weight:200 1000;font-style:normal}}
*{{margin:0;padding:0;box-sizing:border-box}}
html,body{{width:{w}px;height:{h}px;overflow:hidden;background:{bg};
  font-family:Nunito,sans-serif;color:{NAVY};-webkit-font-smoothing:antialiased}}
</style></head><body>{body}</body></html>'''

def render(name, html, w, h, scale=2):
    p = T / (name + '.html'); p.write_text(html)
    raw = T / (name + f'@{scale}x.png')
    subprocess.run(
        ['google-chrome','--headless=new','--no-sandbox','--disable-gpu','--hide-scrollbars',
         '--default-background-color=00000000', f'--force-device-scale-factor={scale}',
         f'--window-size={w},{h}', f'--screenshot={raw}', p.as_uri()],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    im = Image.open(raw)
    if im.size != (w, h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    dest = B / f'{name}.png'
    im.save(dest)
    print('rendered', dest, im.size, im.mode)

def inline(svg, w=None, h=None):
    attrs = (f' width="{w}"' if w else '') + (f' height="{h}"' if h else '')
    return svg.replace('<svg ', f'<svg{attrs} ', 1)

# ---- map ----
gj = json.load(open(ROOT / 'app/example-data/data/counties.geojson'))
share = {}
with open(ROOT / 'data/csv/lung_report2026_treatment_by_wsc.csv', encoding='utf-8') as f:
    for r in csv.DictReader(f):
        if r['treatment_group_fi'] == 'Parantava' and r['sex'] == 'total':
            share[r['region_code']] = float(r['value'])

def col(v):
    for i, b in enumerate(BINS):
        if v < b: return SCALE[i]
    return SCALE[-1]

def polygons_of(geom):
    return [geom['coordinates']] if geom['type'] == 'Polygon' else geom['coordinates']

def project_fn(features):
    k = math.cos(math.radians(65.0))
    xs, ys = [], []
    for ft in features:
        for poly in polygons_of(ft['geometry']):
            for ring in poly:
                for x, y in ring:
                    xs.append(x * k); ys.append(y)
    return k, min(xs), max(xs), min(ys), max(ys)

def path_d(ft, k, x0, y0, y1, ox, oy, s):
    d = []
    for poly in polygons_of(ft['geometry']):
        for ring in poly:
            d.append('M' + 'L'.join(f'{ox+(x*k-x0)*s:.2f},{oy+(y1-y)*s:.2f}' for x, y in ring) + 'Z')
    return ' '.join(d)

def map_svg(W, H, stroke, stroke_w=1.4, pad=10):
    main = [ft for ft in gj['features'] if ft['properties']['id'] != '91']
    aland = [ft for ft in gj['features'] if ft['properties']['id'] == '91']
    k, x0, x1, y0, y1 = project_fn(main)
    inner_w, inner_h = W - 2 * pad, H - 2 * pad
    bw, bh, gap = min(W * 0.28, 168), min(H * 0.18, 132), 10
    need = bw + gap
    s = min(inner_w / (x1 - x0), inner_h / (y1 - y0))
    mw, mh = (x1 - x0) * s, (y1 - y0) * s
    ox = pad + (inner_w - mw) / 2
    oy = pad + (inner_h - mh) / 2
    if ox < pad + need:
        s = min((inner_w - need) / (x1 - x0), inner_h / (y1 - y0))
        mw, mh = (x1 - x0) * s, (y1 - y0) * s
        ox = pad + need
        oy = pad + (inner_h - mh) / 2
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">',
        '<defs><pattern id="hatch" width="7" height="7" patternUnits="userSpaceOnUse" patternTransform="rotate(45)">',
        '<rect width="7" height="7" fill="#E4E0D6"/>',
        '<line x1="0" y1="0" x2="0" y2="7" stroke="#9A958A" stroke-width="2"/></pattern></defs>',
    ]
    for ft in main:
        cid = ft['properties']['id']
        fill = col(share[cid]) if cid in share else 'url(#hatch)'
        parts.append(
            f'<path d="{path_d(ft, k, x0, y0, y1, ox, oy, s)}" fill="{fill}" '
            f'stroke="{stroke}" stroke-width="{stroke_w}" stroke-linejoin="round"/>'
        )
    # Åland inset sits in the natural SW water of the mainland bounding box
    if aland:
        bx = pad + 2
        by = oy + mh * 0.70
        # keep the box on the canvas
        by = min(max(by, pad), H - bh - pad)
        parts.append(
            f'<rect x="{bx}" y="{by}" width="{bw}" height="{bh}" rx="12" '
            f'fill="{OFF}" stroke="#C9C4B8" stroke-width="1.25"/>'
        )
        ak, ax0, ax1, ay0, ay1 = project_fn(aland)
        ip = 12
        as_ = min((bw - 2 * ip) / (ax1 - ax0), (bh - 2 * ip) / (ay1 - ay0))
        aox = bx + (bw - (ax1 - ax0) * as_) / 2
        aoy = by + (bh - (ay1 - ay0) * as_) / 2
        for ft in aland:
            parts.append(
                f'<path d="{path_d(ft, ak, ax0, ay0, ay1, aox, aoy, as_)}" fill="url(#hatch)" '
                f'stroke="#9A958A" stroke-width="1" stroke-linejoin="round"/>'
            )
    parts.append('</svg>')
    return ''.join(parts)

def legend_html(fg, size=15, sw=46, sh=14):
    cells = [
        f'<div style="display:flex;flex-direction:column;align-items:center;gap:6px">'
        f'<div style="width:{sw}px;height:{sh}px;border-radius:7px;background:{c};'
        f'box-shadow:inset 0 0 0 1px rgba(22,35,63,.25)"></div>'
        f'<span style="font-weight:650;letter-spacing:.2px">{lab}</span></div>'
        for c, lab in zip(SCALE, SCALE_LABELS)
    ]
    return (
        f'<div style="display:flex;gap:10px;align-items:flex-end;font-size:{size}px;color:{fg}">'
        f'<span style="font-weight:700;padding-bottom:2px;opacity:.85">Lower</span>'
        + ''.join(cells)
        + f'<span style="font-weight:700;padding-bottom:2px;opacity:.85">Higher</span></div>'
    )

# ---------- submission cover 1920×1080
cover = f'''
<div style="position:relative;width:1920px;height:1080px;background:{OFF}">
  <div style="position:absolute;left:88px;top:56px">{inline(LOGO, 330, 64)}</div>
  <div style="position:absolute;left:88px;top:136px;font-size:34px;font-weight:700;letter-spacing:.2px">{TAG_EN}</div>
  <div style="position:absolute;left:88px;top:184px;font-size:15px;font-weight:700;color:{MUTED};letter-spacing:.3px">Junction 2026 · Equal Care Across Finland</div>
  <div style="position:absolute;left:88px;top:260px;width:880px">
    <div style="font-size:268px;font-weight:800;line-height:.82;letter-spacing:-8px">~65</div>
    <div style="font-size:26px;font-weight:550;line-height:1.45;margin-top:36px;max-width:820px">{PN_TEXT}</div>
    <div style="display:inline-block;margin-top:22px;padding:7px 16px;border-radius:999px;background:{NAVY};color:{OFF};font-size:15px;font-weight:700;letter-spacing:.3px">{LABEL}</div>
  </div>
  <div style="position:absolute;left:1040px;top:36px;width:800px;height:900px">{map_svg(800, 900, '#D4CFC5', stroke_w=1.35, pad=8)}</div>
  <div style="position:absolute;left:1080px;bottom:86px">{legend_html(NAVY, 13, 42, 13)}</div>
  <div style="position:absolute;left:88px;right:88px;bottom:36px;font-size:13px;line-height:1.45;color:{MUTED}">{SRC}</div>
</div>
'''
render('submission-cover', page(cover, 1920, 1080, bg=OFF), 1920, 1080, scale=2)

# ---------- square social 1080×1080 — map on an off-white panel so navy counties read
sq = f'''
<div style="position:relative;width:1080px;height:1080px;background:{NAVY};color:{OFF}">
  <div style="position:absolute;left:56px;top:44px">{inline(LOGO_WHITE, 290, 56)}</div>
  <div style="position:absolute;left:56px;top:112px;font-size:26px;font-weight:700;letter-spacing:.2px">{TAG_EN}</div>
  <div style="position:absolute;left:56px;top:200px;width:500px">
    <div style="font-size:188px;font-weight:800;line-height:.82;letter-spacing:-6px">{'~65'}</div>
    <div style="font-size:21px;font-weight:550;line-height:1.4;margin-top:24px;color:{OFF}">{PN_TEXT}</div>
    <div style="display:inline-block;margin-top:18px;padding:6px 14px;border-radius:999px;background:{TEAL};color:{NAVY};font-size:13px;font-weight:800;letter-spacing:.2px">ESTIMATE · computed by Tasan · not stage-adjusted</div>
  </div>
  <div style="position:absolute;right:48px;top:168px;width:456px;height:760px;background:{OFF};border-radius:28px;overflow:hidden">
    <div style="position:absolute;left:8px;top:8px;width:440px;height:680px">{map_svg(440, 680, '#D4CFC5', stroke_w=1.2, pad=6)}</div>
    <div style="position:absolute;left:16px;bottom:16px">{legend_html(NAVY, 11, 28, 10)}</div>
  </div>
  <div style="position:absolute;left:56px;right:520px;bottom:36px;font-size:12px;line-height:1.45;color:#C5CBD6">{LABEL}<br>{SRC}</div>
</div>
'''
render('social-card', page(sq, 1080, 1080, bg=NAVY), 1080, 1080, scale=2)

# ---------- brand sheet
def swatch(hexv, name, note, border=False):
    edge = 'box-shadow:inset 0 0 0 1.5px #C9C4B8;' if border or hexv == OFF else 'box-shadow:inset 0 0 0 1px rgba(22,35,63,.12);'
    return (
        f'<div style="width:200px">'
        f'<div style="height:92px;border-radius:16px;background:{hexv};{edge}"></div>'
        f'<div style="margin-top:10px;font-weight:800;font-size:18px">{name}</div>'
        f'<div style="font-weight:650;font-size:15px;letter-spacing:.4px">{hexv}</div>'
        f'<div style="font-size:13px;color:{MUTED};margin-top:2px;font-weight:600">{note}</div></div>'
    )

sheet = f'''
<div style="position:relative;width:1920px;height:1080px;background:{OFF}">
  <div style="position:absolute;left:80px;top:52px">{inline(LOGO, 360, 70)}</div>
  <div style="position:absolute;left:80px;top:140px;font-size:22px;font-weight:650;color:{MUTED};max-width:820px;line-height:1.4">
    <em>tasan</em> is Finnish for “even, level, exactly.” The mark is a spirit level: the teal bubble sits dead-centre when care does not tilt with the postcode.
  </div>

  <div style="position:absolute;left:80px;top:240px;display:flex;gap:28px">
    {swatch(NAVY,'Navy','Text + field. 13.83:1 on off-white')}
    {swatch(TEAL,'Teal','Graphic only on light grounds')}
    {swatch(TEAL_TEXT,'Teal ink','Text teal. 4.71:1 on off-white (AA)')}
    {swatch(OFF,'Off-white','Paper. 13.83:1 under navy', True)}
  </div>

  <div style="position:absolute;left:80px;top:460px;font-size:15px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:{MUTED}">Map scale · lower share → navy · colour-blind safe sequential</div>
  <div style="position:absolute;left:80px;top:494px">{legend_html(NAVY, 15, 48, 15)}</div>

  <div style="position:absolute;left:80px;top:590px;font-size:15px;font-weight:700;letter-spacing:1.4px;text-transform:uppercase;color:{MUTED}">Type</div>
  <div style="position:absolute;left:80px;top:622px;font-size:44px;font-weight:800;letter-spacing:-.5px">{TAG_EN}</div>
  <div style="position:absolute;left:80px;top:682px;font-size:28px;font-weight:700;color:{TEAL_TEXT}">{TAG_FI}</div>
  <div style="position:absolute;left:80px;top:734px;font-size:18px;font-weight:600;color:{MUTED};max-width:900px;line-height:1.45">
    Nunito 600 wordmark / 800 numerals. Fallback: Varela Round, Helvetica Neue, Arial. UI/body: Inter (see UI_STYLE.md).
  </div>

  <div style="position:absolute;left:80px;top:830px;font-size:16px;font-weight:650;line-height:1.55;max-width:960px">
    <b>Do</b> keep the bubble centred · use lowercase tasan · put a source next to every number · say “about” for Tasan-computed figures.<br>
    <b>Don’t</b> recolour the dot · stretch the pill · say “lives saved” · claim an AstraZeneca–county pilot · use the gold serif T.
  </div>

  <div style="position:absolute;right:80px;top:52px;width:720px;height:200px;background:{NAVY};border-radius:24px;display:flex;align-items:center;justify-content:center">
    {inline(LOGO_WHITE, 520, 100)}
  </div>
  <div style="position:absolute;right:80px;top:274px;display:flex;gap:28px;align-items:center">
    {inline(FAV, 160, 160)}
    {inline(FAV, 64, 64)}
    {inline(FAV, 32, 32)}
    {inline(MARK, 260, 104)}
  </div>
  <div style="position:absolute;right:80px;top:500px;width:720px;height:500px">
    {map_svg(720, 500, '#D4CFC5', stroke_w=1.2, pad=4)}
  </div>
  <div style="position:absolute;left:80px;bottom:28px;font-size:13px;color:{MUTED};font-weight:600">Tasan brand kit v1 · JN Brand &amp; Marketing · Junction 2026 · navy #16233F · teal #3A9A9A · off-white #F4F1EA</div>
</div>
'''
render('brand-sheet', page(sheet, 1920, 1080, bg=OFF), 1920, 1080, scale=2)
print('done')
