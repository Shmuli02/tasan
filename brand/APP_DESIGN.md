# Tasan app design spec v1 (for JN Builder) — 2026-11-14
Quick card: `brand/UI_STYLE.md` (fonts, colours, map ramp, icons, console look). Tokens: `brand/tasan-tokens.css`.
Mockups (1920×1080): `brand/mockup-overview.png`, `brand/mockup-live.png`, `brand/mockup-howwebuilt.png` (fan-out) and `brand/mockup-howwebuilt-open.png` (opened note). Source: `brand/mockups/{overview,live,howwebuilt,howwebuilt-fan}.html`, `app.css`, `overview.css`, `live.css`, `howwebuilt.css`. Rebuild with `python3 brand/mockups/build.py`. Render Overview/Live with `render.py` (Playwright). Render How we built it with `python3 brand/mockups/howwebuilt.py --render` (headless Chrome, same as `brand/build/build.py`).
Feel: premium Nordic health-tech. Every screen is full: KPI row, then a 3-column grid of charts and cards. Labels are short and there are no paragraphs.

## 0. Hookup (Tailwind v4 is already in app/src/index.css)
```css
@import "../../brand/tasan-tokens.css";   /* or copy the file into src/ */
@theme {
  --font-sans: "Inter", ui-sans-serif, system-ui, sans-serif;
  --font-display: "Nunito", "Inter", sans-serif;
  --font-mono: "JetBrains Mono", ui-monospace, monospace;
  --color-navy: #16233F; --color-teal: #3A9A9A; --color-teal-ink: #2A7676; --color-paper: #F4F1EA;
  --color-ink: #141B2B; --color-muted: #6B7385; --color-line: #E4DFD4; --color-card: #FFFFFF;
  --color-ok: #2A7F62; --color-risk: #B38A00; --color-alert: #D9822B; --color-critical: #C2412D; --color-example: #7A5AA6;
  --color-map-1: #E6F2EF; --color-map-2: #BCDCD6; --color-map-3: #86BFB9; --color-map-4: #4F9C9C; --color-map-5: #2D6B7D; --color-map-6: #16233F;
  --color-console: #0E1628; --color-console-surface: #16233F; --color-console-raised: #1D2D4F; --color-console-line: #2A3B60;
}
```
The current app uses the red→green map ramp and Source Serif. Replace both: the ramp with the teal→navy sequential ramp (colour-blind safe, lowest share = darkest), the serif with Nunito for display/numbers and Inter for UI. Nunito is also bundled at `brand/fonts/Nunito-VariableFont_wght.ttf`, so it works offline.

## 1. Layout grid
```
┌ top bar 64px (white) ─ logo 30px · 6 tabs · ……… · FI/EN · [AI on Verda · EU-hosted] ┐
├ main (paper, padding 24/32) ───────────────────────────────┬ Ask Tasan panel ───────┤
│ header row 56px: kicker + H1 (≤7 words) · view toggles     │ 380px @1920            │
│ KPI row: 4 tiles, 162px tall (hero tile 1.45fr)            │ 340px @1440            │
│ content: 12-col grid, gap 20 (typical 4 / 5 / 3 columns)   │ collapsible to a 56px   │
│ fills to the bottom: no page scroll at 1920×1080            │ rail (sparkles icon)    │
└────────────────────────────────────────────────────────────┴────────────────────────┘
```
```css
.app{display:grid;grid-template-rows:var(--tz-topbar-h) 1fr;height:100vh}
.shell{display:grid;grid-template-columns:1fr var(--tz-panel-w);min-height:0}
.main{padding:24px var(--tz-page-pad);display:flex;flex-direction:column;gap:20px;overflow:auto}
.content{display:grid;grid-template-columns:repeat(12,1fr);gap:var(--tz-gutter);flex:1;min-height:0}
@media (max-width:1600px){:root{--tz-panel-w:340px;--tz-page-pad:24px;--tz-gutter:16px;--tz-fs-kpi:40px;--tz-fs-kpi-xl:64px}}
@media (max-width:1280px){.shell{grid-template-columns:1fr}.panel{position:fixed;right:0;top:64px;bottom:0;width:360px;transform:translateX(100%)}}
```
Breakpoints: **1920×1080 projector** is the design target (fonts never below 12px, chart labels ≥11px). **1440×900 laptop** uses the media query above: the KPI row stays 4-up and the content grid goes to 2 columns with the third card stacked under. Below 1280 the panel turns into a drawer.

## 2. Components (CSS ready in tasan-tokens.css / mockups/app.css)
**KPI tile** (`.tz-kpi` → `__label`, `__value` + `<small>` unit, `__delta`, `__foot` with source chips). The number is Nunito 800, 44px, tabular. The label goes above it, 13px muted. The comparison line sits under it: "National **27.0%**". The foot holds source chips and a measure badge. Hero variant: navy fill, white 76px number, label to the right (`.kpi.hero` in overview.css). Do not compute a delta unless facts.json has it (usage rule: no new arithmetic).

**Source chip** (`.tz-chip-src` / `.src`): pill, 22px, mono 11px fact id with a teal dot. On click it opens a popover with `statement_en`, `source_table`, `caveat` and a link to `source_url`. Popover: white, `--tz-sh-3`, radius 12, max 360px. Global "Sources" toggle in the header: when off, chips collapse to a 6px dot (still clickable).

**Badges** (`.tz-badge--*`): `EXAMPLE` (purple, dashed border; on all simulated data, tab label, chat, Live console). `CHART ESTIMATE` (`.b-est`, slate) whenever measure_type = chart_estimate; the number gets a "~" prefix ("about"). `COMPUTED BY TASAN` (`.b-comp`, teal tint) for computed_by_tasan. `DATA GAP` / `No public data` (`.b-nodata`, near-black #2B2F3A) for no_public_data facts. `AI on Verda · EU-hosted` (`.tz-badge--verda`, navy + teal dot), always in the top bar and in the panel footer.

**Charts** (SVG or Recharts, same tokens):
- Ranked bar / gap bar: 13px bars on a 24px row pitch, radius `0 4 4 0`, colour = the county's map ramp step (ties the bar to the map). Selected county: bold name + 8px amber dot. National reference: 2px dashed `--tz-chart-national` vertical line labelled "National 27.0%". Grid: 1px `--tz-chart-grid` at 10% steps. Axis text 11px `--tz-chart-axis`. Value labels only where a fact exists.
- Line: 2.5px teal line, area gradient 35%→0% opacity, end dot 4.5px with a 2px surface ring, dashed baseline. No chart junk.
- CI whiskers: 2px line plus 12px end caps in `--tz-chart-ci`, 14px dot with a 2px white ring (focus navy, comparison teal), label above the dot as "~16.2" in 11.5px bold. Footnote: "Read from report chart (±1 pp) · 95% intervals don't overlap".
- Choropleth legend: 6 swatches 26×10 joined into one bar, "lower ← → higher" end labels only, plus a hatched "No public data" swatch. Selected county: 2.5px `--tz-map-selected` outline drawn on top. Helsinki-region inset (Uusimaa counties 01–04, 90) in a small white card, so the capital-area counties stay visible.
- "Chart estimate" labelling: the `CHART ESTIMATE` badge sits in the card header, numbers carry "~", and the caveat goes in the footnote. Never present a chart estimate without all three.

**Cards**: `.tz-card` (white, 1px `#E4DFD4`, radius 16, `--tz-sh-1`, padding 20×24). Header = 17px title + 13px muted sub on the left, source chip or badge on the right.
- Recommendation card: 4px left bar (teal = lead/T3, navy = T1, slate = T2), Lucide icon in a 34px tile, title 17px, then a 2×2 mini-grid of Owner / Cost / KPI / Stop-go (label 11px caps muted, value 14px 600), Goal 3 chip (e.g. `G3 · target times`), source chips. Max ~25 words.
- County card: county name + mini map silhouette (step colour), big share number with an "of national" comparison line, rank pill "#22 of 22" (only if computed from the same source table; otherwise omit), CI whisker strip, data-gap chips, primary button "Generate pilot brief".

## 3. Tasan Live console (see mockup-live.png, live.css)
Dark surface: main `#0E1628`, cards `#16233F` with 1px `#2A3B60` borders, radius 16. Text `#E7ECF5` / `#A9B4C8` / `#6F7D97`. All data is JetBrains Mono, tabular.
- Header: title, then context "Lapland · lung pathway / navigator console", `LIVE` pill (pulse dot), `EXAMPLE · simulated patients` badge, and a playback dock on the right (pause/play 36px teal button, 1×/8×/32× segmented control, pilot-day scrubber with a day-28 tick and "stop/go D90").
- KPI tiles (dark): label, 34px mono number, 92×34 sparkline, mono delta line.
- Patient table: 40px rows. Columns: mini day-ring 28px · id (teal) · `D28` · 5-segment step bar (done teal / current white / todo line) · blocker (icon + word in status colour) · navigator avatar · status pill. Selected/alert row: amber 3px inset left bar + `rgba(242,166,90,.09)` fill.
- Day clock ring (SVG 128px, stroke 11): track `#2A3B60`, arc colour by day (<21 ok `#4CC2A4`, 21–27 risk `#E6C25A`, 28–41 alert `#F2A65A`, ≥42 critical `#FF6B5A`), ticks at D21/D28, centre `D28` 28px plus "of 42 · 6 wk", soft glow in the arc colour. Animation: the arc grows over 600ms when the patient is selected.
- Alert rows: 4px colour bar, mono id + `DAY 28` chip, blocker icon + reason, ghost "Assign" button. Feed rows: `09:42:07 ● P-0207 DAY-28 ALERT CT not booked`. The newest row slides in with a teal gradient highlight that fades over 2s.
- Pulse dot: `.tz-pulse` (prefers-reduced-motion respected).

## 4. Ask Tasan side panel
Header: 30px navy tile with the Lucide `sparkles` icon, "Ask Tasan" in Nunito 700, `EXAMPLE` badge while answers are cached/mocked, and a context chip "Lapland · Overview" (updates with tab + county). Bubbles: user = navy, right, radius 16 with a 5px tail corner; AI = `#FBFAF6` with a 1px line, left. Every sentence ends with citation pills (`.cite`, mono 10.5px, teal tint, fact id; click opens the same source popover). Meta row: shield icon + "N facts cited · source report". **Refusal style**: transparent bubble, 1px dashed `#9AA1AF` border, caps header with the `eye-off` icon and "No sourced answer" / "No public data", one sentence, plus the matching `nodata_*` pill. It is never red and never apologetic. Suggestion chips: white pills above the input, 3 per context (Overview: "Draft Lapland pilot brief", "Where does data go dark?", "Compare Kymenlaakso"; Live: "Summarise today's alerts", "Who needs a navigator?", "Draft weekly CMO note"). Input is 50px with a teal send button. Footer: "Cites data/facts.json only · refuses without data · AI on Verda · EU-hosted". On Tasan Live the panel switches to its dark variant (`.panel.dark`).

## 5. Per-tab layouts (12-col; each fills 1920×1080 without scrolling)
1. **Overview** (mockup): header "Curative care is not even across Finland" + Crude/Age-adjusted toggle + Sources. KPIs: hero ~65/yr (`people_number_national`) · Lapland 18.5% vs national 27.0% (`lung_curative_lapland`, `lung_curative_national`) · ~12/yr Lapland (`people_number_lapland`) · "0 public reports of 6-week compliance" (`nodata_regional_target_compliance`). Content: map 4 col · ranked bars 5 col · right 3 col = age-adjusted CI card (4 chart-estimate facts) + "Where the data goes dark" strip.
2. **Counties**: left 3 col = searchable county list with step swatch and share. Centre 6 col = county card large (share vs national bar, CI whiskers, age-adjusted men/women where facts exist, survival/stage facts where available, e.g. `lung_surv1y_north` for collaborative areas, clearly labelled with the region type). Right 3 col = data-gap list (`nodata_*` chips) + big "Generate pilot brief" button → Pilot tab.
3. **Pathway**: full-width horizontal flow Referral → Imaging → Biopsy → MDT → Treatment (icon nodes, 1-week step targets `thl_diagnostic_steps_1wk`, 6-week span bar `thl_6wk_referral_to_treatment`). Steps with no public data are drawn as black boxes with "No public data" (`nodata_referral_to_diagnosis`, `nodata_dx_to_treatment_by_county`). The one lit segment, dx→surgery 13.5 vs 46.0 d, is a collaborative-area fact and always carries the same-day-surgery caveat (`lung_same_day_surgery_caveat`). Bottom row = 3 Goal 3 indicator cards (`g3_indicator_*`).
4. **Tasan Live** (mockup, EXAMPLE): KPI row 8 col + feed 3 col full height. Patient table 7 col · alert column 4 col (clock ring card + queue). Bottom row: blockers + 6-week trend + "where time is lost". Everything simulated → EXAMPLE badge in the header, tab label and card subtitles.
5. **Simulate (Verda)**: left 3 col = controls card (navigator on/off, day-28 alert on/off, CT / biopsy / MDT capacity sliders with teal thumbs, county select). Centre 6 col = per-county dot + interval chart of "share treated within 6 weeks" for the scenario vs **zero-effect** (always drawn, grey dashed). Right 3 col = scenario KPI tiles + "Computed on Verda" card (job id, runtime, `AI on Verda · EU-hosted`). Sim output = model output → `EXAMPLE / SIMULATION` badge, never "lives saved".
6. **Pilot**: document-style white sheet 8 col (A4 proportion, title "Lapland 90-day Tasan pilot — DRAFT", owner/cost/KPI tiles, 90-day timeline bar: W0 sign · W1–2 clock + navigator · D28 alerts live · D90 stop/go). Right 4 col = KPI targets + stop/go criteria cards + "Download PDF" primary button (`download` icon). Content comes only from recs/pilot_brief_lapland.*.

## 6. Numbers used in the mockups → fact ids
| Shown | Fact id | Type |
|---|---|---|
| ~65 /yr (wording from statement_en) | people_number_national | computed_by_tasan |
| ~12 /yr Lapland | people_number_lapland | computed_by_tasan |
| 18.5% Lapland · 27.0% national | lung_curative_lapland · lung_curative_national | published |
| 18.9% · 19.3% · 33.0% · 35.6% bar labels | lung_curative_south_karelia · _kymenlaakso · _helsinki · _vantaa_kerava | published |
| ~16.2 [12.7–20.4], ~29.8 [24.2–36.1], ~23.1 [17.9–29.0], ~39.7 [33.1–47.0] | lung_curative_agestd_{lapland,vk}_{men,women} | chart_estimate |
| "0" public 6-week reports | nodata_regional_target_compliance | no_public_data |
| 6 weeks, 1 week per step | thl_6wk_referral_to_treatment · thl_diagnostic_steps_1wk | published |
| Map colours + unlabelled bar lengths (22 counties) | data/csv/lung_report2026_treatment_by_wsc.csv (Taulukko 11, same source as the facts above) | published, not individually in facts.json |
| Everything on Tasan Live (patients, days, 14, 9/14, 3, 33 d, feed, trend, blockers) | none | **EXAMPLE** |
| Chat transcripts | quote facts above | **EXAMPLE chat** |

## 7. How we built it page
New 7th tab (Lucide `layers` icon, already in `brand/mockups/icons.py`). Same chrome as the other tabs: 64px top bar, logo from `brand/logo-horizontal.svg`, `AI on Verda · EU-hosted` badge, Ask Tasan panel 380px @1920. No KPI row. The main column is header → hero → pipeline, and it must fill 1920×1080 without scrolling.

```
┌ top bar (7 tabs, How we built it active) ─────────────────────────────────────┐
├ kicker + H1 "How we built it" + SYNTHETIC / Qwen3-32B / EU-hosted chips ──────┤
├ hero: paper stage (1fr) ──────────────────────────────┬ rail 320px ───────────┤
│   warm sunk well, radius 22. A fan of the 10 notes.   │ Event types legend    │
│   Open state: SYN-P0051-oncology_note-04 is large,    │ Extracted events list │
│   slightly rotated (−1.2°), highlights + stamp.       │ Day-28 clock (gold vs │
│   The other nine stay in a left-hand fan.             │ note_date)            │
│   Fan state: all ten in one arc, chosen note in front,│ (rail hidden in fan)  │
│   still sheet-sized.                                  │                       │
├ pipeline card, 132px: Notes → Extract → Events → Clock ───────────────────────┤
└───────────────────────────────────────────────────────────────────────────────┘
```

**Copy rules.** At most ~40 words of prose on the screen (apart from document text). Every sheet is SYNTHETIC. Do not say "lives saved". Do not claim an AstraZeneca–county pilot. For Verda say "EU-hosted inference", never "Finland". Read current `source_now` / `source_after_gpu` from `verda/extract/samples.json` — as of this mockup both are `qwen3-32b` (`model_name`: `Qwen/Qwen3-32B-AWQ`). Label regex as the non-LLM floor, not as the live extractor. Clock numbers (`day_count`, `alert`) come from the note object and are computed from **gold** events vs `note_date` (see SAMPLES.md); do not present them as model output.

**Data.** The 10 papers are the notes in `verda/extract/samples.json` (same ids as `SAMPLES.md` / `app_export.json`). Use the schema as written: event `type` enum is `referral_received`, `ct_done`, `biopsy_done`, `pathology_result`, `mdt_decision`, `treatment_decision`, `treatment_start`. Do not invent types. Each event has `type`, `date`, `evidence_span`, `start`, `end`, `confidence`.

**What drives the highlights.** On the open note, wrap `text[start:end]` from **`model_events`** (fall back to `gold_events` if `model_events` is missing). Offsets are character offsets into the full `text` field, which is the corpus file including the SYNTHETIC header. The clinical body starts after the second `=======` rule (`body_pos` in `howwebuilt.py`, around index 550–590). Skip any event with `start < 0` or `end < 0` — that happens when `evidence_span` does not occur verbatim in `text` (example in this snapshot: `SYN-P0001-discharge_summary-05` / `referral_received` has `start`/`end` = −1 because the model span says "Specialist referral" and the note text has the typo "Specialist erferral"). Render marks as `<mark class="hl hl-{type}" data-type data-date data-start data-end>`.

The mockup opens `SYN-P0051-oncology_note-04` (Finnish `oncology_note`, late_wait, `day_count` 53, `alert` true, six model events; `treatment_start` is absent because treatment has not started). On this note, model events match gold (dates and offsets). That is not true of every showcase note: v2 `SYN2-P0014-ct_report-02` disagrees on both dates; Swedish `SYN-P0002-mdt_minutes-03` disagrees on the `pathology_result` date. Do not silently "correct" model events to gold.

**Paper tokens** (also in `howwebuilt.css`):
```css
--tz-sheet: #F8F5EE;        /* slightly lighter than app paper #F4F1EA */
--tz-sheet-edge: #E7E1D4;
--tz-sheet-meta: #F3F0E8;   /* compact file-header band on the open sheet */
--tz-sh-sheet: 0 1px 0 rgba(255,255,255,.7) inset, 0 10px 28px rgba(22,35,63,.12), 0 2px 6px rgba(22,35,63,.08);
--tz-sh-sheet-open: 0 1px 0 rgba(255,255,255,.8) inset, 0 22px 50px rgba(22,35,63,.18), 0 6px 16px rgba(22,35,63,.10);
```
Sheet typography: JetBrains Mono 10.5px closed / 12px open, line-height 1.55–1.6, ink `#141B2B` / `#3E4759`. Navy file-tab at the top edge with the raw `doc_type` string; meta row is `LANG · note_date`; v2 notes get a small `v2` chip. Footer: `note_id`. Stage surface is a sunk well (`#EDE9E0` → `#E6E1D6`, radius 22) with an elliptical floor shadow.

**Stamps.** Every sheet, including those still in the pile, must show `SYNTHETIC · NOT A REAL PATIENT`. Rubber-stamp look: Inter 800, 8.5–10.5px, letter-spacing 0.07em, uppercase, two lines; ink `#9B4A42` (muted red, 5.59:1 on `#F8F5EE`); 2px border plus 1px inset ring; radius 3px; opacity 0.82; `mix-blend-mode: multiply`; rotation about ±7–14°. Closed sheets: stamp sits on the top edge (fan state, top-right) or on the visible left strip (open state, so the pile does not hide it). Open sheet: lower left, over the "Kirjaaja" footer, never over a highlighted span.

**Highlight colours** (soft marker fill + dark text, colour-blind safe, no red/green pairing). Text-on-fill contrast is WCAG AA in every row. A type not present on the open note is drawn in the legend at 42% opacity (here: `treatment_start`).

| Event type (`type`) | Fill | Text | Contrast |
|---|---|---|---|
| `referral_received` | `#C5E0DC` | `#1A4A48` | 7.12:1 |
| `ct_done` | `#C4D6F0` | `#1C3A66` | 7.70:1 |
| `biopsy_done` | `#DDD0F0` | `#4A2C78` | 7.47:1 |
| `pathology_result` | `#F0DB9A` | `#5A4208` | 6.90:1 |
| `mdt_decision` | `#C9D2E2` | `#16233F` | 10.25:1 |
| `treatment_decision` | `#EEC8B0` | `#5A2E12` | 7.37:1 |
| `treatment_start` | `#E8C5D8` | `#6A2450` | 6.77:1 |

CSS: `mark.hl` with `box-decoration-break: clone`, 2px radius, 1px/3px padding. Tokens: `--hl-{type}-bg` / `--hl-{type}-fg`.

**Pipeline** (four stages, teal connecting chevrons, 40px icon tiles):
1. Synthetic notes — "10 showcase notes · not real patients"
2. Extract on Verda — "**Qwen3-32B** · EU-hosted inference / regex_baseline as the floor". Navy icon tile (current stage). Use `source_now` from samples.json; if it ever reverts, swap the label rather than hard-coding.
3. Structured events — "7 types, dates + evidence spans"
4. Day-28 clock — "Alert when day_count ≥ 28"

**Animation** (CSS already in `howwebuilt.css`; mockup PNGs are the settled frames with `body.capture`):
- Fan-out: each sheet `700ms` `var(--tz-ease)` (`cubic-bezier(.2,.7,.2,1)`), stagger **45ms** per sheet (back → front), from a stacked origin (`--from-x/y/rot`) to its arc slot (`--x`, `--y`, `--rot`).
- Open: the chosen sheet then eases to its large position, `800ms` same easing, delay **420ms**.
- Highlights fade in `400ms` at **900ms**. Rail slides in `500ms` at **700ms**.
- `prefers-reduced-motion: reduce`: no animation; sheets render in their final `translate + rotate` pose and highlights/rail are visible immediately.

Rebuild HTML with `python3 brand/mockups/howwebuilt.py`, PNGs with `--render`.
