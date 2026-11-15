"""Aggregate job outputs -> results/sim_results.json + results/sim_summary.csv + model fact cards.
Cards are type 'model' (VERDA_PLAN guardrail 8): the analyst must say 'modelled' when citing them."""
from __future__ import annotations
import argparse, csv, glob, json, sys
from pathlib import Path
from .common import CHIP, BUILD_DIR, load_json, dump_json

KEY = ["pct_le42_from_referral", "median_days_referral_to_treatment", "n_le42_from_referral"]

def fmt(s):
    return None if s["median"] is None else f"{s['median']:.1f} ({s['p2_5']:.1f}-{s['p97_5']:.1f})"

def main(argv=None):
    ap = argparse.ArgumentParser(); ap.add_argument("--results", default="results"); a = ap.parse_args(argv)
    files = sorted(glob.glob(f"{a.results}/*/*.json"))
    files = [f for f in files if Path(f).parent.name not in ("validation", "calibration")]
    if not files:
        print("no job outputs found", file=sys.stderr); return 1
    by = {}; rows = []
    for f in files:
        r = load_json(f); c, s = r["job"]["county"], r["job"]["scenario"]
        e = by.setdefault(c, {"county": r["county"], "baseline": None, "scenarios": {}})
        if s == "baseline":
            e["baseline"] = {k: r["baseline"][k] for k in r["baseline"]}
            e["sensitivity_ref_to_dx"] = r["sensitivity_pct_le42_from_referral_by_ref_to_dx_median_days"]
        e["scenarios"][s] = {"label": r["scenario"]["label"], "source": r["scenario"].get("source"),
                             "scenario_arm": {k: r["scenario_arm"][k] for k in KEY},
                             "delta_vs_baseline": {k: r["delta_vs_baseline"][k] for k in KEY},
                             "seed": r["job"]["seed"], "n_runs": r["job"]["n_runs"]}
        for arm, blk in (("baseline", r["baseline"]), ("scenario", r["scenario_arm"]), ("delta", r["delta_vs_baseline"])):
            for m in blk:
                rows.append({"county": c, "county_name": r["county"]["name_en"], "area": r["county"]["area"], "scenario": s,
                             "arm": arm, "metric": m, **{k: blk[m][k] for k in ("mean", "p2_5", "median", "p97_5")}})
    cards = []
    for c, e in sorted(by.items()):
        b = e["baseline"]
        if not b:
            continue
        name = e["county"]["name_en"]
        cards.append({"id": f"model.{c}.baseline.pct_le42_from_referral", "type": "model", "chip": CHIP,
                      "statement_en": f"Modelled: in {name}, an estimated {fmt(b['pct_le42_from_referral'])}% of lung cancer patients who got surgery, radiotherapy or drug therapy within 6 months started it within 42 days of referral (median, 95% interval). The width comes mainly from the unpublished referral-to-diagnosis time.",
                      "value": b["pct_le42_from_referral"], "unit": "%", "region": name,
                      "source": "Tasan Pathway Twin (sim/), calibrated to Keuhkosyöpä Suomessa 2024 Taulukko 4.1/4.5; volumes Taulukko 11 (2026)",
                      "caveat": "MODEL OUTPUT; referral->diagnosis is an ASSUMPTION (7-35 d median); county timing inherited from collaborative area."})
        cards.append({"id": f"model.{c}.baseline.pct_le42_from_diagnosis", "type": "model", "chip": CHIP,
                      "statement_en": f"Modelled: in {name}, an estimated {fmt(b['pct_le42_from_diagnosis'])}% of actively treated lung cancer patients started treatment within 42 days of the registry diagnosis date (collaborative-area timing).",
                      "value": b["pct_le42_from_diagnosis"], "unit": "%", "region": name,
                      "source": "Tasan Pathway Twin calibrated to Keuhkosyöpä Suomessa 2024 Taulukko 4.1/4.5",
                      "caveat": "Diagnosis-anchored, not the THL referral-anchored target; registry diagnosis date can equal the treatment date."})
        for s, sc in e["scenarios"].items():
            if s == "baseline":
                continue
            d = sc["delta_vs_baseline"]["pct_le42_from_referral"]
            cards.append({"id": f"model.{c}.{s}.delta_pct_le42_from_referral", "type": "model", "chip": CHIP,
                          "statement_en": f"Modelled what-if ({sc['label']}) in {name}: change in % starting within 42 days of referral = {fmt(d)} percentage points.",
                          "value": d, "unit": "percentage points", "region": name, "source": sc["source"],
                          "caveat": "What-if only; effect sizes transferred from other interventions/countries (ASSUMPTION)."})
    calib = load_json(BUILD_DIR / "calibration_report.json") if (BUILD_DIR / "calibration_report.json").exists() else None
    out = {"chip": CHIP, "type": "model", "n_jobs": len(files), "counties": by, "fact_cards": cards,
           "calibration_pass": calib["pass"] if calib else None,
           "output_scope": "pathway timings and shares only (time to first treatment, % within 42 days); no outcome effects are modelled"}
    dump_json(out, f"{a.results}/sim_results.json")
    with open(f"{a.results}/sim_summary.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print(f"aggregated {len(files)} jobs, {len(by)} counties, {len(cards)} model cards -> {a.results}/sim_results.json")
    return 0

if __name__ == "__main__":
    sys.exit(main())
