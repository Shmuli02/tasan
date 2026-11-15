"""Parameter provenance registry -> build/parameters.json.

Every input the microsimulation consumes is listed with kind = sourced | calibrated | derived | assumption | design
and a source (file + table + URL) or an explicit ASSUMPTION/DESIGN label.
"""
from __future__ import annotations
from .common import BUILD_DIR, CONFIG_DIR, AREAS, EVENTS, ACTIVE, load_json, dump_json

# Inputs read by twin/model.py (validate.py checks that each has a registry entry with provenance).
MODEL_INPUTS = [
    "area.first_event_share_month6", "area.n_patients", "area.timing_posterior",
    "county.annual_volume", "county.area",
    "assumption.ref_to_dx_median_days", "assumption.ref_to_dx_sigma", "assumption.target_days",
    "assumption.alert_day", "assumption.month_days", "assumption.cohort_volume_poisson",
    "scenario.effect_days", "scenario.crowding_extra_days",
]

def build():
    t = load_json(BUILD_DIR / "targets.json"); post = load_json(BUILD_DIR / "posterior.json")
    assump = load_json(CONFIG_DIR / "assumptions.json")["items"]
    scen = load_json(CONFIG_DIR / "scenarios.json")["scenarios"]
    P = []
    for a in AREAS:
        at = t["areas"][a]
        for k in EVENTS + ["none"]:
            P.append({"id": f"area.first_event_share_month6[{a}][{k}]", "group": "area.first_event_share_month6", "kind": "sourced",
                      "value": at["cum_first_event_pct"][k][6], "unit": "% of all patients",
                      "source": at["cum_source"], "note": "Dirichlet uncertainty with pseudo-counts share x n_patients (derived)"})
        P.append({"id": f"area.n_patients[{a}]", "group": "area.n_patients", "kind": "sourced", "value": at["n_patients"],
                  "unit": "patients diagnosed 1/2018-6/2022", "source": at["n_patients_source"]})
        for k in EVENTS:
            pk = post["areas"][a][k]
            P.append({"id": f"area.timing_posterior[{a}][{k}]", "group": "area.timing_posterior", "kind": "calibrated",
                      "value": {"n_particles": pk["n_particles"], "posterior_median_days": pk["posterior_median_days"], "posterior_pi0_median": pk["posterior_pi0_median"]},
                      "source": {"calibrated_to": [at["cum_source"]] + ([at["quantiles_source"]] if k in ACTIVE else []),
                                 "method": "ABC rejection, config/calibration.json", "file": "build/posterior.json"}})
    for c in t["counties"]:
        P.append({"id": f"county.annual_volume[{c['code']}]", "group": "county.annual_volume", "kind": "derived",
                  "value": c["annual_volume"], "unit": "patients/year", "source": c["source"]})
        P.append({"id": f"county.area[{c['code']}]", "group": "county.area", "kind": "sourced", "value": c["area"],
                  "source": {**c["source"], "column": "collaborative_area_fi"}})
    for a in assump:
        kind = {"ASSUMPTION": "assumption", "DESIGN": "design", "SOURCED": "sourced"}[a["label"]]
        P.append({"id": f"assumption.{a['id']}", "group": f"assumption.{a['id']}", "kind": kind, "label": a["label"],
                  "value": a.get("value", a.get("range")), "unit": a.get("unit"),
                  "source": a.get("source") or ("ASSUMPTION: " + a["why"])})
    for s in scen:
        if s.get("intervention"):
            P.append({"id": f"scenario.effect_days[{s['id']}]", "group": "scenario.effect_days", "kind": "assumption" if s["id"] != "zero_effect" else "design",
                      "label": "ASSUMPTION (effect_transfer)" if s["id"] != "zero_effect" else "DESIGN (zero-effect control)",
                      "value": s["effect_days"], "source": s["source"]})
            if "crowding_extra_days" in s:
                P.append({"id": f"scenario.crowding_extra_days[{s['id']}]", "group": "scenario.crowding_extra_days", "kind": "assumption",
                          "label": "ASSUMPTION", "value": s["crowding_extra_days"], "source": s["source"]})
    out = {"model_inputs": MODEL_INPUTS, "parameters": P}
    dump_json(out, BUILD_DIR / "parameters.json")
    return out

if __name__ == "__main__":
    o = build(); print(len(o["parameters"]), "parameters registered")
