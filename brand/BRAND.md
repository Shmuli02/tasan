# Tasan brand sheet

Calm, Nordic, honest, visual-first. Very little text. App UI detail lives in `UI_STYLE.md`, `APP_DESIGN.md` and `tasan-tokens.css`; this sheet is the source for meaning, logo, contrast, voice and favicon.

## Name and mark

*Tasan* is Finnish for “even, level, exactly.” The mark is a spirit level: a navy rounded pill, an off-white bar, and a centred teal bubble. The bubble sits dead-centre when the surface is even — care should not tilt with the postcode. Wordmark is lowercase **tasan** in Nunito 600, letter-spacing +1, set to the right of the mark.

## Palette

| Token | Hex | Use |
|---|---|---|
| Navy | `#16233F` | Logo pill, headings, primary text, map “lowest share” |
| Teal | `#3A9A9A` | Logo dot, graphic accent, chips on navy |
| Teal ink | `#2A7676` | Teal *text* on light grounds (`--tz-teal-700`) |
| Off-white | `#F4F1EA` | Paper, logo-white pill and wordmark |

### Contrast (WCAG AA: 4.5 normal text, 3.0 large text / UI)

Computed from sRGB relative luminance, this kit.

| Pair | Ratio | AA normal | AA large |
|---|---:|---|---|
| Navy on off-white, and reverse | **13.83** | Pass | Pass |
| White `#FFFFFF` on navy, and reverse | **15.60** | Pass | Pass |
| Teal ink `#2A7676` on off-white | **4.71** | Pass | Pass |
| Teal ink on white | **5.31** | Pass | Pass |
| Teal `#3A9A9A` on navy | **4.66** | Pass | Pass |
| Teal `#3A9A9A` on off-white | **2.97** | **Fail** | **Fail** — graphics only, never body text |
| White on teal `#3A9A9A` | **3.35** | Fail | Pass (large only) |
| Teal ink on navy | **2.94** | Fail | Fail — do not use |

Safe text pairings: navy ↔ off-white or white; teal ink `#2A7676` on off-white or white; teal `#3A9A9A` on navy (or as a fill behind navy text). Do not set `#3A9A9A` as text on paper.

## Map scale

Sequential navy → light teal, colour-blind safe (monotonic lightness). Lowest curative-treatment share is darkest. Official tokens in `tasan-tokens.css`:

`#16233F` → `#2D6B7D` → `#4F9C9C` → `#86BFB9` → `#BCDCD6` → `#E6F2EF`

Bins used on the cover and social card (crude share, 2019–2023, Taulukko 11): `<21` · `21–24` · `24–27` · `27–30` · `30–33` · `≥33`. No data (Åland): `#D9D4C9` + 45° hatch. On paper, stroke counties with a soft warm line (`#D4CFC5`) so the lightest class still reads; the app token stroke is white.

## Typography

- **Wordmark:** Nunito 600, lowercase, letter-spacing +1. Fallback: Varela Round, Helvetica Neue, Arial.
- **Hero / KPI numbers:** Nunito 800, tabular (`~65`).
- **Headlines:** Nunito 700.
- **UI / body:** Inter 400 / 600, as in `UI_STYLE.md`. Fallback: system-ui, sans-serif.
- Do not use Georgia, Source Serif, or a gold serif “T” in new brand materials.

## Voice — 5 do / don’t

**Do**
- Say “about” / “noin” for every `computed_by_tasan` or `chart_estimate` number, and carry the caveat (shortened is fine, dropped is not).
- Put the fact id and source (table + year) next to every figure.
- Call Verda “EU-hosted inference,” never “Finland-hosted.”
- Prefer a number and a map over a paragraph; keep screens around 40 words.
- Label crude vs age-adjusted vs chart estimate. `~65 a year` is crude, not stage-adjusted.

**Don’t**
- Don’t say “lives saved,” “deaths prevented,” or “patients denied treatment” (`nodata_lives_saved`).
- Don’t claim an existing AstraZeneca–county pilot in Finland.
- Don’t use the “17% earliest stage” figure.
- Don’t present day 28 or 80% as official targets (Tasan design choices). The six-week reference is THL Ohjaus 21/2016, watermarked outdated.
- Don’t drop “about” from `~65` / `~12`, or describe them as age- or stage-adjusted.

## Logo do / don’t

**Do:** keep the lockup on one line (mark, then wordmark); use lowercase **tasan**; keep the teal bubble centred on the bar; give clear space of at least half the pill height; use `logo-white` (off-white pill, navy bar, teal dot, off-white wordmark) on navy.

**Don’t:** don’t write the wordmark as “Tasan” or in caps; don’t recolour or offset the dot (off-centre means the level is off); don’t stretch, outline, or drop-shadow the pill; don’t place the navy logo on navy; don’t use the old gold serif “T” favicon.

## Favicon check

The live app favicon (`app/public/favicon.svg` and `app/dist/favicon.svg`) is a **gold serif “T”** (`#C9A227` on `#1A2744`, Georgia). That is off-brand: gold is not in the palette, the type is not Nunito, and the capital T breaks the lowercase wordmark.

Replacement assets, ready to drop in when the builder is free (this kit does not edit `app/`):

- `brand/favicon.svg` — navy rounded square, level bar, centred teal dot (use at 32 px and up)
- `brand/logo-icon-small.svg` — simplified 16-unit icon (2 px bar, 4 px-radius bubble)
- `brand/favicon-16.png` (from `logo-icon-small.svg`), `favicon-32.png`, `favicon-48.png`, `favicon-180.png`, `favicon-512.png`
- `brand/favicon-check.png` — 16 / 32 / 48 at actual size and at 8×

Verdict: the 1.5 px bar in `favicon.svg` does **not** survive at 16 px (it antialiases to muddy grey stubs). Use `logo-icon-small.svg` at 16 px, where the level reads clearly. At 32 px and 48 px the standard favicon bar is intact.

## App alignment notes

Checked against `app/screenshot-hero-viewport.png` and `app/src/index.css`. No app files were edited.

- **Paper is on-brand.** Body background is `#F4F1EA`.
- **Wordmark is title case “Tasan,”** not lowercase **tasan**.
- **Type is off-brand.** The app uses Inter for UI and Source Serif 4 for the hero number (`.serif` / `.hero-number`). Brand hero numerals are Nunito 800.
- **Navy and teal are close, not exact.** App navy is `#1A2744` (brand `#16233F`); app teal is `#0E6A67` (darker and greener than `#3A9A9A`). Ink is `#151C24`.
- **Map is off-brand and not colour-blind safe.** The live hero uses a red–orange–gold–green diverging ramp (`--color-map-0..4`: `#9A2F2A` … `#0E6A67`). Brand / tokens specify the sequential navy→teal scale above, with Lapland darkest.
- **Gold, rose and green** appear as UI status colours. Keep them for status-with-icon only, as in `UI_STYLE.md`; do not use them on the map or logo.
- **Footer badge** “AI on Verda · EU-hosted” matches Decision 5. Prefer “EU-hosted inference” in any longer line.
- **Favicon** is the gold serif T, as above.

## Files

Outlined wordmark (Nunito 600 paths, no `<text>`): `logo-horizontal.svg` + `logo-horizontal.png` / `logo-horizontal@2x.png` · `logo-white.svg` + `logo-white.png` / `logo-white@2x.png` · `logo-white-on-navy.svg` + `logo-white-on-navy.png` / `logo-white-on-navy@2x.png` · `logo-icon.svg` (mark only) + `logo-icon.png` / `logo-icon@2x.png` · `logo-icon-small.svg` (16 px).

`logo.svg` is unchanged and still contains `<text>` (the app may reference it; `logo-horizontal.svg` is the outlined equivalent). `mark.svg` / `mark.png` (512).

Favicon: `favicon.svg`, `favicon-16.png` (from the small icon), `favicon-32.png`, `favicon-48.png`, `favicon-180.png`, `favicon-512.png`, `favicon-check.png`.

Also: `brand-sheet.png` (1920×1080) · `submission-cover.png` (1920×1080) · `social-card.png` (1080×1080) · `TAGLINES.md`
