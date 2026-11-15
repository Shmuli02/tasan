# Equal Care — data contract

The demo app **never hard-codes indicator values or recommendations**. It loads four JSON files (plus a bundled county map). Teammates drop real files into the folders below and run one command:

```bash
cd /workspace/junction-new/app && npm run sync && npm run build
# or, to also publish: npm run deploy
```

`scripts/sync-data.mjs` copies and validates:

| Team folder (source of truth) | App destination after sync |
| --- | --- |
| `/workspace/junction-new/data/regions.json` | `src/content/regions.json` |
| `/workspace/junction-new/data/sources.json` | `src/content/sources.json` |
| `/workspace/junction-new/data/key_message.json` | `src/content/key_message.json` |
| `/workspace/junction-new/recs/recommendations.json` | `src/content/recommendations.json` |
| (optional) `/workspace/junction-new/data/counties.geojson` | `src/content/counties.geojson` |

If a required file is **missing or invalid**, the script falls back to `example-data/` and the UI keeps the banner **“Example data – awaiting team dataset”**. It will not crash. A load report is written to `src/content/_load_report.json`.

Human notes such as `data/SOURCES.md` are welcome for the team; the app itself reads **`sources.json`**. Keep them in sync.

All files use `schema_version: "1.0"` and UTF-8 JSON (2-space indent is fine).

Set `meta.is_example` to `true` until the data are real. Set it to `false` when you are ready to drop the example banner. Every individual value can still be flagged with `"is_example": true`.

**Do not invent official-looking numbers and present them as facts.** If a value is a placeholder, keep `is_example: true` and cite `src-example-synthetic` (or your own clearly named placeholder source).

---

## Official region ids (use these)

21 wellbeing services counties + Helsinki + Åland (Åland is shown on the map; set `include_in_national: false` unless you have a reason to include it in the national figure).

| `id` | Finnish short name | English short name | `type` | Sotkanet id |
| --- | --- | --- | --- | --- |
| `01` | Itä-Uusimaa | East Uusimaa | `wellbeing_services_county` | 961 |
| `02` | Keski-Uusimaa | Central Uusimaa | `wellbeing_services_county` | 966 |
| `03` | Länsi-Uusimaa | West Uusimaa | `wellbeing_services_county` | 969 |
| `04` | Vantaa-Kerava | Vantaa-Kerava | `wellbeing_services_county` | 977 |
| `05` | Varsinais-Suomi | Southwest Finland | `wellbeing_services_county` | 978 |
| `06` | Satakunta | Satakunta | `wellbeing_services_county` | 976 |
| `07` | Kanta-Häme | Kanta-Häme | `wellbeing_services_county` | 963 |
| `08` | Pirkanmaa | Pirkanmaa | `wellbeing_services_county` | 970 |
| `09` | Päijät-Häme | Päijät-Häme | `wellbeing_services_county` | 975 |
| `10` | Kymenlaakso | Kymenlaakso | `wellbeing_services_county` | 967 |
| `11` | Etelä-Karjala | South Karelia | `wellbeing_services_county` | 957 |
| `12` | Etelä-Savo | South Savo | `wellbeing_services_county` | 959 |
| `13` | Pohjois-Savo | North Savo | `wellbeing_services_county` | 974 |
| `14` | Pohjois-Karjala | North Karelia | `wellbeing_services_county` | 972 |
| `15` | Keski-Suomi | Central Finland | `wellbeing_services_county` | 965 |
| `16` | Etelä-Pohjanmaa | South Ostrobothnia | `wellbeing_services_county` | 958 |
| `17` | Pohjanmaa | Ostrobothnia | `wellbeing_services_county` | 971 |
| `18` | Keski-Pohjanmaa | Central Ostrobothnia | `wellbeing_services_county` | 964 |
| `19` | Pohjois-Pohjanmaa | North Ostrobothnia | `wellbeing_services_county` | 973 |
| `20` | Kainuu | Kainuu | `wellbeing_services_county` | 962 |
| `21` | Lappi | Lapland | `wellbeing_services_county` | 968 |
| `90` | Helsinki | Helsinki | `city` | 960 |
| `91` | Ahvenanmaa | Åland | `autonomous_region` | 956 |
| `FI` (national block only) | Koko maa | Finland (national) | — | 658 |

Map geometry is already bundled (Statistics Finland, 2026, CC BY 4.0). You do not need to supply GeoJSON unless you want to replace it. Feature property `id` must match the region `id` above.

---

## Pathway stages (fixed ids)

Use exactly these `stage` values: `detection` | `referral` | `diagnosis` | `treatment`.

---

## 1. `data/regions.json`

```json
{
  "meta": {
    "schema_version": "1.0",
    "is_example": false,
    "title": "optional short title",
    "disclaimer": "Limitations, missing years, and anything a judge should not over-read.",
    "updated": "2026-11-14",
    "national_aggregation": "Describe how the national figure was obtained (official series vs computed)."
  },
  "stages": [
    { "id": "detection", "label": "Detection", "label_fi": "Toteaminen", "order": 1, "short": "Detect" },
    { "id": "referral", "label": "Primary → specialist referral", "label_fi": "Lähete…", "order": 2, "short": "Refer" },
    { "id": "diagnosis", "label": "Diagnosis", "label_fi": "Diagnoosi", "order": 3, "short": "Diagnose" },
    { "id": "treatment", "label": "Treatment initiation", "label_fi": "Hoidon aloitus", "order": 4, "short": "Treat" }
  ],
  "indicator_catalog": [
    {
      "id": "treatment_within_target_share",
      "stage": "treatment",
      "label": "Share of patients starting treatment within target timeframes",
      "label_fi": "optional",
      "unit": "%",
      "higher_is_better": true,
      "decimals": 0,
      "target": 80,
      "target_source_id": "src-…",
      "target_note": "Say whether the target is official or a team assumption.",
      "goal": "3",
      "goal3_indicator": "g3-treatment-within-target"
    }
  ],
  "national": {
    "id": "FI",
    "name": "Finland (national)",
    "name_fi": "Koko maa",
    "sotkanet_id": 658,
    "indicators": [
      { "id": "treatment_within_target_share", "value": 63.0, "year": 2024, "source_id": "src-…", "is_example": false }
    ]
  },
  "regions": [
    {
      "id": "21",
      "slug": "lappi",
      "name": "Lapland",
      "name_fi": "Lappi",
      "name_official_en": "Lapland wellbeing services county",
      "name_official_fi": "Lapin hyvinvointialue",
      "type": "wellbeing_services_county",
      "sotkanet_id": 968,
      "include_in_national": true,
      "indicators": [
        { "id": "treatment_within_target_share", "value": 53.0, "year": 2024, "source_id": "src-…", "is_example": false, "note": "optional" }
      ]
    }
  ]
}
```

**Indicator values** (on `national` and each region) inherit label, unit, target, stage and Goal 3 mapping from `indicator_catalog` by `id`. You only need to repeat those fields on a value if you must override them.

- `value` is a number (or `null` if missing — the UI shows “n/a”).
- `year` is a number or `null`.
- `source_id` must exist in `sources.json`.
- Prefer one **primary indicator per stage**. Extra indicators are allowed and will be listed; the map colours the catalog indicator whose `stage` matches the selected stage (first match if several).

The challenge requires at least one indicator connected to **Goal 3** of the National Cancer Strategy 2026–2035 (*Varmistetaan yhdenvertainen ja vaikuttava syövänhoito*). The official Goal 3 follow-up metrics include:

- patients start treatment within target timeframes (THL Ohjaus 21/2016);
- 5-year survival of poor-prognosis cancers reaching the Nordic level;
- 10% reduction in cancer mortality.

Use `goal: "3"` and a `goal3_indicator` id (see recommendations file) so the UI can show a **Goal 3** badge.

---

## 2. `data/sources.json`

```json
{
  "meta": { "schema_version": "1.0", "is_example": false, "updated": "2026-11-14" },
  "sources": [
    {
      "id": "src-cancer-registry-2024",
      "title": "Human-readable title",
      "publisher": "Finnish Cancer Registry / THL / …",
      "url": "https://…",
      "accessed": "2026-11-14",
      "year": 2024,
      "note": "Optional: what was used, and limitations."
    }
  ]
}
```

`id` is unique. `url` may be `null`. `accessed` is ISO date. Every number and claim in the other files should point at one of these ids.

---

## 3. `data/key_message.json`

The one-screen message a decision-maker should grasp in under two minutes. Fill this once the gap finding is agreed.

```json
{
  "meta": { "schema_version": "1.0", "is_example": false, "updated": "2026-11-14" },
  "headline": "One sentence: where the gap is.",
  "gap": "A few sentences on the size and meaning of the gap.",
  "where_in_pathway": "Detection, referral, diagnosis, and/or treatment initiation — be specific.",
  "what_to_do": "The first concrete action you want a county or the national level to take.",
  "primary_rec_id": "rec-…",
  "spotlight_stage": "treatment",
  "spotlight_indicator_id": "treatment_within_target_share",
  "source_ids": ["src-…"]
}
```

If `headline` / `gap` / `where_in_pathway` / `what_to_do` are omitted, the app auto-summarises from the loaded data and labels the text as auto-generated.

---

## 4. `recs/recommendations.json`

```json
{
  "meta": { "schema_version": "1.0", "is_example": false, "updated": "2026-11-14", "disclaimer": "optional" },
  "goal3_indicators": [
    {
      "id": "g3-treatment-within-target",
      "label": "Patients start treatment within target timeframes",
      "label_fi": "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa",
      "strategy_ref": "National Cancer Strategy 2026–2035, Goal 3",
      "source_id": "src-strategy-2026"
    }
  ],
  "recommendations": [
    {
      "id": "rec-treatment-clock",
      "title": "Short action title",
      "stage": "treatment",
      "what": "Concrete action a health centre or county can implement.",
      "who_implements": "Role and organisation.",
      "owner": "Named owner role (e.g. johtajaylilääkäri).",
      "cost": {
        "label": "€110,000 per county per year",
        "amount": 110000,
        "currency": "EUR",
        "basis": "What the amount covers, and over what period.",
        "source_id": "src-…",
        "is_example": false
      },
      "kpi": {
        "name": "Share of patients starting treatment within target timeframes",
        "indicator_id": "treatment_within_target_share",
        "unit": "%",
        "target": "Text target, e.g. shrink the regional spread and lift every county toward X%."
      },
      "goal3_indicator": "g3-treatment-within-target",
      "evidence": "Why this should work, with limitations.",
      "evidence_source_ids": ["src-…"],
      "expected_effect": {
        "indicator_id": "treatment_within_target_share",
        "direction": "increase",
        "delta": 8,
        "unit": "percentage points",
        "horizon": "18 months",
        "source_id": "src-…",
        "assumptions": "Spell out the assumptions. Judges will read this.",
        "is_example": false
      },
      "effect_params": {
        "type": "linear",
        "applies_to_indicator": "treatment_within_target_share",
        "effect_at_full_coverage": 8,
        "max_coverage": 1.0,
        "applicable_regions": ["*"],
        "clamp_min": 0,
        "clamp_max": 100
      }
    }
  ]
}
```

Fields the care strategist was asked to supply are all first-class: **`owner`**, **`cost`**, **`kpi`**, **`evidence`** / `evidence_source_ids`, and **`goal3_indicator`**.

Simulator model (keep `type` as `linear` unless you agree a change with the builder):

> projected = clamp(current + coverage × effect_at_full_coverage, clamp_min, clamp_max)

Coverage is a 0–100% slider per recommendation. Effects that share an indicator are **added**, then clamped. That can overestimate combined impact — say so in `assumptions`. `applicable_regions` is `["*"]` or a list of region ids. Optional per-region modifiers later: `region_modifiers: { "21": 1.2 }` (multiplies the effect).

---

## Worked examples

See `app/example-data/` for a complete, clearly labelled EXAMPLE set that already follows this contract. Copy a file from there into `data/` or `recs/` and replace values.

---

## Swap-in checklist (data analyst + care strategist)

1. Write `data/sources.json` first (every later `source_id` must exist).
2. Write `data/regions.json` (catalog + national + 22 or 23 regions, at least one Goal 3 indicator).
3. Write `recs/recommendations.json` (concrete actions, owner, cost, KPI, evidence, Goal 3 mapping, effect params).
4. Write `data/key_message.json` once the gap and first action are agreed.
5. From `app/`: `npm run sync && npm run test && npm run deploy`.
6. Set `is_example: false` only when you are willing to stand behind the numbers in front of judges.

## Local stage fallback

`npm run stage` in `app/` builds and serves `dist/` at http://127.0.0.1:8080 with no network required.
