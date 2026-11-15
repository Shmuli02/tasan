"""Microsimulation of the lung-cancer pathway for one county x scenario.

Per simulated year (one 'run'):
  1. parameter uncertainty: one ABC particle per first-event type, Dirichlet first-event mix,
     referral->diagnosis ASSUMPTION draw, scenario effect draw;
  2. cohort: Poisson(annual volume) newly diagnosed lung cancer patients;
  3. each patient: first event type (6-month horizon); if surgery/radiotherapy/drug, diagnosis->treatment days
     from the calibrated mixture; referral->diagnosis days from the ASSUMPTION lognormal;
  4. baseline and scenario are evaluated on the SAME patients (common random numbers),
     so deltas are paired and a zero effect gives exactly zero.
Outputs are timings/shares only.
"""
from __future__ import annotations
import time
import numpy as np
from .common import (BUILD_DIR, CONFIG_DIR, CHIP, ACTIVE, EVENTS, load_json, sha256_file, sample_mix, norm_ppf)
from . import __version__

CATS = EVENTS + ["none"]
SENS_MEDIANS = [7, 14, 21, 28, 35]
SENS_SIGMA = 0.65
METRICS = {
    "pct_le42_from_referral": "% of patients with a first active treatment (surgery, non-palliative RT, drug) within 6 months of diagnosis who started it <=42 days after referral arrival [depends on ASSUMPTION ref_to_dx]",
    "pct_le42_from_diagnosis": "% of the same patients who started <=42 days after the Cancer Registry diagnosis date [data-anchored; baseline only]",
    "median_days_referral_to_treatment": "median days referral arrival -> first active treatment [depends on ASSUMPTION ref_to_dx]",
    "median_days_diagnosis_to_treatment": "median days diagnosis -> first active treatment [data-anchored; baseline only]",
    "n_patients": "simulated newly diagnosed lung cancer patients in the year",
    "n_active_treated": "patients with a first active treatment within 6 months",
    "n_le42_from_referral": "patients per year starting first active treatment <=42 days after referral",
    "n_untreated_at_alert_day": "actively treated patients still untreated at day 28 after referral = day-28 alerts per year among them (lower bound on alert volume; baseline only)",
}
DX_ONLY = {"pct_le42_from_diagnosis", "median_days_diagnosis_to_treatment", "n_untreated_at_alert_day"}  # baseline-only metrics

class Inputs:
    def __init__(self):
        self.targets = load_json(BUILD_DIR / "targets.json")
        self.posterior = load_json(BUILD_DIR / "posterior.json")
        self.cal = load_json(CONFIG_DIR / "calibration.json")
        self.assump = {a["id"]: a for a in load_json(CONFIG_DIR / "assumptions.json")["items"]}
        self.scenarios = {s["id"]: s for s in load_json(CONFIG_DIR / "scenarios.json")["scenarios"]}
        self.counties = {c["code"]: c for c in self.targets["counties"]}
        self.provenance = {f: sha256_file(BUILD_DIR / f) for f in ("targets.json", "posterior.json")}
        for f in ("calibration.json", "assumptions.json", "scenarios.json"):
            self.provenance[f"config/{f}"] = sha256_file(CONFIG_DIR / f)

def _effect(rng, spec):
    if spec["dist"] == "fixed":
        return float(spec["value"])
    if spec["dist"] == "normal_from_ci":
        lo, hi = spec["ci95"]; sd = (hi - lo) / (2 * 1.959964)
        return max(spec.get("min", 0.0), float(rng.normal(spec["mean"], sd)))
    raise ValueError(spec)

def simulate_year(inp: Inputs, county, scenario, seed, run):
    area = county["area"]; at = inp.targets["areas"][area]; post = inp.posterior["areas"][area]
    T = inp.cal["horizon_days"]; target = inp.assump["target_days"]["value"]; alert = inp.assump["alert_day"]["value"]
    cint = int(county["code"])
    ss = np.random.SeedSequence([int(seed), cint, int(run)])
    s_par, s_coh, s_int = ss.spawn(3)
    rp, rc, ri = (np.random.default_rng(x) for x in (s_par, s_coh, s_int))
    # 1. parameters
    share = np.array([at["cum_first_event_pct"][k][6] for k in CATS], float)
    share = share / share.sum()
    mix = rp.dirichlet(share * at["n_patients"] + 0.5)
    part = {k: int(rp.integers(len(post[k]["particles"]["pi0"]))) for k in ACTIVE}
    m_lo, m_hi = inp.assump["ref_to_dx_median_days"]["range"]; s_lo, s_hi = inp.assump["ref_to_dx_sigma"]["range"]
    r_med = rp.uniform(m_lo, m_hi); r_sig = rp.uniform(s_lo, s_hi)
    # 2. cohort
    n = int(rc.poisson(county["annual_volume"]))
    cats = rc.choice(len(CATS), size=n, p=mix)
    d_list = []
    for ki, k in enumerate(ACTIVE):
        idx = CATS.index(k); m = int((cats == idx).sum())
        p = post[k]["particles"]; j = part[k]
        d_list.append(sample_mix(rc, m, p["pi0"][j], p["mu"][j], p["sigma"][j], T))
    D = np.rint(np.concatenate(d_list)) if d_list else np.zeros(0)
    z = norm_ppf(rc.random(D.size))
    R = np.rint(r_med * np.exp(r_sig * z))
    tot = R + D
    # 3. scenario (intervention stream only)
    sc = inp.scenarios[scenario]
    tot_s = tot.copy()
    if sc.get("intervention"):
        E = _effect(ri, sc["effect_days"])
        crowd = 0.0
        if "crowding_extra_days" in sc:
            crowd = float(ri.uniform(*sc["crowding_extra_days"]["range"]))
        alerted = tot > alert
        tot_s = np.where(alerted, np.maximum(alert, tot - E), tot + np.rint(crowd))
    def metrics(t, with_dx):
        na = t.size
        out = {"n_patients": n, "n_active_treated": na,
               "pct_le42_from_referral": 100.0 * np.mean(t <= target) if na else np.nan,
               "median_days_referral_to_treatment": float(np.median(t)) if na else np.nan,
               "n_le42_from_referral": int((t <= target).sum()),
               "n_untreated_at_alert_day": int((t > alert).sum())}
        if with_dx:
            out["pct_le42_from_diagnosis"] = 100.0 * np.mean(D <= target) if na else np.nan
            out["median_days_diagnosis_to_treatment"] = float(np.median(D)) if na else np.nan
        return out
    base = metrics(tot, True); scen = metrics(tot_s, True)
    sens = {}
    for med in SENS_MEDIANS:
        Rm = np.rint(med * np.exp(SENS_SIGMA * z))
        sens[str(med)] = 100.0 * np.mean(Rm + D <= target) if D.size else np.nan
    return base, scen, sens, {"ref_to_dx_median": r_med, "ref_to_dx_sigma": r_sig}

def _summ(x):
    x = np.asarray(x, float); x = x[~np.isnan(x)]
    if x.size == 0:
        return {"mean": None, "p2_5": None, "median": None, "p97_5": None, "n_runs_valid": 0}
    r = lambda v: round(float(v), 4)
    return {"mean": r(x.mean()), "p2_5": r(np.percentile(x, 2.5)), "median": r(np.median(x)),
            "p97_5": r(np.percentile(x, 97.5)), "n_runs_valid": int(x.size)}

def run_job(county_code, scenario, seed=1, n_runs=1000, inputs: Inputs | None = None):
    t0 = time.time()
    inp = inputs or Inputs()
    if scenario not in inp.scenarios:
        raise SystemExit(f"unknown scenario {scenario!r}; choose from {sorted(inp.scenarios)}")
    code = str(county_code).zfill(2)
    if code not in inp.counties:
        raise SystemExit(f"unknown county {county_code!r}; choose from {sorted(inp.counties)}")
    county = inp.counties[code]
    B = {k: [] for k in METRICS}; S = {k: [] for k in METRICS}; Dl = {k: [] for k in METRICS}
    sens = {str(m): [] for m in SENS_MEDIANS}
    for r in range(n_runs):
        b, s, se, _ = simulate_year(inp, county, scenario, seed, r)
        for k in METRICS:
            B[k].append(b[k]); S[k].append(s[k]); Dl[k].append(s[k] - b[k])
        for m in sens:
            sens[m].append(se[m])
    sc = inp.scenarios[scenario]
    res = {
        "chip": CHIP, "type": "model", "model": "Tasan Pathway Twin", "version": __version__,
        "job": {"county": code, "scenario": scenario, "seed": int(seed), "n_runs": int(n_runs)},
        "county": {k: county[k] for k in ("code", "name_en", "name_fi", "area", "annual_volume", "n_patients_5y", "years")},
        "county_source": county["source"],
        "scenario": {k: sc[k] for k in sc},
        "metric_definitions": METRICS,
        "baseline": {k: _summ(v) for k, v in B.items()},
        "scenario_arm": {k: _summ(v) for k, v in S.items() if k not in DX_ONLY},
        "delta_vs_baseline": {k: _summ(v) for k, v in Dl.items() if k not in DX_ONLY},
        "sensitivity_pct_le42_from_referral_by_ref_to_dx_median_days": {
            "sigma": SENS_SIGMA, "values": {m: _summ(v) for m, v in sens.items()}},
        "interval_note": "2.5-97.5 percentiles across simulated years; combine calibration-posterior, first-event-mix, referral->diagnosis ASSUMPTION, effect and cohort (Poisson) uncertainty.",
        "assumptions": [{"id": a["id"], "label": a["label"], "value": a.get("value", a.get("range"))} for a in inp.assump.values()],
        "caveats": [
            "Referral->diagnosis is unpublished in Finland; referral-anchored outputs depend on a labelled ASSUMPTION range (7-35 day median).",
            "County timing is inherited from its collaborative area (no county-level timing is published).",
            "42-day target: THL Ohjaus 21/2016 section 4.1, document marked outdated; no lung-specific limit.",
            "Scenario effect sizes come from other interventions/countries (effect_transfer ASSUMPTION); the zero-effect scenario is always shown.",
            "Diagnosis date equals treatment date for >=25% of surgical patients in 3 areas (Taulukko 4.1 Q1 = 0); short diagnosis-anchored times partly reflect recording.",
        ],
        "provenance": inp.provenance,
        "runtime_seconds": None,
    }
    res["runtime_seconds"] = round(time.time() - t0, 3)
    return res

def result_rows(res):
    rows = []
    for arm, block in (("baseline", res["baseline"]), ("scenario", res["scenario_arm"]), ("delta", res["delta_vs_baseline"])):
        for metric, s in block.items():
            rows.append({"county": res["job"]["county"], "county_name": res["county"]["name_en"], "area": res["county"]["area"],
                         "scenario": res["job"]["scenario"], "arm": arm, "metric": metric, **{k: s[k] for k in ("mean", "p2_5", "median", "p97_5")},
                         "seed": res["job"]["seed"], "n_runs": res["job"]["n_runs"], "chip": res["chip"]})
    return rows
