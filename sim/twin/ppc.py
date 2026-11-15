"""Posterior predictive check: simulate large area cohorts with the SAME sampler as the job model
and compare with the published registry targets (Taulukko 4.5 curves, 4.1 quartiles, derived first-active curve)."""
from __future__ import annotations
import numpy as np
from .common import BUILD_DIR, AREAS, ACTIVE, EVENTS, dump_json, sample_mix
from .model import Inputs, CATS

def area_ppc(inp: Inputs, area, n, seed):
    rng = np.random.default_rng([seed, AREAS.index(area)])
    at = inp.targets["areas"][area]; post = inp.posterior["areas"][area]
    M, T = inp.cal["month_days"], inp.cal["horizon_days"]
    tol = inp.cal["tolerance"]
    share = np.array([at["cum_first_event_pct"][k][6] for k in CATS], float); share /= share.sum()
    counts = rng.multinomial(n, share)
    out = {"n_patients": n, "events": {}}
    times = {}
    for k, m in zip(CATS, counts):
        if k == "none":
            continue
        p = post[k]["particles"]; P = len(p["pi0"])
        j = rng.integers(P, size=m)  # integrate over posterior: one particle per patient
        t = np.empty(m)
        for jj in np.unique(j):
            sel = j == jj
            t[sel] = sample_mix(rng, int(sel.sum()), p["pi0"][jj], p["mu"][jj], p["sigma"][jj], T)
        times[k] = np.rint(t)
    worst_c, worst_q = 0.0, 0.0
    for k in EVENTS:
        sim_curve = [100.0 * np.sum(times[k] <= mth * M) / n for mth in range(0, 7)]
        obs = at["cum_first_event_pct"][k]
        err = [abs(sim_curve[mth] - obs[mth]) for mth in range(1, 7)]
        e = {"sim_curve_pct": [round(x, 2) for x in sim_curve], "obs_curve_pct": obs,
             "curve_max_abs_err_pp": round(max(err), 3), "curve_rmse_pp": round(float(np.sqrt(np.mean(np.square(err)))), 3)}
        worst_c = max(worst_c, max(err))
        if k in ACTIVE:
            q = at["quantiles_days"][k]
            sq = np.percentile(times[k], [25, 50, 75])
            qe = [abs(sq[0] - q["q1"]), abs(sq[1] - q["median"]), abs(sq[2] - q["q3"])]
            e.update({"sim_q1_median_q3": [float(x) for x in sq], "obs_q1_median_q3": [q["q1"], q["median"], q["q3"]],
                      "quantile_max_abs_err_days": round(float(max(qe)), 2)})
            worst_q = max(worst_q, max(qe))
        out["events"][k] = e
    act = np.concatenate([times[k] for k in ACTIVE])
    der = at["derived_first_active_pct"]
    inside = []
    dcmp = {}
    for mth in range(1, 7):
        v = 100.0 * np.sum(act <= mth * M) / n
        d = der[str(mth)] if str(mth) in der else der[mth]
        ok = d["ci95_low"] - 0.05 <= v <= d["ci95_high"] + 0.05
        inside.append(ok); dcmp[mth] = {"sim": round(v, 2), "obs": d["value"], "ci95": [d["ci95_low"], d["ci95_high"]], "inside_ci": bool(ok)}
    out["derived_first_active"] = {"by_month": dcmp, "months_inside_ci": int(sum(inside))}
    out["worst_curve_err_pp"] = round(worst_c, 3); out["worst_quantile_err_days"] = round(worst_q, 2)
    out["pass_curve"] = bool(worst_c <= tol["curve_abs_pp"])
    out["pass_quantiles"] = bool(worst_q <= tol["quantile_abs_days"])
    out["pass"] = out["pass_curve"] and out["pass_quantiles"]
    return out

def pct_le42_dx_area(inp, posterior, area, n, seed, target=42):
    """Area-level % of actively treated patients starting <=42 d after diagnosis, integrating over a posterior."""
    rng = np.random.default_rng([seed, 99, AREAS.index(area)])
    at = inp.targets["areas"][area]; T = inp.cal["horizon_days"]
    w = np.array([at["cum_first_event_pct"][k][6] for k in ACTIVE]); w = w / w.sum()
    ts = []
    for k, m in zip(ACTIVE, rng.multinomial(n, w)):
        p = posterior["areas"][area][k]["particles"]; j = rng.integers(len(p["pi0"]), size=m)
        for jj in np.unique(j):
            c = int((j == jj).sum())
            ts.append(np.rint(sample_mix(rng, c, p["pi0"][jj], p["mu"][jj], p["sigma"][jj], T)))
    t = np.concatenate(ts)
    return 100.0 * float(np.mean(t <= target))

def run(inp=None):
    inp = inp or Inputs()
    cfg = inp.cal["posterior_predictive"]
    res = {"tolerance": inp.cal["tolerance"], "areas": {}}
    for a in AREAS:
        res["areas"][a] = area_ppc(inp, a, cfg["n_patients_per_area"], cfg["seed"])
    res["pass"] = all(v["pass"] for v in res["areas"].values())
    alt_p = BUILD_DIR / "posterior_curve_only.json"
    if alt_p.exists():
        from .common import load_json
        alt = load_json(alt_p); ss = {}
        for a in AREAS:
            j = pct_le42_dx_area(inp, inp.posterior, a, 100000, cfg["seed"])
            c = pct_le42_dx_area(inp, alt, a, 100000, cfg["seed"])
            ss[a] = {"joint_fit_pct_le42_from_dx": round(j, 2), "curve_only_fit_pct_le42_from_dx": round(c, 2), "difference_pp": round(c - j, 2)}
        res["structural_sensitivity_4_1_vs_4_5"] = ss
    dump_json(res, BUILD_DIR / "calibration_report.json")
    return res

if __name__ == "__main__":
    r = run()
    for a, v in r["areas"].items():
        print(f"{a:12s} pass={v['pass']} worst_curve={v['worst_curve_err_pp']}pp worst_q={v['worst_quantile_err_days']}d derivedCI={v['derived_first_active']['months_inside_ci']}/6")
        for k, e in v["events"].items():
            print(f"   {k:12s} curve_max={e['curve_max_abs_err_pp']} rmse={e['curve_rmse_pp']}", e.get("sim_q1_median_q3"), e.get("obs_q1_median_q3"))
