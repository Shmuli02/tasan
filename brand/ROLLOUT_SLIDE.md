# County rollout slide

16:9 slide (1920×1080) showing how a county adopts Tasan in 90 days. Lapland is the example only. The pilot is **proposed**: draft, not signed, not discussed with the county. No existing AstraZeneca–county pilot is claimed.

## Files

| File | Role |
|---|---|
| `brand/rollout-slide.png` | Final slide, 1920×1080 PNG |
| `brand/rollout-slide.html` | Source (Nunito, palette, logo inlined from `brand/logo.svg`) |
| `brand/fonts/Nunito-VariableFont_wght.ttf` | Font used by the HTML source |
| `brand/ROLLOUT_SLIDE.md` | This note: exact copy, full wording, sources |

`brand/logo-horizontal.svg` was not present, so the slide uses the current `brand/logo.svg` mark and wordmark, small in the top-left corner (inlined so Nunito renders in the wordmark). Do not treat this HTML as a place to polish the master logo.

To re-render the PNG from the HTML (box, Europe/Helsinki):

```bash
google-chrome --headless=new --disable-gpu --hide-scrollbars \
  --force-device-scale-factor=1 --window-size=1920,1080 \
  --virtual-time-budget=8000 --default-background-color=FFF4F1EA \
  --screenshot=/workspace/junction-new/brand/rollout-slide.png \
  file:///workspace/junction-new/brand/rollout-slide.html
```

## On-slide copy (exact)

Main copy is 41 words, excluding the source line. Palette: navy `#16233F`, teal `#3A9A9A`, off-white `#F4F1EA`. Font: Nunito.

**Badge:** Proposed · Lapland

**Title:** How a county adopts Tasan in 90 days

**Timeline (left to right):**

| Kicker | Heading | Body |
|---|---|---|
| Week 0 | Sign | Chief medical officer signs |
| Weeks 1–2 | Set up | Clock and nurse navigator |
| From day 31 | Day-28 alerts live | To the navigator |
| Day 90 | Stop/go | ≥85% complete, ≥90% actioned |

**Source line (tiny, at the foot):**  
Source: recs/pilot_brief_lapland.md · Draft, not discussed with the county · Day-28 and KPI targets are Tasan design choices · No existing AstraZeneca–county pilot is claimed

## Full wording behind each step

Every step is taken from `recs/pilot_brief_lapland.md` and `recs/pilot_brief_lapland.json` (status: `DRAFT – not signed. Not discussed with the county.`). Slide text is shortened to fit the word limit. Nothing below is an agreed or existing pilot.

### Week 0 — Sign

**On slide:** Chief medical officer signs.

**From the brief:** The signer / sponsor is the johtajaylilääkäri (chief medical officer). In the Lapland draft the named role-holder is Jyri J. Taskila, verified on the county website (https://lapha.fi/yhteystiedot/johto, 2026-11-14). The name is not on the slide, because the brief is a draft and has not been discussed with the county. The county would own the signature; this is a proposed ask, not an agreement.

### Weeks 1–2 — Set up

**On slide:** Clock and nurse navigator.

**From the brief (Days 1–30):** extract 12 months of time points, completeness check, publish baseline, name navigator.

The campaign brief asked for a “Weeks 1–2” set-up marker. The pilot brief’s set-up window is **Days 1–30**, not two weeks. The slide uses the requested kicker for the *start* of that work and does not say set-up finishes in two weeks.

**Clock:** the 4 THL time points (referral, specialist visit, diagnosis, first treatment) per patient, weekly feed from county data. Owner: county analytics unit (person to be named by the county).

**Named nurse navigator (1.0 FTE):** contacts every new suspected case and unblocks waits. Navigator line manager in the Lapland draft: Henna Kauranen, vs. hoitotyön johtaja (name held off the slide for the same draft reason).

**Also in days 1–30, not on the slide:** registry-completeness check first; publish the county’s own baseline.

### From day 31 — Day-28 alerts live

**On slide:** Day-28 alerts live. To the navigator.

**From the brief (Days 31–60):** weekly feed, day-28 alert live, navigator acts.

The “day-28” here is the **patient-pathway** day: if there is no treatment decision 28 days after referral arrival, the open pathway goes to the navigator and the responsible physician. Alerts go live from **pilot day 31**, not calendar day 28 of the 90-day pilot. The kicker “From day 31” is there so the slide does not contradict the brief.

**KPIs that start at go-live (day 31), both Tasan design choices:**
- Day-28 alerts actioned: ≥90% within 2 working days
- Navigator contact: ≥90% of new suspected cases within 3 working days

### Day 90 — Stop/go

**On slide:** ≥85% complete, ≥90% actioned.

**Abbreviated.** Full go rule from the brief (decider: johtajaylilääkäri, on the day-90 board report):

Go (extend) if:
- ≥85% of pathways have all 4 time points,
- the own baseline is presented to the board,
- ≥90% of day-28 alerts are actioned within 2 working days, and
- ≥90% of new cases are contacted within 3 working days.

**Pause / fix (not on the slide):** completeness <70% after one fix cycle: pause the clock and fix recording first. Otherwise extend 90 days with one named fix.

**Days 61–90 in the brief:** first board report including non-pathway waits; day-90 stop/go.

All of these KPI targets are Tasan design choices. The 42-day / 80% treatment-within-target KPI in the brief (THL Ohjaus 21/2016, 6 weeks referral → first treatment, document watermarked outdated; no lung-specific limit; cancer-specific times due 2026–2028) is **not** on the slide.

## What is deliberately not on the slide

- Staff cost only, estimate: €20,339–€23,988 for 90 days (`cost_range` in the JSON). Basis and KT sources stay in the brief.
- Named individuals (draft, not discussed).
- The people-number or curative-share figures (those belong on the cover / pitch, with `data/facts.json` ids `people_number_national` / `people_number_lapland` and the chart-estimate caveats).
- Any “lives saved” or deaths-prevented claim (forbidden; see `facts.json` usage_rules and `nodata_lives_saved`).
- Any claim that AstraZeneca already has, runs or funds a pilot with a Finnish wellbeing services county. The brief states: “No existing AstraZeneca–wellbeing-county pilot in Finland is claimed.” AstraZeneca’s possible role in the brief (co-fund an independent evaluation; no patient steering) is not on this slide.
- The Estonia 2023 pathway PPP (a national service-design project, not a county pilot).

## Sources

- `recs/pilot_brief_lapland.md`
- `recs/pilot_brief_lapland.json` (same content, structured)

No number on this slide is taken from `data/facts.json`. The only figures shown (≥85%, ≥90%) are Tasan design-choice KPI targets from the pilot brief, labelled as such in the source line.
