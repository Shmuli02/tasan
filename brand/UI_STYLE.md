# Tasan UI style — quick card for JN Builder (v1, 2026-11-14)
Tokens: `brand/tasan-tokens.css` (CSS vars `--tz-*` + ready classes `.tz-kpi`, `.tz-chip-src`, `.tz-badge--*`, `.tz-pulse`). Full spec + per-tab layouts: `brand/APP_DESIGN.md`.
Feel: premium Nordic health-tech. White cards on warm paper, navy ink, one teal accent, dense but calm. Numbers big, words few.

## Fonts (Google Fonts link is the first line of tasan-tokens.css)
| Use | Font | Size / weight |
|---|---|---|
| Hero number (~65) | Nunito 800, tabular | 72px / lh 1 |
| KPI tile number | Nunito 800, tabular | 44px / lh 1 (unit 18px Inter 700 muted) |
| Screen title (H1) | Nunito 700 | 32px |
| Card title (H2 / H3) | Inter 600 | 22px / 17px |
| Body | Inter 400 | 15px / lh 1.5 |
| KPI label, axis label, tabs | Inter 600 | 13px (tabs 14px) |
| Chips, badges | Inter 700 caps +0.06em | 11.5px |
| Console feed, patient ids, timers | JetBrains Mono 400/500, tabular | 13px (clock centre 28px 600) |
Every number: `font-variant-numeric: tabular-nums lining-nums` (class `.tz-num`). Projector (1920): keep sizes; laptop (1440): KPI 40px, hero 64px.

## Colour
Brand: navy `#16233F` · teal `#3A9A9A` (text-on-light teal `#2A7676`) · paper `#F4F1EA` · card `#FFFFFF`.
Ink: `#141B2B` body · `#3E4759` secondary · `#6B7385` labels · `#9AA1AF` ticks · lines `#E4DFD4` / grid `#EEEAE1`.
Status (always icon + word, never colour alone):
| Status | Light UI fg / bg | Console (dark) | Meaning |
|---|---|---|---|
| ok | `#2A7F62` / `#E2F1EA` | `#4CC2A4` | on track |
| risk | `#B38A00` / `#FBF1CF` | `#E6C25A` | watch (day 21–27) |
| alert (amber) | `#D9822B` / `#FCE9D6` | `#F2A65A` | day-28 alert fired |
| critical | `#C2412D` / `#F8E0DA` | `#FF6B5A` | past 6-week target |
| EXAMPLE badge | `#7A5AA6` / `#EFE8F7`, dashed border | same | simulated data |

## Map ramp (6 steps, light → dark, colour-blind safe: monotonic lightness, teal → navy)
`#E6F2EF` `#BCDCD6` `#86BFB9` `#4F9C9C` `#2D6B7D` `#16233F`
Highest curative share = lightest; **lowest share = darkest (Lapland = `#16233F`)**. No data = `#D9D4C9` + 45° hatch (`#B9B2A4`, 1px every 6px). County stroke white 1px; selected county 2.5px `#D9822B` outline. Legend = 6 swatches with end labels only ("lower ↔ higher curative share").
Charts: focus `#16233F`, comparison `#3A9A9A`, others `#C9C3B6`, national line dashed `#D9822B`, target line `#2A7F62`, CI whiskers `#3E4759` 1.5px.

## Shape
Radius: chips/tabs/badges pill · buttons/rows 10px · cards 16px · map/hero panel 22px.
Shadows: card `0 1px 2px rgba(22,35,63,.06), 0 1px 1px rgba(22,35,63,.04)` + 1px border `#E4DFD4`; hover/popover `0 4px 14px rgba(22,35,63,.07)`; modal `0 14px 40px rgba(22,35,63,.12)`.
Spacing 4px base: 4 8 12 16 20 24 32 40 48. Card padding 20×24, gutter 24, page padding 32.
Icons: **Lucide** (`lucide-react`), stroke 1.75, 18px in UI / 16px in chips; colour = current text. Suggested: `map`, `building-2`, `route`, `activity`, `sliders-horizontal`, `clipboard-check`, `sparkles` (Ask Tasan), `info` (source), `alert-triangle`, `clock`, `scan` (CT), `microscope` (biopsy), `users` (MDT).

## Tasan Live console (dark, looks like real ops software)
- Surface: page `#0E1628`, panels `#16233F`, raised rows `#1D2D4F`, borders `#2A3B60`, radius 16, shadow `0 18px 50px rgba(5,10,22,.45)`.
- Text `#E7ECF5` / `#A9B4C8` / `#6F7D97`; all data JetBrains Mono 13px tabular.
- Event feed row: `14:02:11  ●  P-0193  CT booked → day 9` — time in `#6F7D97`, 8px status dot, id in teal `#5CC4C4`, 32px row height, 1px `#2A3B60` divider, newest row fades in from top (200ms).
- Alert row: 4px left bar in status colour + tinted bg (`rgba(242,166,90,.12)` amber, `rgba(255,107,90,.12)` critical), mono "DAY 28" chip, blocker icon + word, "Assign navigator" ghost button.
- Day clock ring: SVG 120px, track `#2A3B60` 10px stroke, progress arc teal → amber at day 21 → red at day 42 (6 wk); centre "D 28" 28px mono 600, sub "of 42" 11px. Mini 28px rings in patient rows.
- Live pulse dot: 9px `#4CC2A4` with expanding ring (`.tz-pulse`), next to "LIVE · EXAMPLE".
- Whole console carries a visible `EXAMPLE` badge top-right: all patients/events are simulated.

## Tabs & chrome
Top bar 64px white, bottom border `#E4DFD4`: logo (height 28) · tabs **Overview · Counties · Pathway · Tasan Live · Simulate · Pilot** (Inter 600 14px, active = navy text + 3px teal underline pill) · right: FI/EN pill toggle · `AI on Verda · EU-hosted` badge.
**Ask Tasan** side panel on every tab: right, 380px (340px at 1440), white, left border, header with `sparkles` icon + current context chip (e.g. "Lapland · Overview").
Rules: real numbers only from `data/facts.json` with a source chip; chart estimates say "about" + `CHART ESTIMATE` badge; anything simulated gets `EXAMPLE`. Never "lives saved".
