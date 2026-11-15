# Tasan Extract synthetic corpus

**SYNTHETIC — NOT REAL PATIENTS.** Every document, name, date and finding in this folder is invented for the Junction 2026 Tasan Extract evaluation. There is no real personal data and nothing here may be treated as a clinical record.

## How it is made

```bash
python3 generate.py --seed 20261114 --out data
```

The generator is seeded and reproducible. It uses templates plus combinatorial variation only (no LLM). A later GPU paraphrase pass is optional and is not required for v1.

## Contents (`data/`, seed `20261114`)

| | |
|---|---|
| Documents | 600 `.txt` files under `data/documents/` |
| Patients | 120 (`SYN-P0001` …), mixed-language pathways |
| Languages | about 75% Finnish, 15% Swedish, 10% English |
| Document types | referral letters, CT/radiology reports, bronchoscopy/biopsy notes, pathology reports, MDT minutes, oncology notes, discharge summaries |
| Event types | `referral_received`, `ct_done`, `biopsy_done`, `pathology_result`, `mdt_decision`, `treatment_decision`, `treatment_start` |
| Gold | per-document ISO date + verbatim `evidence_span`; patient-level merge is **latest document wins** |
| Day-28 alert | `day_count >= 28` and no `treatment_start`, measured at `clock_as_of` = latest note date |

Every file starts with a `SYNTHETIC DOCUMENT — NOT A REAL PATIENT` banner.

Messiness baked in: abbreviations (TT, PET-TT, bronkoskopia, EBUS, MDT / moniammatillinen kokous, lähete, sytostaatti, sädehoito), date formats (`14.11.2026`, `14.11`, `14/11`, `viime tiistaina`, `kaksi viikkoa sitten`), typos, negations and plans (`TT suunniteltu`, `biopsia peruttiin`), copy-pasted history, and distractor dates (birth dates, unrelated old operations).

Hard cases include: no referral, late wait (alert), treatment on day 28 / day 29, relative-date-only notes, typo-heavy notes, cancelled-then-done biopsy, conflicting CT dates across documents, mixed FI/SV/EN, and long discharges with distractors.

Do not add real EHR text to this tree.

## v2 held-out corpus (`data_v2/`, seed `20261142`)

```bash
python3 generate_v2.py --seed 20261142 --out data_v2
```

600 documents, 120 patients (`SYN2-P*`), 40-patient **dev** / 80-patient **test** split. Languages ≈ 74.8% FI / 15.2% SV / 10% EN. Same event types and gold-by-construction labels as v1, but **phrasings the v1 regex was never tuned on** (consultation request written vs logged as arrived, imaging booked vs performed, ISO week dates, relative weekdays, dictation artifacts). Tune regex on dev only if at all; do not add test keywords.

The official untuned v2 regex report is `../eval/results/regex_report_v2.md` (exact micro F1 0.000 on dev and on test). A later GPU paraphrase pass will rewrite a subset with a gold-date recoverability filter.

Do not add real EHR text to this tree.
