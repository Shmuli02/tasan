#!/usr/bin/env python3
"""Extract a small UI dataset from team CSVs / key_findings / optional hero.json.
Never ships combined.json (5.9 MB) to the browser.
"""
from __future__ import annotations

import csv
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]  # junction-new
DATA = ROOT / "data"
RECS = ROOT / "recs"
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "app" / "src" / "content"

REGION_META = {
    "01": {"slug": "ita-uusimaa", "name": "East Uusimaa", "name_fi": "Itä-Uusimaa",
           "name_official_en": "East Uusimaa wellbeing services county",
           "name_official_fi": "Itä-Uudenmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 961, "include_in_national": True},
    "02": {"slug": "keski-uusimaa", "name": "Central Uusimaa", "name_fi": "Keski-Uusimaa",
           "name_official_en": "Central Uusimaa wellbeing services county",
           "name_official_fi": "Keski-Uudenmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 966, "include_in_national": True},
    "03": {"slug": "lansi-uusimaa", "name": "West Uusimaa", "name_fi": "Länsi-Uusimaa",
           "name_official_en": "West Uusimaa wellbeing services county",
           "name_official_fi": "Länsi-Uudenmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 969, "include_in_national": True},
    "04": {"slug": "vantaa-kerava", "name": "Vantaa-Kerava", "name_fi": "Vantaa-Kerava",
           "name_official_en": "Vantaa and Kerava wellbeing services county",
           "name_official_fi": "Vantaan ja Keravan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 977, "include_in_national": True},
    "05": {"slug": "varsinais-suomi", "name": "Southwest Finland", "name_fi": "Varsinais-Suomi",
           "name_official_en": "Southwest Finland wellbeing services county",
           "name_official_fi": "Varsinais-Suomen hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 978, "include_in_national": True},
    "06": {"slug": "satakunta", "name": "Satakunta", "name_fi": "Satakunta",
           "name_official_en": "Satakunta wellbeing services county",
           "name_official_fi": "Satakunnan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 976, "include_in_national": True},
    "07": {"slug": "kanta-hame", "name": "Kanta-Häme", "name_fi": "Kanta-Häme",
           "name_official_en": "Kanta-Häme wellbeing services county",
           "name_official_fi": "Kanta-Hämeen hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 963, "include_in_national": True},
    "08": {"slug": "pirkanmaa", "name": "Pirkanmaa", "name_fi": "Pirkanmaa",
           "name_official_en": "Pirkanmaa wellbeing services county",
           "name_official_fi": "Pirkanmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 970, "include_in_national": True},
    "09": {"slug": "paijat-hame", "name": "Päijät-Häme", "name_fi": "Päijät-Häme",
           "name_official_en": "Päijät-Häme wellbeing services county",
           "name_official_fi": "Päijät-Hämeen hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 975, "include_in_national": True},
    "10": {"slug": "kymenlaakso", "name": "Kymenlaakso", "name_fi": "Kymenlaakso",
           "name_official_en": "Kymenlaakso wellbeing services county",
           "name_official_fi": "Kymenlaakson hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 967, "include_in_national": True},
    "11": {"slug": "etela-karjala", "name": "South Karelia", "name_fi": "Etelä-Karjala",
           "name_official_en": "South Karelia wellbeing services county",
           "name_official_fi": "Etelä-Karjalan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 957, "include_in_national": True},
    "12": {"slug": "etela-savo", "name": "South Savo", "name_fi": "Etelä-Savo",
           "name_official_en": "South Savo wellbeing services county",
           "name_official_fi": "Etelä-Savon hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 959, "include_in_national": True},
    "13": {"slug": "pohjois-savo", "name": "North Savo", "name_fi": "Pohjois-Savo",
           "name_official_en": "North Savo wellbeing services county",
           "name_official_fi": "Pohjois-Savon hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 974, "include_in_national": True},
    "14": {"slug": "pohjois-karjala", "name": "North Karelia", "name_fi": "Pohjois-Karjala",
           "name_official_en": "North Karelia wellbeing services county",
           "name_official_fi": "Pohjois-Karjalan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 972, "include_in_national": True},
    "15": {"slug": "keski-suomi", "name": "Central Finland", "name_fi": "Keski-Suomi",
           "name_official_en": "Central Finland wellbeing services county",
           "name_official_fi": "Keski-Suomen hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 965, "include_in_national": True},
    "16": {"slug": "etela-pohjanmaa", "name": "South Ostrobothnia", "name_fi": "Etelä-Pohjanmaa",
           "name_official_en": "South Ostrobothnia wellbeing services county",
           "name_official_fi": "Etelä-Pohjanmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 958, "include_in_national": True},
    "17": {"slug": "pohjanmaa", "name": "Ostrobothnia", "name_fi": "Pohjanmaa",
           "name_official_en": "Ostrobothnia wellbeing services county",
           "name_official_fi": "Pohjanmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 971, "include_in_national": True},
    "18": {"slug": "keski-pohjanmaa", "name": "Central Ostrobothnia", "name_fi": "Keski-Pohjanmaa",
           "name_official_en": "Central Ostrobothnia wellbeing services county",
           "name_official_fi": "Keski-Pohjanmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 964, "include_in_national": True},
    "19": {"slug": "pohjois-pohjanmaa", "name": "North Ostrobothnia", "name_fi": "Pohjois-Pohjanmaa",
           "name_official_en": "North Ostrobothnia wellbeing services county",
           "name_official_fi": "Pohjois-Pohjanmaan hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 973, "include_in_national": True},
    "20": {"slug": "kainuu", "name": "Kainuu", "name_fi": "Kainuu",
           "name_official_en": "Kainuu wellbeing services county",
           "name_official_fi": "Kainuun hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 962, "include_in_national": True},
    "21": {"slug": "lappi", "name": "Lapland", "name_fi": "Lappi",
           "name_official_en": "Lapland wellbeing services county",
           "name_official_fi": "Lapin hyvinvointialue",
           "type": "wellbeing_services_county", "sotkanet_id": 968, "include_in_national": True},
    "90": {"slug": "helsinki", "name": "Helsinki", "name_fi": "Helsinki",
           "name_official_en": "City of Helsinki", "name_official_fi": "Helsingin kaupunki",
           "type": "city", "sotkanet_id": 960, "include_in_national": True},
    "91": {"slug": "ahvenanmaa", "name": "Åland", "name_fi": "Ahvenanmaa",
           "name_official_en": "Åland", "name_official_fi": "Ahvenanmaa",
           "type": "autonomous_region", "sotkanet_id": 956, "include_in_national": False},
}

YTA_IDS = {
    "Etelä-Suomen yhteistyöalue": "yta-etela",
    "Itä-Suomen yhteistyöalue": "yta-ita",
    "Länsi-Suomen yhteistyöalue": "yta-lansi",
    "Pohjois-Suomen yhteistyöalue": "yta-pohjoinen",
    "Sisä-Suomen yhteistyöalue": "yta-sisa",
}
YTA_NAMES = {
    "yta-etela": {"name": "Southern Finland", "name_fi": "Etelä-Suomi", "official_fi": "Etelä-Suomen yhteistyöalue"},
    "yta-ita": {"name": "Eastern Finland", "name_fi": "Itä-Suomi", "official_fi": "Itä-Suomen yhteistyöalue"},
    "yta-lansi": {"name": "Western Finland", "name_fi": "Länsi-Suomi", "official_fi": "Länsi-Suomen yhteistyöalue"},
    "yta-pohjoinen": {"name": "Northern Finland", "name_fi": "Pohjois-Suomi", "official_fi": "Pohjois-Suomen yhteistyöalue"},
    "yta-sisa": {"name": "Inland Finland", "name_fi": "Sisä-Suomi", "official_fi": "Sisä-Suomen yhteistyöalue"},
}


BANNED_SOTKANET = ("6411", "2676", "6410")


def is_banned_sotkanet(name: str) -> bool:
    n = name.lower()
    return any(code in n for code in BANNED_SOTKANET)


def read_csv(name: str) -> list[dict]:
    # Sotkanet 6411 (and predecessor 2676) are all-cause primary-care waits, not cancer,
    # and are unreliable for Vantaa-Kerava/Helsinki. 6410 is the same family and is not
    # endorsed in FINDINGS.md — do not load any of them.
    if is_banned_sotkanet(name):
        return []
    path = DATA / "csv" / name
    if not path.exists():
        return []
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def num(v):
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None


def main():
    sources: dict[str, dict] = {}

    def add_source(sid, title, publisher, url, table=None, year=None, note=None):
        if sid in sources:
            return sid
        sources[sid] = {
            "id": sid,
            "title": title,
            "publisher": publisher,
            "url": url,
            "accessed": "2026-11-14",
            "year": year,
            "note": " — ".join([t for t in (table, note) if t]),
        }
        return sid

    add_source(
        "src-thl-2016",
        "Hoitoonpääsyn seuranta syövän hoidossa (THL Ohjaus 21/2016)",
        "Terveyden ja hyvinvoinnin laitos (THL)",
        "https://www.julkari.fi/items/0424a55a-f159-406f-8883-5dfdad4d6772",
        year=2016,
        note="Named by the National Cancer Strategy 2026–2035 as the reference for Goal 3 indicator 3. Generic maximum: 6 weeks (42 days) from referral arrival to first treatment. The PDF carries a 'Vanhentunut' watermark; no newer published target-time version was found.",
    )
    add_source(
        "src-strategy-2026",
        "Kansallinen syöpästrategia 2026–2035. Yhdessä syöpää vastaan – ihmislähtöistä syövän ehkäisyä ja hoitoa",
        "Sosiaali- ja terveysministeriö / FICAN / THL / Syöpäjärjestöt",
        "https://files.hackjunction.app/resources/Kansallinen_syopastrategia_2026_2035_FINAL.pdf",
        year=2026,
        note="Goal 3: Varmistetaan yhdenvertainen ja vaikuttava syövänhoito (S p. 5, p. 32).",
    )
    add_source(
        "src-roadmap-2026",
        "Kansallinen syöpästrategia: Toimeenpanon tiekartta vuosille 2026–2031",
        "Sosiaali- ja terveysministeriö / FICAN",
        "https://files.hackjunction.app/resources/Kansallinen_syopastrategia_toimeenpanon_tiekartta_2026_2031.pdf",
        year=2026,
    )
    add_source(
        "src-lung-2024-yta",
        "Keuhkosyöpä Suomessa (2024), Taulukko 4.1 — days from diagnosis to first treatment, by collaborative area",
        "Suomen Syöpärekisteri (Finnish Cancer Registry)",
        "https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf",
        table="Taulukko 4.1, printed p. 27 (PDF p. 28); diagnosed 1/2018–6/2022; manually transcribed from the table image",
        year=2024,
        note="Intervals start at diagnosis, not at referral. Published only for the five collaborative areas (YTA), not for the 22 counties.",
    )
    add_source(
        "src-lung-2026-t11",
        "Keuhkosyöpä Suomessa 2019–2023, Taulukko 11 — treatment groups by wellbeing services county",
        "Finnish Cancer Registry / THL / FICAN (published 23.4.2026)",
        "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
        table="Taulukko 11; crude shares, 12-month follow-up",
        year=2026,
        note="Curative-treatment share is a proxy for Goal 3-a (poor-prognosis survival). Shares are crude. The 'no treatment record' share varies widely by county and may reflect recording, not care.",
    )
    add_source(
        "src-lung-2026-kuva16",
        "Keuhkosyöpä Suomessa 2019–2023, Kuva 16 — age-standardised curative-treatment share by county and sex (chart estimate)",
        "Finnish Cancer Registry / THL / FICAN (published 23.4.2026)",
        "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
        table="Kuva 16 (Parantava panel); Tasan chart-digitised estimates ±1 pp; not a printed table",
        year=2026,
        note="Age-standardised share with surgery or curative radiotherapy within 12 months, by sex. Values and 95% CIs were read from the chart; they are not published as numbers. Not stage-adjusted, not survival. Kainuu is suppressed in the figure.",
    )
    add_source(
        "src-lung-2026-t4",
        "Keuhkosyöpä Suomessa 2019–2023, Taulukko 4 — stage-information coverage, whole country",
        "Finnish Cancer Registry / THL / FICAN (published 23.4.2026)",
        "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
        table="Taulukko 4 (N=14 873)",
        year=2026,
        note="Stage missing ('Ei tietoa') for 7 097 / 14 873 = 47.7%. Strategy sub-goal 3.2 target is 90% coverage.",
    )
    add_source(
        "src-sotkanet-6103",
        "Proportion of invited to colorectal cancer screening who attended, % (Sotkanet 6103)",
        "THL Sotkanet / Finnish Cancer Registry screening statistics",
        "https://sotkanet.fi/sotkanet/en/metadata/indicators/6103",
        table="Sotkanet 6103; data-updated 2026-06-12",
        year=2024,
    )
    add_source(
        "src-sotkanet-13",
        "Share of specialist-care referrals processed within 3 days (Sotkanet 13)",
        "THL Sotkanet",
        "https://sotkanet.fi/sotkanet/en/metadata/indicators/13",
        table="Sotkanet 13, 2025; all specialties, not cancer-specific; producer-based",
        year=2025,
        note="HUS reports for Uusimaa as a whole; several Uusimaa counties have no separate public figure.",
    )
    add_source(
        "src-thl-2017",
        "Hoitoonpääsyn seuranta syövän hoidossa — hankkeen loppuraportti (THL Työpaperi 3/2017)",
        "Terveyden ja hyvinvoinnin laitos (THL)",
        "https://www.julkari.fi/items/c296653c-356e-4742-a029-ddab51cd0aab",
        year=2017,
        note="“Kansallinen seuranta syöpään sairastuneiden hoitoonpääsystä on puuttunut.”",
    )
    add_source(
        "src-geo-statfin-2026",
        "Wellbeing services county boundaries 2026, scale 1:4 500 000 (hyvinvointialue4500k_2026)",
        "Statistics Finland (Tilastokeskus), geo.stat.fi",
        "https://geo.stat.fi/",
        year=2026,
        note="Licence: CC BY 4.0. Used only for the map geometry.",
    )

    # --- YTA wait times ---
    yta_rows = read_csv("lung_report2024_days_dx_to_first_treatment_by_yta.csv")
    modality = {
        "surgery": "lung_dx_to_surgery_days",
        "radiotherapy": "lung_dx_to_radiotherapy_days",
        "drug therapy": "lung_dx_to_drug_days",
    }

    def yta_id_from_row(r: dict) -> str:
        code = (r.get("region_code") or "").upper()
        mapping = {
            "YTA-ETELA": "yta-etela",
            "YTA-ITA": "yta-ita",
            "YTA-LANSI": "yta-lansi",
            "YTA-POHJOIS": "yta-pohjoinen",
            "YTA-SISA": "yta-sisa",
        }
        if code in mapping:
            return mapping[code]
        n = f"{r.get('region','')} {r.get('region_name_fi','')}".lower()
        if "etelä" in n or "etela" in n or "south finland" in n:
            return "yta-etela"
        if "itä" in n or "east finland" in n:
            return "yta-ita"
        if "länsi" in n or "lansi" in n or "west finland" in n:
            return "yta-lansi"
        if "pohjois" in n or "north finland" in n:
            return "yta-pohjoinen"
        if "sisä" in n or "sisa" in n or "inland finland" in n:
            return "yta-sisa"
        raise ValueError(r.get("region") or r.get("region_code"))

    yta_waits: dict[str, dict] = {k: {**v, "id": k, "modalities": {}} for k, v in YTA_NAMES.items()}
    for r in yta_rows:
        yid = yta_id_from_row(r)
        ind = r["indicator"].lower()
        key = None
        if "surgery" in ind:
            key = "surgery"
        elif "radiotherapy" in ind:
            key = "radiotherapy"
        elif "drug" in ind:
            key = "drug"
        else:
            continue
        yta_waits[yid]["modalities"][key] = {
            "median": num(r["value"]),
            "q1": num(r.get("q1")),
            "q3": num(r.get("q3")),
            "unit": r["unit"],
            "year": r["year"],
            "source_id": "src-lung-2024-yta",
            "source_url": r["source_url"],
            "source_table": r["source_table"],
            "indicator": r["indicator"],
            "caveat": r.get("caveat") or None,
            "n": r.get("n") or None,
            "label_exact": "diagnosis to surgery, 2018 to mid-2022, by home region, surgical patients only (~11%)" if key=="surgery" else None,
        }
        yta_waits[yid]["source_id"] = "src-lung-2024-yta"

    # --- Curative share + YTA membership ---
    treat = read_csv("lung_report2026_treatment_by_wsc.csv")
    curative = {}
    no_record = {}
    county_yta = {}
    for r in treat:
        code = r["region_code"]
        yid = YTA_IDS[r["collaborative_area_fi"]]
        county_yta[code] = yid
        rec = {
            "value": num(r["value"]),
            "numerator": int(r["numerator"]) if r["numerator"] else None,
            "denominator": int(r["denominator"]) if r["denominator"] else None,
            "ci95_low": num(r["ci95_low"]),
            "ci95_high": num(r["ci95_high"]),
            "year": "2019–2023",
            "source_id": "src-lung-2026-t11",
            "source_url": r["source_url"],
            "source_table": r["source_table"],
        }
        if r["treatment_group_fi"] == "Parantava":
            rec["ci_note"] = "95% CI compiled in the team CSV (Wilson intervals; not printed in Taulukko 11)."
            rec["definition"] = "Crude share with a curative-treatment record within 12 months. Not 5-year survival, not age-adjusted."
            curative[code] = rec
        elif r["treatment_group_fi"] == "Ei hoitotietoa":
            no_record[code] = rec


    def load_curative_agestd():
        """Kuva 16 chart-digitised age-standardised shares, by county and sex. Do not invent missing cells."""
        path = DATA / "csv" / "lung_report2026_curative_agestd_by_sex_chart_estimate.csv"
        out = {}
        if not path.exists():
            return out
        with path.open(encoding="utf-8", newline="") as fh:
            for row in csv.DictReader(fh):
                if (row.get("region_type") or "").strip() != "HYVINVOINTIALUE":
                    continue
                code = (row.get("region_code") or "").strip()
                if not code:
                    continue
                sex_raw = (row.get("sex") or "").strip().lower()
                sex = "men" if sex_raw in {"male", "men"} else "women" if sex_raw in {"female", "women"} else None
                if not sex:
                    continue
                try:
                    val = float(row["value"])
                    lo = float(row["ci95_low"])
                    hi = float(row["ci95_high"])
                except (TypeError, ValueError, KeyError):
                    continue
                out.setdefault(code, {})[sex] = {"value": val, "ci95": [lo, hi]}
        return out

    curative_agestd = load_curative_agestd()

    # National 27.0 is stated in key_findings (Taulukko 11) and equals the unweighted-cohort sum.
    nat_num = sum(r["numerator"] or 0 for r in curative.values())
    nat_den = sum(r["denominator"] or 0 for r in curative.values())
    nat_curative = {
        "value": 27.0,
        "numerator": 4009,
        "denominator": 14873,
        "year": "2019–2023",
        "source_id": "src-lung-2026-t11",
        "note": "National 27.0% (4,009 / 14,873) as published in the 2026 lung report text (Taulukko 11 family). County CIs in the team CSV are Wilson intervals compiled by the data team; they are not printed in Taulukko 11. This is a crude 12-month curative-treatment-record share, not 5-year survival.",
    }

    # --- Screening 6103 ---
    s6103 = read_csv("sotkanet_6103_screening_colorectal_attendance.csv")
    screen = {}
    screen_nat = None
    for r in s6103:
        if r["year"] != "2024" or r["sex"] != "total":
            continue
        rec = {
            "value": num(r["value"]),
            "abs_value": num(r["abs_value"]),
            "year": 2024,
            "source_id": "src-sotkanet-6103",
            "source_url": r["source_url"],
            "source_table": r["source_table"],
        }
        if r["region_code"] == "358":
            screen_nat = rec
        elif r["region_code"] in REGION_META:
            screen[r["region_code"]] = rec

    # men/women national for key message
    def pick_6103(code, sex):
        for r in s6103:
            if r["year"] == "2024" and r["sex"] == sex and r["region_code"] == code:
                return num(r["value"])
        return None

    # --- Referrals sotkanet 13 ---
    s13 = read_csv("sotkanet_13_esh_referrals_processed_within_3d.csv")
    ref = {}
    ref_nat = None
    for r in s13:
        if r["year"] != "2025" or r["sex"] != "total":
            continue
        rec = {
            "value": num(r["value"]),
            "year": 2025,
            "source_id": "src-sotkanet-13",
            "source_url": r["source_url"],
            "source_table": r["source_table"],
            "note": "All specialties, not cancer-specific. Producer-based reporting.",
        }
        if r["region_code"] == "358":
            ref_nat = rec
        elif r["region_code"] in REGION_META:
            ref[r["region_code"]] = rec

    # --- Stage coverage national ---
    stage_cov = read_csv("lung_report2026_stage_info_coverage_national.csv")
    stage_info = {
        "source_id": "src-lung-2026-t4",
        "n_total": 14873,
        "missing_n": 7097,
        "missing_pct": 47.7,
        "coverage_pct": 52.3,
        "target_pct": 90,
        "rows": [
            {"type": r["stage_info_type_fi"], "n": int(float(r["n"])), "pct": num(r["pct"])}
            for r in stage_cov
        ],
    }

    MISSING_COUNTY_WAIT = {
        "value": None,
        "year": None,
        "source_id": "src-lung-2024-yta",
        "missing": True,
        "missing_reason": "No public county-level statistic. Lung diagnosis-to-treatment times are published only for the five collaborative areas (YTA).",
    }

    def missing_ind(source_id, reason):
        return {
            "value": None,
            "year": None,
            "source_id": source_id,
            "missing": True,
            "missing_reason": reason,
        }

    catalog = [
        {
            "id": "colorectal_screening_share",
            "stage": "detection",
            "label": "Colorectal screening participation (invited who attended)",
            "label_fi": "Suolistosyövän seulontaan osallistuneiden osuus kutsutuista",
            "unit": "%",
            "higher_is_better": True,
            "decimals": 1,
            "target": 80,
            "target_source_id": "src-strategy-2026",
            "target_note": "Official Goal 2 follow-up metric: 80% participation in every wellbeing services county and Helsinki (S p. 5; R p. 48). Not a Goal 3 indicator — shown as pathway context.",
            "goal": "2",
            "goal3_indicator": None,
        },
        {
            "id": "referral_within_3d_share",
            "stage": "referral",
            "label": "Specialist-care referrals processed within 3 days (all specialties)",
            "unit": "%",
            "higher_is_better": True,
            "decimals": 1,
            "target": None,
            "target_source_id": "src-sotkanet-13",
            "target_note": "No official cancer-specific target. This is an all-specialty referral indicator, not a Goal 3 lung-cancer measure.",
            "goal": None,
            "goal3_indicator": None,
        },
        {
            "id": "lung_dx_to_surgery_days",
            "stage": "diagnosis",
            "label": "Lung cancer: median days from diagnosis to first surgery",
            "unit": "days",
            "higher_is_better": False,
            "decimals": 1,
            "target": 42,
            "target_source_id": "src-thl-2016",
            "target_note": "THL Ohjaus 21/2016: 6 weeks (42 days) from referral arrival to first treatment. The published medians start at diagnosis, so they understate time from referral. County-level values are not published.",
            "goal": "3",
            "goal3_indicator": "g3-treatment-within-target",
            "geo_level": "yta",
        },
        {
            "id": "lung_curative_share",
            "stage": "treatment",
            "label": "Lung cancer: age-adjusted share with curative treatment within 12 months (chart estimate, not survival)",
            "unit": "%",
            "higher_is_better": True,
            "decimals": 1,
            "target": None,
            "target_source_id": "src-lung-2026-kuva16",
            "target_note": "Chart estimate from Kuva 16 (±1 pp), age-adjusted, not stage-adjusted, not survival. Men's figure is used for the map colour. The crude Taulukko 11 share is shown only as a secondary line on the hero card.",
            "goal": "3",
            "goal3_indicator": "g3-survival-poor-prognosis",
        },
    ]

    def iv(ind_id, rec):
        if rec is None:
            return None
        out = {"id": ind_id, **rec}
        return out

    regions = []
    for rid, meta in REGION_META.items():
        indicators = []
        indicators.append(iv("colorectal_screening_share", screen.get(rid) or missing_ind(
            "src-sotkanet-6103", "No public figure for this region in Sotkanet 6103 (2024)."
        )))
        if rid in ref:
            indicators.append(iv("referral_within_3d_share", ref[rid]))
        else:
            indicators.append(iv("referral_within_3d_share", missing_ind(
                "src-sotkanet-13",
                "No public county figure. Sotkanet 13 is missing for this area in 2025 (HUS reports Uusimaa as a producer; Åland is outside the series).",
            )))
        # diagnosis wait: always missing at county level
        indicators.append(iv("lung_dx_to_surgery_days", {
            **MISSING_COUNTY_WAIT,
            "yta_id": county_yta.get(rid),
        }))
        agestd = curative_agestd.get(rid) or {}
        if agestd.get("men") and agestd.get("women"):
            men = agestd["men"]
            women = agestd["women"]
            indicators.append(iv("lung_curative_share", {
                "value": men["value"],
                "ci95_low": men["ci95"][0],
                "ci95_high": men["ci95"][1],
                "men": men,
                "women": women,
                "source_id": "src-lung-2026-kuva16",
                "source_table": "Kuva 16 (Parantava panel), chart-digitised ±1 pp",
                "measure_label": "chart estimate, age-adjusted, not stage-adjusted, not survival",
                "note": "Chart estimate from the report's age-standardised chart (Kuva 16, ±1 percentage point), not a printed table. Men's figure is used for the map colour. Not stage-adjusted, not survival. The crude share is shown only as a secondary line on the hero card.",
                "year": "2019-2023",
                "missing": False,
            }))
        else:
            indicators.append(iv("lung_curative_share", missing_ind(
                "src-lung-2026-kuva16",
                "No public age-adjusted figure in Kuva 16 for this county (chart estimate; some small counties are suppressed).",
            )))
        regions.append({
            "id": rid,
            **meta,
            "yta_id": county_yta.get(rid),
            "indicators": indicators,
        })

    national = {
        "id": "FI",
        "name": "Finland (national)",
        "name_fi": "Koko maa",
        "sotkanet_id": 658,
        "indicators": [
            iv("colorectal_screening_share", screen_nat),
            iv("referral_within_3d_share", ref_nat),
            iv("lung_dx_to_surgery_days", {
                "value": 37.0,
                "iqr": [0, 56],
                "unit": "days",
                "source_id": "src-lung-2024-yta",
                "source_table": "Keuhkosyöpä Suomessa (2024), national median from report text p.27; Taulukko 4.1 is YTA-only",
                "note": "National median 37 d (IQR 0–56, report text p.27); counties not published — YTA only.",
                "year": "2018-2022",
                "missing": False,
            }),
            iv("lung_curative_share", missing_ind(
                "src-lung-2026-kuva16",
                "No published national age-adjusted figure in Kuva 16 (the chart is by county). The map uses the county chart estimates.",
            )),
        ],
    }

    # Key message — hero is lung dx-to-treatment (overrides colorectal headline)
    hero_path = DATA / "hero.json"
    hero_in = {}
    if hero_path.exists():
        hero_in = json.loads(hero_path.read_text(encoding="utf-8"))

    TASAN_CLOCK_NOTE = (
        "Target per THL Ohjaus 21/2016 (marked outdated; no lung-specific limit; "
        "new cancer-specific targets due 2026-28, roadmap 3.1.2). "
        "Day-28 alert and 80% goal are Tasan design choices."
    )
    recs_src_early = RECS / "recommendations.json"
    recs_raw_early = json.loads(recs_src_early.read_text(encoding="utf-8")) if recs_src_early.exists() else {}
    recs_by_id = {r["id"]: r for r in (recs_raw_early.get("recommendations") or []) if r.get("id")}
    # Prefer fields from the strategist file so a regenerate is picked up on the next sync.
    lead_id = (
        recs_raw_early.get("lead_id")
        or recs_raw_early.get("centrepiece_id")
        or recs_raw_early.get("primary_rec_id")
        or "T3"
    )
    clock_note = (
        recs_raw_early.get("tasan_clock_note")
        or recs_raw_early.get("clock_note")
        or TASAN_CLOCK_NOTE
    )

    def rec_title(rid: str, fallback: str) -> str:
        r = recs_by_id.get(rid) or {}
        return r.get("title") or fallback

    def rec_pilot(rid: str) -> str:
        p = (recs_by_id.get(rid) or {}).get("pilot_county")
        return f" (pilot: {p})" if p else ""

    t3_title = rec_title("T3", "Tasan lung waiting-time tracker with day-28 alert and a named nurse navigator")
    t1_title = rec_title("T1", "Lung cancer one-stop diagnostic fast track")
    t2_title = rec_title("T2", "Regional thoracic MDT with remote participation")
    what_to_do = recs_raw_early.get("what_to_do") or (
        f"Lead with {lead_id}: {rec_title(lead_id, t3_title)}{rec_pilot(lead_id)}. "
        f"When the day-28 alert fires, the nurse navigator triggers T1 {t1_title}{rec_pilot('T1')} "
        f"and T2 {t2_title}{rec_pilot('T2')}."
    )
    headline = recs_raw_early.get("hero_headline") or recs_raw_early.get("headline") or (
        "No county publishes whether lung-cancer patients start treatment within six weeks of referral. "
        "That missing Goal 3 clock is why Tasan exists — the centrepiece is the waiting-time tracker "
        "with a day-28 alert and nurse navigator."
    )
    where_in = recs_raw_early.get("where_in_pathway") or (
        "Goal 3 asks whether patients start treatment within target timeframes. "
        + clock_note
        + " No public county statistic reports 6-week compliance. The published times start at diagnosis, "
        "cover only five collaborative areas, and only patients who received that treatment within six months."
    )

    default_km = {
        "headline": headline,
        "gap": (
            (hero_in.get("headlines") or [{}])[0].get("label")
            if isinstance(hero_in, dict) and (hero_in.get("headlines") or [{}])[0].get("id") == "lung_curative_share"
            else "The hero number is the age-adjusted lung curative-treatment share (chart estimate; men and women shown side by side). Other public signals are separate cohorts and years, not one patient journey, and are not a North-versus-South story."
        ),
        "where_in_pathway": where_in,
        "what_to_do": what_to_do,
        "primary_rec_id": lead_id,
        "tasan_clock_note": clock_note,
        "spotlight_stage": "treatment",
        "spotlight_indicator_id": "lung_curative_share",
        "source_ids": [
            "src-lung-2024-yta",
            "src-thl-2016",
            "src-strategy-2026",
            "src-thl-2017",
            "src-lung-2026-t11",
            "src-lung-2026-kuva16",
        ],
    }
    # allow hero.json to override any of these fields (flat or nested)
    def merge_hero(base, incoming):
        if not incoming:
            return base
        body = incoming.get("key_message") or incoming.get("hero") or incoming
        for k in base:
            if k in body and body[k]:
                base[k] = body[k]
        return base

    km_body = merge_hero(default_km, hero_in)
    # Lock the map default: age-adjusted curative share (Treat). Must not revert to surgery days.
    km_body["spotlight_stage"] = "treatment"
    km_body["spotlight_indicator_id"] = "lung_curative_share"

    key_message = {
        "meta": {
            "schema_version": "1.0",
            "updated": "2026-11-14",
            "hero_from_file": hero_path.exists(),
        },
        **km_body,
    }

    # --- Recommendations from strategist (transform) ---
    recs_src = RECS / "recommendations.json"
    recs_doc = {"meta": {"schema_version": "1.0", "is_example": True}, "goal3_indicators": [], "recommendations": []}
    recs_ok = False
    if recs_src.exists():
        raw = json.loads(recs_src.read_text(encoding="utf-8"))
        # import recs sources
        for key, s in (raw.get("sources") or {}).items():
            add_source(
                f"src-rec-{key.lower()}",
                s.get("title") or key,
                s.get("publisher") or "See title",
                s.get("url"),
                year=None,
            )
        g3map = {
            "G3-1": "g3-survival-poor-prognosis",
            "G3-2": "g3-mortality-reduction",
            "G3-3": "g3-treatment-within-target",
        }
        recs_doc["goal3_indicators"] = [
            {
                "id": "g3-survival-poor-prognosis",
                "label": "5-year survival of poor-prognosis cancers reaches the Nordic level",
                "strategy_ref": "National Cancer Strategy 2026–2035, Goal 3 (S p. 5)",
                "source_id": "src-strategy-2026",
            },
            {
                "id": "g3-mortality-reduction",
                "label": "Cancer mortality decreases by 10%",
                "strategy_ref": "National Cancer Strategy 2026–2035, Goal 3 (S p. 5)",
                "source_id": "src-strategy-2026",
            },
            {
                "id": "g3-treatment-within-target",
                "label": "Patients start treatment within target timeframes",
                "label_fi": "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa",
                "strategy_ref": "National Cancer Strategy 2026–2035, Goal 3 (S p. 5); THL Ohjaus 21/2016",
                "source_id": "src-thl-2016",
            },
        ]
        stage_of = {
            "late_detection": "detection",
            "referral": "referral",
            "diagnosis_to_treatment": "treatment",
        }
        # Optional numeric days effects for the simulator (clearly assumed unless the rec states a number)
        assumed_days = {
            "T1": {
                "delta_days": -14,
                "note": "ASSUMED what-if, not a Finnish impact estimate. The strategist notes that rapid-investigation and one-stop lung clinics shortened time to treatment by 2–3 weeks in comparable settings, and Norway saw lung surgery waits fall by 7 days. The simulator applies a 14-day (2-week) left shift of the published YTA medians, leaving the IQR width unchanged.",
                "source_id": "src-strategy-2026",
            },
            "C2": {
                "delta_days": -12,
                "note": "ASSUMED analogy, not a Finnish estimate: Toronto reflex EGFR/ALK testing, median time to treatment 34→22 days (Cheema 2017). Applied here only as a what-if on the YTA lung medians.",
                "source_id": "src-rec-cheema17",
            }
        }
        out_recs = []
        for r in raw.get("recommendations") or []:
            ev_ids = ["src-strategy-2026"]
            def as_text(v):
                if v is None:
                    return ""
                if isinstance(v, list):
                    parts = []
                    for item in v:
                        if isinstance(item, dict):
                            parts.append(" ".join(str(x) for x in item.values()))
                        else:
                            parts.append(str(item))
                    return " ".join(parts)
                if isinstance(v, dict):
                    return " ".join(str(x) for x in v.values())
                return str(v)
            ev = as_text(r.get("evidence"))
            effect_txt = as_text(r.get("expected_effect"))
            blob = ev + " " + effect_txt
            ev_raw = r.get("evidence")
            if isinstance(ev_raw, list):
                for item in ev_raw:
                    if not isinstance(item, dict):
                        continue
                    sid = item.get("source_id")
                    if sid:
                        ev_ids.append(add_source(
                            f"src-rec-{sid.lower()}",
                            item.get("source_title") or sid,
                            "See title",
                            item.get("url"),
                            note=item.get("claim"),
                        ))
            for key in (raw.get("sources") or {}):
                if re.search(rf"\b{re.escape(key)}\b", blob, re.I):
                    ev_ids.append(f"src-rec-{key.lower()}")
            ev_ids = list(dict.fromkeys(ev_ids))
            g3 = None
            for g in r.get("goal3_mapping") or []:
                g3 = g3map.get(g, g3)
            cost_txt = r.get("cost_estimate") or ""
            rec_out = {
                "id": r["id"],
                "title": r["title"],
                "stage": stage_of.get(r.get("bottleneck"), "treatment"),
                "what": r.get("action") or r.get("problem") or "",
                "who_implements": ", ".join(r.get("owners") or []) or None,
                "owner": (r.get("owners") or [None])[0],
                "cost": {
                    "label": cost_txt,
                    "basis": "Strategist estimate; figures marked ESTIMATE are not sourced prices.",
                    "source_id": "src-rec-kt24" if "KT 2024" in cost_txt else None,
                    "is_example": "ESTIMATE" in cost_txt,
                },
                "kpi": {
                    "name": (r.get("kpis") or [{}])[0].get("name") if r.get("kpis") else None,
                    "target": "Patients treated within THL 21/2016 target times (6 weeks from referral).",
                },
                "goal3_indicator": g3,
                "evidence": "\n\n".join(x for x in [(r.get("problem") or ""), effect_txt, ev] if x),
                "evidence_source_ids": ev_ids,
                "expected_effect": {
                    "indicator_id": "lung_dx_to_surgery_days",
                    "direction": "decrease",
                    "unit": "days",
                    "source_id": ev_ids[-1] if ev_ids else "src-strategy-2026",
                    "assumptions": effect_txt or "No verified Finnish effect size.",
                    "is_example": r["id"] not in assumed_days,
                },
                "priority": r.get("priority"),
                "first_90_days": r.get("first_90_days"),
                "risks": r.get("risks"),
            }
            if r["id"] in assumed_days:
                a = assumed_days[r["id"]]
                rec_out["expected_effect"]["delta"] = a["delta_days"]
                rec_out["expected_effect"]["assumptions"] = a["note"]
                rec_out["expected_effect"]["is_example"] = False
                rec_out["expected_effect"]["is_assumed"] = True
                rec_out["expected_effect"]["source_id"] = a["source_id"]
                rec_out["effect_params"] = {
                    "type": "linear",
                    "applies_to_indicator": "lung_dx_to_surgery_days",
                    "effect_at_full_coverage": a["delta_days"],
                    "max_coverage": 1.0,
                    "applicable_regions": ["*"],
                    "geo_level": "yta",
                    "clamp_min": 0,
                    "clamp_max": 365,
                    "assumption_note": a["note"],
                }
            out_recs.append(rec_out)
        recs_doc["recommendations"] = out_recs
        recs_doc["meta"] = {
            "schema_version": "1.0",
            "updated": raw.get("generated", "2026-11-14"),
            "disclaimer": raw.get("note"),
            "author": raw.get("author"),
        }
        recs_ok = len(out_recs) > 0
        # Prefer the strategist's real schema (top3, priority_rank, nonpriority, pilot_county, data_basis, kpis…).
        recs_doc = dict(raw)
        recs_doc["meta"] = {
            "schema_version": "1.0",
            "updated": raw.get("generated", "2026-11-14"),
            "disclaimer": raw.get("note"),
            "author": raw.get("author"),
            "passthrough": True,
        }
        recs_doc["lead_id"] = raw.get("lead_id") or raw.get("centrepiece_id") or raw.get("primary_rec_id") or lead_id
        recs_doc["tasan_clock_note"] = raw.get("tasan_clock_note") or raw.get("clock_note") or clock_note
        top_ids = recs_doc.get("top3_ids") or [r.get("id") for r in recs_doc.get("recommendations") or [] if r.get("top3")]
        lid = recs_doc["lead_id"]
        recs_doc["display_ids"] = raw.get("display_ids") or ([lid] + [i for i in top_ids if i and i != lid])
        if "what_to_do" not in recs_doc and what_to_do:
            recs_doc["what_to_do"] = what_to_do
        if isinstance(recs_doc.get("goal3_indicators"), dict):
            recs_doc["goal3_indicators_by_code"] = recs_doc["goal3_indicators"]
            recs_doc["goal3_indicators"] = [
                {"id": str(code), "label": label, "strategy_ref": label}
                for code, label in recs_doc["goal3_indicators_by_code"].items()
            ]
        # Keep the strategist's fields, but fill the few UI/validator keys if a regenerate omits them.
        stage_of_norm = {
            "late_detection": "detection",
            "referral": "referral",
            "diagnosis_to_treatment": "treatment",
        }
        for r in recs_doc.get("recommendations") or []:
            if not r.get("what"):
                r["what"] = r.get("action") or r.get("problem") or ""
            if not r.get("stage"):
                r["stage"] = stage_of_norm.get(r.get("bottleneck"), "treatment")
            if r.get("goal3_mapping") and not r.get("goal3_indicator"):
                gmap = {"G3-1": "g3-survival-poor-prognosis", "G3-2": "g3-mortality-reduction", "G3-3": "g3-treatment-within-target"}
                gm = r.get("goal3_mapping")
                if isinstance(gm, list) and gm:
                    r["goal3_indicator"] = gmap.get(gm[0], gm[0])
                elif isinstance(gm, str):
                    r["goal3_indicator"] = gmap.get(gm, gm)

    regions_doc = {
        "meta": {
            "schema_version": "1.0",
            "title": "Tasan — public aggregate cancer-pathway dataset",
            "disclaimer": "Public aggregate data only, compiled 2026-11-14. Lung diagnosis-to-treatment times are published only for collaborative areas (YTA), not counties — county cells are shown as “No public data”, never interpolated. Sotkanet 6411, 2676 and 6410 (all-cause primary-care waits, not cancer; Avohilmo gaps in Vantaa, Kerava and Helsinki) are excluded and not shown. The map and county treatment panel use age-adjusted curative-treatment shares (Kuva 16 chart estimates, ±1 pp). The crude Taulukko 11 shares are not shown there. The THL 6-week target starts at referral; published lung intervals start at diagnosis.",
            "updated": "2026-11-14",
            "national_aggregation": "National colorectal screening and referral figures are the Sotkanet “Whole country” (code 358) rows. National lung curative share 27.0% is the published Taulukko 11 / key_findings figure (matches the 22-county numerator sum).",
        },
        "stages": [
            {"id": "detection", "label": "Detection", "label_fi": "Toteaminen", "order": 1, "short": "Detect"},
            {"id": "referral", "label": "Primary → specialist referral", "label_fi": "Lähete", "order": 2, "short": "Refer"},
            {"id": "diagnosis", "label": "Diagnosis → treatment", "label_fi": "Diagnoosista hoitoon", "order": 3, "short": "Dx→Tx"},
            {"id": "treatment", "label": "Treatment (curative share)", "label_fi": "Hoidon aloitus / parantava hoito", "order": 4, "short": "Treat"},
        ],
        "indicator_catalog": catalog,
        "national": national,
        "regions": regions,
        "target_days": {
            "referral_to_treatment_days": 42,
            "label": "6 weeks from referral arrival to first treatment",
            "source_id": "src-thl-2016",
        },
    }

    hero_out = {
        "mode": "lung_dx_to_treatment",
        "product_name": "Tasan",
        "target_times_caveat": recs_raw_early.get("target_times_caveat"),
        "tasan_clock_note": clock_note,
        "lead_id": lead_id,
        "target_days": 42,
        "target_source_id": "src-thl-2016",
        "yta_waits": list(yta_waits.values()),
        "county_yta": county_yta,
        "stage_coverage": stage_info,
        "key_facts": {
            "surgery_min": {"yta_id": "yta-pohjoinen", "days": 13.5},
            "surgery_max": {"yta_id": "yta-etela", "days": 46.0},
            "ratio": 3.4,
            "curative_min": {"region_id": "21", "value": 16.2, "ci": [12.7, 20.4], "sex": "men", "measure": "age-adjusted chart estimate"},
            "curative_max": {"region_id": "04", "value": 29.8, "ci": [24.2, 36.1], "sex": "men", "measure": "age-adjusted chart estimate"},
            "stage_missing_pct": 47.7,
        },
        "secondary": {
            "colorectal": {
                "national_2024": screen_nat["value"] if screen_nat else None,
                "men": pick_6103("358", "male"),
                "women": pick_6103("358", "female"),
                "counties_at_target": 0,
                "counties": 22,
                "lowest": {"region_id": "90", "value": 69.6},
                "source_id": "src-sotkanet-6103",
            }
        },
    }

    # Pass data/hero.json headlines, caveats and target_reference through UNCHANGED
    # so the UI can render them verbatim (no retyping).
    if hero_in:
        for k in ("project", "generated", "goal", "target_reference", "headlines", "excluded", "people_number"):
            if k in hero_in:
                hero_out[k] = hero_in[k]
        hero_out["hero_from"] = "data/hero.json"

    # Crude Taulukko 11 shares for the county gap bar (not used to colour the map).
    crude_path = DATA / "csv" / "lung_report2026_treatment_by_wsc.csv"
    if crude_path.exists():
        import csv as _csv
        nat_n, nat_N = 4009, 14873
        p_nat = nat_n / nat_N
        counties = []
        for row in _csv.DictReader(crude_path.open(encoding="utf-8")):
            if row.get("treatment_group_fi") != "Parantava" or row.get("sex") != "total":
                continue
            code = str(row.get("region_code") or "")
            if code in {"358", ""}:
                continue
            n, N = int(row["numerator"]), int(row["denominator"])
            share = n / N
            gap_5y = p_nat * N - n
            counties.append({
                "code": code,
                "region": row.get("region"),
                "n": n,
                "N": N,
                "share_pct": round(100 * share, 1),
                "gap_5y": round(gap_5y, 1) if share < p_nat else 0,
                "gap_per_year": round(gap_5y / 5, 1) if share < p_nat else 0,
                "below_national": share < p_nat,
            })
        hero_out["crude_curative"] = {
            "national_pct": 27.0,
            "national_n": nat_n,
            "national_N": nat_N,
            "national_share": round(p_nat, 4),
            "period": "diagnosed 2019-2023, 12-month follow-up",
            "source_table": "Keuhkosyöpä Suomessa 2019-2023, Taulukko 11",
            "source_url": "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
            "measure_label": "crude share, not age- or stage-adjusted, not survival",
            "counties": counties,
        }

    # Drop any banned Sotkanet artefacts
    # The exclusion rationale in hero.excluded may mention those codes; that is allowed.
    def _banned_payload(obj) -> bool:
        if isinstance(obj, dict):
            sid = str(obj.get("id") or obj.get("source_id") or "")
            if is_banned_sotkanet(sid) or sid.startswith("src-sotkanet-6411") or sid.startswith("src-sotkanet-2676") or sid.startswith("src-sotkanet-6410"):
                return True
        return False

    sources = {k: v for k, v in sources.items() if not is_banned_sotkanet(k) and not _banned_payload(v)}

    sources_doc = {
        "meta": {"schema_version": "1.0", "updated": "2026-11-14"},
        "sources": list(sources.values()),
    }

    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "regions.json").write_text(json.dumps(regions_doc, ensure_ascii=False, indent=2) + "\n")
    (OUT / "sources.json").write_text(json.dumps(sources_doc, ensure_ascii=False, indent=2) + "\n")
    (OUT / "key_message.json").write_text(json.dumps(key_message, ensure_ascii=False, indent=2) + "\n")
    (OUT / "recommendations.json").write_text(json.dumps(recs_doc, ensure_ascii=False, indent=2) + "\n")
    (OUT / "hero.json").write_text(json.dumps(hero_out, ensure_ascii=False, indent=2) + "\n")

    # Copy counties geo if not already there — caller handles geo copy
    # Hard fail if a banned source id reached the extract (excluded-rationale text is OK).
    for fp in (OUT / "hero.json", OUT / "sources.json", OUT / "regions.json", OUT / "key_message.json"):
        raw = fp.read_text(encoding="utf-8")
        if "src-sotkanet-6411" in raw or "src-sotkanet-2676" in raw or "src-sotkanet-6410" in raw:
            raise SystemExit(f"extract: banned Sotkanet source id leaked into {fp.name}")
    print(f"extract_team_data: wrote {OUT}")
    print(f"  regions={len(regions)} sources={len(sources)} recs={len(recs_doc['recommendations'])} recs_ok={recs_ok} hero_file={hero_path.exists()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
