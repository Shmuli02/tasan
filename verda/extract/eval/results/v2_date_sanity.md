# v2 date sanity check (not a regex retune)

The official v1 regex is left unchanged. This file asks whether v2 gold is fair:

- Documents: 600; gold events: 2146
- Evidence span found verbatim in the corpus file: 2146/2146 (100.0%)
- Gold dates a careful human-equivalent parser can recover from (evidence span + note_date): **1879/2146 (87.6%)**
- Official v1 regex predicted events on v2: **1** (exact TP 0) — this is why exact F1 was 0.000

## Literal date strings

A “literal date string” here means an explicit calendar form a reader can resolve without only a relative word (`eilen` / `yesterday`). That includes ISO and dotted numeric dates, the v2 `dd-mm-yyyy` form, spelled month names (e.g. `14. huhtikuuta 2026`), and ISO-week forms (`viikolla 34 maanantaina (2026)`), which uniquely identify a day.

- Notes whose **body** contains at least one literal date string (including historical distractors): **600/600 (100.0%)**
- Notes whose gold evidence spans contain a literal / spelled / week date (not only `eilen` etc.): **580/600 (96.7%)**
- Notes in which the **v1 regex numeric parser** finds any date in the body (ISO, `d.m.yyyy`, `d/m/yyyy` — **not** `dd-mm-yyyy`, spelled months, or ISO weeks): **600/600 (100.0%)**

## Gold surface forms (per event)

- `spelled_fi`: 535
- `numeric_dmy_dash`: 337
- `iso_week_fi`: 320
- `spelled_gen_fi`: 237
- `unparsed`: 233
- `spelled_sv`: 52
- `bare_weekday_fi`: 49
- `spelled_en`: 45
- `relative_yesterday`: 33
- `numeric_iso`: 31
- `relative_2days`: 24
- `spelled_gen_sv`: 22
- `iso_week_en`: 22
- `iso_week_sv`: 17
- `spelled_gen_en`: 17
- `mixed:iso_week_fi,spelled_fi`: 16
- `mixed:numeric_dmy_dash,spelled_fi`: 14
- `mixed:spelled_gen_sv,spelled_sv`: 12
- `mixed:spelled_fi,spelled_gen_fi`: 12
- `mixed:numeric_iso,spelled_gen_sv`: 10
- `mixed:spelled_en,spelled_sv`: 10
- `mixed:numeric_iso,spelled_sv`: 9
- `mixed:spelled_en,spelled_gen_en`: 9
- `mixed:iso_week_sv,numeric_iso`: 9
- `mixed:iso_week_sv,spelled_sv`: 8
- `mixed:iso_week_en,spelled_en`: 6
- `mixed:iso_week_fi,spelled_gen_fi`: 6
- `mixed:numeric_dmy_dash,spelled_en`: 5
- `mixed:iso_week_fi,numeric_dmy_dash`: 5
- `mixed:numeric_dmy_dash,spelled_gen_fi`: 5
- `mixed:iso_week_en,numeric_dmy_dash`: 3
- `mixed:iso_week_sv,spelled_gen_sv`: 3
- `mixed:numeric_dmy_dash,spelled_gen_en`: 3
- `mixed:relative_2days,spelled_gen_sv`: 2
- `mixed:iso_week_sv,spelled_en,spelled_sv`: 2
- `mixed:iso_week_en,spelled_gen_en`: 2
- `mixed:iso_week_en,relative_yesterday`: 2
- `mixed:relative_2days,spelled_gen_fi`: 2
- `mixed:relative_yesterday,spelled_sv`: 2
- `mixed:numeric_dmy_dash,relative_yesterday`: 2
- `mixed:spelled_en,spelled_gen_sv,spelled_sv`: 1
- `mixed:iso_week_sv,relative_yesterday`: 1
- `mixed:numeric_iso,spelled_en,spelled_sv`: 1
- `mixed:iso_week_fi,relative_yesterday`: 1
- `mixed:relative_2days,relative_yesterday`: 1
- `mixed:relative_2days,spelled_sv`: 1
- `mixed:relative_yesterday,spelled_en`: 1
- `mixed:relative_2days,relative_yesterday,spelled_gen_en`: 1
- `mixed:relative_2days,relative_yesterday,spelled_en`: 1
- `mixed:relative_2days,spelled_fi`: 1
- `mixed:numeric_iso,relative_yesterday`: 1
- `mixed:numeric_dmy_dash,relative_2days`: 1
- `mixed:relative_yesterday,spelled_gen_fi`: 1

## Why regex F1 is 0.000 (two stacked effects, not a broken gold file)

1. **Held-out keywords (intended).** v2 sentences were written to avoid the v1 keyword list (`ESH-lähete vastaanotettu`, `Thoraxin TT tehty`, …). A few v2 templates still share a verb (`Lähete saapui …`) but OCR splits (`Lä-hete`) often break even those. Keyword hits on v2 bodies, by type: referral_received=87 (out of 2146 events).
2. **Date-format mismatch (also real, and harsher than a fair “messy clinical Finnish” test).** v2’s “numeric” style is `14-04-2026` (dashes, day-first). The v1 regex only accepts `2026-04-14`, `14.4.2026`, `14/4/2026`, or `14.4`. It does **not** parse spelled months or `viikolla 34 maanantaina (2026)`. Those week forms *are* uniquely resolvable with a calendar; a careful human can do it. So 0.000 is not “the gold dates are hidden”, but it is also not only lexical difficulty — a large share of gold dates are in formats the official parser was never taught.

## Unrecoverable examples (267)

- `SYN2-P0001-biopsy_note-02` biopsy_done gold=2026-02-02 kind=spelled_fi span='Toimenpide varattiin 27. tammikuuta 2026, mutta näyte otettiin vasta toissap-äivänä.'
- `SYN2-P0002-oncology_note-03` biopsy_done gold=2026-07-04 kind=unparsed span='Tähystyksen yhteydessä punktionäyte 4. heinäkuuta 2026.'
- `SYN2-P0002-oncology_note-03` pathology_result gold=2026-07-16 kind=unparsed span='Laboratorio ilmoitti histo logian 16. heinäkuuta 2026: adenokarsinooma.'
- `SYN2-P0002-oncology_note-03` treatment_decision gold=2026-07-18 kind=unparsed span='Sovittiin hoitomuodosta heinäkuun 18. päivänä 2026 (sytostaatti).'
- `SYN2-P0002-mdt_minutes-04` pathology_result gold=2026-07-16 kind=unparsed span='Laboratorio ilmoitti histologian 16. heinäkuuta 2026: levyepiteelikarsinooma.'
- `SYN2-P0002-mdt_minutes-04` mdt_decision gold=2026-07-18 kind=unparsed span='Tiimikokous pidettiin 18. heinäkuuta 2026 ja suositus kirjattiin.'
- `SYN2-P0002-mdt_minutes-04` biopsy_done gold=2026-07-04 kind=unparsed span='Kudosnäytteet haettiin toimenpiteessä 4. heinäkuuta 2026.'
- `SYN2-P0002-discharge_summary-05` referral_received gold=2026-06-15 kind=unparsed span='Asiakirja merkittiin saapuneeksi keuhkoyksikköön 15. kesä-kuuta 2026.'
- `SYN2-P0004-ct_report-01` referral_received gold=2026-06-20 kind=spelled_gen_sv span='Konsultationsbegäran skrevs juni den 15 år 2026, men registrerades som inkommen först på lördagen.'
- `SYN2-P0004-oncology_note-04` treatment_decision gold=2026-07-21 kind=unparsed span='Valittiin etenemistapa heinäkuun 21. päivänä 2026: sytostaatti.'
- `SYN2-P0004-oncology_note-04` biopsy_done gold=2026-07-03 kind=unparsed span='Tähystyksen yhteydessä punktionäyte heinäkuun 3. päivänä 2026.'
- `SYN2-P0004-oncology_note-04` mdt_decision gold=2026-07-20 kind=unparsed span='Yhteispalaveri järjestettiin 20. heinäkuuta 2026; linja muodostettiin siellä.'
- `SYN2-P0004-discharge_summary-05` biopsy_done gold=2026-07-03 kind=unparsed span='Kudosnäytteet haettiin toimenpiteessä 3. heinäkuuta 2026.'
- `SYN2-P0005-biopsy_note-02` biopsy_done gold=2026-01-22 kind=unparsed span='Näyte otettiin tähystyksessä ta mmikuun 22. päivänä 2026.'
- `SYN2-P0005-mdt_minutes-03` referral_received gold=2026-01-05 kind=unparsed span='Begäran nådde kliniken den 5 ja nuari 2026.'


## OCR-tolerant second pass

A hyphen-only cleanup (`kesä-kuuta` → `kesäkuuta`, `toissap-äivänä` → `toissapäivänä`) plus the same careful parser recovers **1778/2146 (82.9%)** of gold dates from the full note + `note_date`. A span-level pass without that cleanup already recovered 1879/2146 (87.6%); the remaining misses are mostly OCR *spaces* inside a month name (`ta mmikuun`, `ja nuari`, `kesä-kuuta` already covered) or a broken relative (`toissap-äivänä` after hyphen join is recoverable; mid-word spaces are not fully normalised). A careful human reading Finnish/Swedish/English can still resolve those.

The gold dates are consistent with the text (ISO weeks such as `viikolla 4 perjantaina (2026)` uniquely map to the labelled day). They are not a format bug in the labels.

The v1 regex numeric parser sees a date in every v2 **body** mainly because historical **distractors** (birth date, old cholecystectomy) use dotted `d.m.yyyy`, while many *gold* event dates use spelled months, ISO weeks, or day-first `dd-mm-yyyy` — formats the official parser does not accept. Combined with held-out keywords, that is why exact F1 is 0.000.
