#!/usr/bin/env python3
"""Convert tasan wordmark to SVG paths (Nunito 600) and export logo + favicon assets."""
from __future__ import annotations

import subprocess
from pathlib import Path

from fontTools.ttLib import TTFont
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.pens.svgPathPen import SVGPathPen
from fontTools.pens.transformPen import TransformPen
from fontTools.misc.transform import Transform
from PIL import Image, ImageDraw, ImageFont

ROOT = Path("/workspace/junction-new")
B = ROOT / "brand"
FONT_PATH = B / "fonts" / "Nunito-VariableFont_wght.ttf"
NAVY, TEAL, OFF, WHITE = "#16233F", "#3A9A9A", "#F4F1EA", "#FFFFFF"

# Match logo.svg: x=140, y=47 (baseline), font-size=46, letter-spacing=1, weight 600
SIZE, ORIGIN_X, BASELINE, TRACKING = 46.0, 140.0, 47.0, 1.0


def wordmark_path(fill: str) -> str:
    font = instantiateVariableFont(TTFont(FONT_PATH), {"wght": 600}, overlap=True)
    glyph_set = font.getGlyphSet()
    cmap = font.getBestCmap()
    scale = SIZE / font["head"].unitsPerEm
    x = ORIGIN_X
    cmds = []
    letters = "tasan"
    for i, ch in enumerate(letters):
        glyph = glyph_set[cmap[ord(ch)]]
        pen = SVGPathPen(glyph_set)
        glyph.draw(TransformPen(pen, Transform(scale, 0, 0, -scale, x, BASELINE)))
        d = pen.getCommands()
        if d:
            cmds.append(d)
        x += glyph.width * scale
        if i < len(letters) - 1:
            x += TRACKING
    # end-x useful for tight viewBoxes
    wordmark_path.end_x = x
    d = " ".join(cmds)
    return f'<path fill="{fill}" d="{d}"/>'


def mark(pill: str, bar: str, x: float = 0, y: float = 8, w: float = 120, h: float = 48) -> str:
    # Proportional: bar inset 14, height 4, vertically centred; dot r=10 at centre
    bx, by, bw, bh = x + 14, y + (h / 2) - 2, w - 28, 4
    cx, cy, r = x + w / 2, y + h / 2, 10
    return (
        f'<rect x="{x:g}" y="{y:g}" width="{w:g}" height="{h:g}" rx="{h/2:g}" fill="{pill}"/>'
        f'<rect x="{bx:g}" y="{by:g}" width="{bw:g}" height="{bh:g}" rx="{bh/2:g}" fill="{bar}"/>'
        f'<circle cx="{cx:g}" cy="{cy:g}" r="{r:g}" fill="{TEAL}"/>'
    )


def svg(view, body, w=None, h=None) -> str:
    vb = " ".join(str(v) for v in view)
    size = (f' width="{w}" height="{h}"' if w and h else "")
    return (
        f'<svg xmlns="http://www.w3.org/2000/svg"{size} viewBox="{vb}" fill="none">\n'
        f"{body}\n</svg>\n"
    )


wm_navy = wordmark_path(NAVY)
end_x = wordmark_path.end_x
wm_off = wordmark_path(OFF)
wm_white = wordmark_path(WHITE)
print(f"wordmark ends at x={end_x:.2f} (viewBox width 330, starts 140)")

# Horizontal lockup — same geometry as logo.svg, paths instead of <text>
lockup_navy = mark(NAVY, OFF) + "\n" + wm_navy
lockup_white = mark(OFF, NAVY) + "\n" + wm_off
lockup_white_pure = mark(OFF, NAVY) + "\n" + wm_white

(B / "logo-horizontal.svg").write_text(svg((0, 0, 330, 64), lockup_navy))
(B / "logo-white.svg").write_text(svg((0, 0, 330, 64), lockup_white))
(B / "logo-icon.svg").write_text(svg((0, 0, 120, 48), mark(NAVY, OFF, x=0, y=0)))

# White lockup on a navy rounded-rect background, with quiet padding
PAD_X, PAD_Y, RX = 24, 16, 20
cw, ch = 330 + 2 * PAD_X, 64 + 2 * PAD_Y  # 378 x 96
bg = f'<rect width="{cw}" height="{ch}" rx="{RX}" fill="{NAVY}"/>'
# Use off-white pill + off-white wordmark (brand "white")
shifted = f'<g transform="translate({PAD_X},{PAD_Y})">\n{mark(OFF, NAVY)}\n{wm_off}\n</g>'
(B / "logo-white-on-navy.svg").write_text(svg((0, 0, cw, ch), bg + "\n" + shifted))
print("wrote outlined SVGs")


def render_svg(src: Path, dest: Path, w: int, h: int, scale: int = 3, bg="00000000"):
    dest.parent.mkdir(parents=True, exist_ok=True)
    raw = B / "build" / f"{dest.stem}@{scale}x-raw.png"
    subprocess.run(
        [
            "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
            "--hide-scrollbars", f"--default-background-color={bg}",
            f"--force-device-scale-factor={scale}",
            f"--window-size={w},{h}", f"--screenshot={raw}", src.resolve().as_uri(),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    im = Image.open(raw)
    if im.size != (w, h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    im.save(dest)
    print("png", dest.name, im.size, im.mode)


# Comparison: text logo vs path logo at 3x, 330x64
html_text = f"""<!doctype html><html><head><style>
@font-face{{font-family:Nunito;src:url('{(B/'fonts'/'Nunito-VariableFont_wght.ttf').as_uri()}');font-weight:200 1000}}
html,body{{margin:0;width:330px;height:64px;background:transparent}}
</style></head><body>{(B/'logo.svg').read_text()}</body></html>"""
(B / "build" / "logo-text.html").write_text(html_text)
html_path = f"""<!doctype html><html><head><style>
html,body{{margin:0;width:330px;height:64px;background:transparent}}
</style></head><body>{(B/'logo-horizontal.svg').read_text()}</body></html>"""
(B / "build" / "logo-path.html").write_text(html_path)

def chrome_html(html: Path, dest: Path, w, h, scale=3):
    raw = B / "build" / (dest.stem + "-raw.png")
    subprocess.run(
        [
            "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
            "--hide-scrollbars", "--default-background-color=00000000",
            f"--force-device-scale-factor={scale}",
            f"--window-size={w},{h}", f"--screenshot={raw}", html.resolve().as_uri(),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    im = Image.open(raw)
    if im.size != (w, h):
        im = im.resize((w, h), Image.Resampling.LANCZOS)
    im.save(dest)
    return im

t_im = chrome_html(B / "build" / "logo-text.html", B / "build" / "cmp-text.png", 330, 64, 3)
p_im = chrome_html(B / "build" / "logo-path.html", B / "build" / "cmp-path.png", 330, 64, 3)
# side by side and difference
t_im = t_im.convert("RGBA")
p_im = p_im.convert("RGBA")
# composite both on off-white for visual compare
def on_paper(im):
    bg = Image.new("RGBA", im.size, (244, 241, 234, 255))
    return Image.alpha_composite(bg, im)

pair = Image.new("RGB", (t_im.width, t_im.height * 2 + 20), (244, 241, 234))
pair.paste(on_paper(t_im), (0, 0))
pair.paste(on_paper(p_im), (0, t_im.height + 20))
pair.save(B / "build" / "cmp-text-vs-path.png")

# pixel diff of RGB on paper
import numpy as np
a = np.array(on_paper(t_im).convert("RGB"), dtype=np.int16)
b = np.array(on_paper(p_im).convert("RGB"), dtype=np.int16)
d = np.abs(a - b)
print("max channel diff", int(d.max()), "mean", float(d.mean()), "pixels >8", int((d.max(axis=2) > 8).sum()), "of", d.shape[0]*d.shape[1])
# save amplified diff
diff_vis = np.clip(d * 8, 0, 255).astype(np.uint8)
Image.fromarray(diff_vis).save(B / "build" / "cmp-diff.png")

# --- PNG exports 1x / 2x for the three new logos ---
# horizontal & icon: transparent, 2px pad at 1x so pill antialias isn't clipped
def export_lockup(svg_name, base, vw, vh, pad=2):
    src = B / svg_name
    for scale, suffix in ((1, ""), (2, "@2x")):
        w, h = (vw + 2 * pad) * scale, (vh + 2 * pad) * scale
        # wrap svg in html with padding
        html = f"""<!doctype html><html><head><style>
html,body{{margin:0;width:{vw+2*pad}px;height:{vh+2*pad}px;background:transparent}}
svg{{display:block;margin:{pad}px}}
</style></head><body>{src.read_text()}</body></html>"""
        hp = B / "build" / f"{base}{suffix}.html"
        hp.write_text(html)
        chrome_html(hp, B / f"{base}{suffix}.png", vw + 2 * pad, vh + 2 * pad, scale=3)
        # chrome_html already resizes to window size; we asked window = 1x css pixels
        # but we want the bitmap at 1x or 2x of (vw+2pad). Fix: render at `scale` device factor
        # equal to the export scale, window = css size.
    # redo properly
    for exp in (1, 2):
        css_w, css_h = vw + 2 * pad, vh + 2 * pad
        html = f"""<!doctype html><html><head><style>
html,body{{margin:0;width:{css_w}px;height:{css_h}px;background:transparent}}
svg{{display:block;width:{vw}px;height:{vh}px;margin:{pad}px}}
</style></head><body>{src.read_text()}</body></html>"""
        hp = B / "build" / f"{base}-{exp}x.html"
        hp.write_text(html)
        raw = B / "build" / f"{base}-{exp}x-raw.png"
        subprocess.run(
            [
                "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
                "--hide-scrollbars", "--default-background-color=00000000",
                f"--force-device-scale-factor={exp}",
                f"--window-size={css_w},{css_h}", f"--screenshot={raw}", hp.resolve().as_uri(),
            ],
            check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        im = Image.open(raw)
        target = (css_w * exp, css_h * exp)
        if im.size != target:
            im = im.resize(target, Image.Resampling.LANCZOS)
        name = f"{base}.png" if exp == 1 else f"{base}@2x.png"
        im.save(B / name)
        print("export", name, im.size, im.mode)

export_lockup("logo-horizontal.svg", "logo-horizontal", 330, 64, pad=2)
export_lockup("logo-icon.svg", "logo-icon", 120, 48, pad=2)

# white-on-navy already has its own bg, no extra pad; 1x = viewBox 378x96
for exp, name in ((1, "logo-white-on-navy.png"), (2, "logo-white-on-navy@2x.png")):
    src = B / "logo-white-on-navy.svg"
    w, h = cw, ch
    html = f"""<!doctype html><html><head><style>
html,body{{margin:0;width:{w}px;height:{h}px;background:transparent}}
svg{{display:block;width:{w}px;height:{h}px}}
</style></head><body>{src.read_text()}</body></html>"""
    hp = B / "build" / f"won-{exp}x.html"
    hp.write_text(html)
    raw = B / "build" / f"won-{exp}x-raw.png"
    subprocess.run(
        [
            "google-chrome", "--headless=new", "--no-sandbox", "--disable-gpu",
            "--hide-scrollbars", "--default-background-color=00000000",
            f"--force-device-scale-factor={exp}",
            f"--window-size={w},{h}", f"--screenshot={raw}", hp.resolve().as_uri(),
        ],
        check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
    )
    im = Image.open(raw)
    target = (int(w * exp), int(h * exp))
    if im.size != target:
        im = im.resize(target, Image.Resampling.LANCZOS)
    # drop unused alpha if fully opaque
    im.save(B / name)
    print("export", name, im.size, im.mode)

# also refresh logo-white.png at 2x (paths), plus 1x
export_lockup("logo-white.svg", "logo-white", 330, 64, pad=2)

print("done outlines + pngs")
