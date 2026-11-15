"""Build build/targets.json from the team's sourced CSVs in junction-new/data/csv.

Every number written here carries the CSV file, row selector, source table and URL it came from.
Nothing is typed in by hand.
"""
from __future__ import annotations
import csv
from collections import defaultdict
from .common import DATA_DIR, BUILD_DIR, AREAS, dump_json, sha256_file

CUM = "csv/lung_report2024_first_event_cumulative_by_yta.csv"
DERIVED = "csv/lung_derived_first_active_treatment_by_month_yta.csv"
QUANT = "csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv"
TOTALS = "csv/lung_report2024_treatment_6m_by_yta.csv"
COUNTY = "csv/lung_report2026_treatment_by_wsc.csv"

EVENT_FI = {"Leikkaushoito": "surgery", "Muu kuin palliatiivinen sädehoito": "radiotherapy",
            "Lääkehoito": "drug", "Palliatiivinen hoito": "palliative", "Kuollut": "death",
            "Keuhkosyöpä": "none"}
QUANT_FI = {"Leikkaushoito": "surgery", "Sädehoito": "radiotherapy", "Lääkehoito": "drug"}
AREA_FI = {"Etelä-Suomen yhteistyöalue": "YTA-ETELA", "Itä-Suomen yhteistyöalue": "YTA-ITA",
           "Länsi-Suomen yhteistyöalue": "YTA-LANSI", "Pohjois-Suomen yhteistyöalue": "YTA-POHJOIS",
           "Sisä-Suomen yhteistyöalue": "YTA-SISA"}

def _rows(rel):
    with open(DATA_DIR / rel, encoding="utf-8") as f:
        return list(csv.DictReader(f))

def build():
    cum, der, qua, tot, cty = (_rows(x) for x in (CUM, DERIVED, QUANT, TOTALS, COUNTY))
    areas = {}
    for a in AREAS:
        r0 = next(r for r in cum if r["region_code"] == a)
        curves = defaultdict(dict)
        for r in cum:
            if r["region_code"] == a:
                curves[EVENT_FI[r["event_fi"]]][int(r["month"])] = float(r["value"])
        n_area = int(next(r for r in tot if r["region_code"] == a)["denominator"])
        quant = {}
        for r in qua:
            if r["region_code"] == a:
                quant[QUANT_FI[r["treatment_fi"]]] = {"q1": float(r["q1"]), "median": float(r["value"]), "q3": float(r["q3"])}
        derived = {int(r["month"]): {"value": float(r["value"]), "ci95_low": float(r["ci95_low"]), "ci95_high": float(r["ci95_high"])}
                   for r in der if r["region_code"] == a}
        areas[a] = {
            "name_en": r0["region"], "name_fi": r0["region_name_fi"], "cohort": r0["year"],
            "n_patients": n_area,
            "n_patients_source": {"file": f"data/{TOTALS}", "table": "Keuhkosyöpä Suomessa 2024, Taulukko 3.3 (PDF p.18)", "column": "denominator"},
            "cum_first_event_pct": {k: [v[m] for m in range(7)] for k, v in curves.items()},
            "cum_source": {"file": f"data/{CUM}", "table": r0["source_table"], "url": r0["source_url"]},
            "quantiles_days": quant,
            "quantiles_source": {"file": f"data/{QUANT}", "table": "Keuhkosyöpä Suomessa 2024, Taulukko 4.1 (PDF p.28)",
                                  "url": r0["source_url"], "population": "patients whose first treatment within 6 months was this modality; days from Cancer Registry diagnosis date"},
            "derived_first_active_pct": derived,
            "derived_source": {"file": f"data/{DERIVED}", "table": "derived by team from Taulukko 4.5 + 3.3 (Wilson 95% CI)"},
        }
        s6 = sum(v[6] for v in curves.values())
        areas[a]["month6_sum_pct"] = round(s6, 2)
    counties = []
    for r in cty:
        if r["treatment_group_fi"] != "Parantava":
            continue
        N = int(r["denominator"])
        counties.append({
            "code": r["region_code"].zfill(2), "name_en": r["region"], "name_fi": r["region_name_fi"],
            "area": AREA_FI[r["collaborative_area_fi"]], "n_patients_5y": N, "years": r["year"],
            "annual_volume": round(N / 5, 2),
            "source": {"file": f"data/{COUNTY}", "table": r["source_table"], "url": r["source_url"],
                       "note": "denominator = lung cancer patients diagnosed 2019-2023 (5 diagnosis years); annual volume = N/5 (derived)"},
        })
    counties.sort(key=lambda c: c["code"])
    files = [CUM, DERIVED, QUANT, TOTALS, COUNTY]
    out = {"areas": areas, "counties": counties,
           "input_files_sha256": {f"data/{f}": sha256_file(DATA_DIR / f) for f in files}}
    dump_json(out, BUILD_DIR / "targets.json")
    return out

if __name__ == "__main__":
    t = build()
    print(f"targets.json: {len(t['areas'])} areas, {len(t['counties'])} counties")
    for a, v in t["areas"].items():
        print(a, v["n_patients"], "month-6 sum", v["month6_sum_pct"])
