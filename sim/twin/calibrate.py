"""ABC-rejection calibration of first-event timing per collaborative area (YTA).

For each area and each first-event type k (surgery, radiotherapy, drug, palliative, death):
  time from diagnosis to first event | type k  ~  pi0 * delta(0) + (1-pi0) * LogNormal(mu, sigma), truncated at 6 months.
The cumulative first-event curve is then share_k(month 6) * F_k(t)  (competing-risk decomposition).
share_k(month 6) is taken directly from Taulukko 4.5 (not fitted).

Accepted particles reproduce, simultaneously:
  * Taulukko 4.5 cumulative % at months 1..5 within tolerance.curve_abs_pp, and
  * Taulukko 4.1 Q1 / median / Q3 (active types only) within tolerance.quantile_abs_days.
The accepted set is the ABC posterior used by the microsimulation.
"""
from __future__ import annotations
import argparse, time
import numpy as np
from .common import (CONFIG_DIR, BUILD_DIR, AREAS, EVENTS, ACTIVE, load_json, dump_json, mix_cdf, mix_quantile)

def _prior(rng, n, cfg, kind):
    pr = cfg["prior"]
    lo, hi = pr["pi0"]["active" if kind in ACTIVE else "other"]
    pi0 = rng.uniform(lo, hi, n)
    m_lo, m_hi = pr["median_days"]
    mu = rng.uniform(np.log(m_lo), np.log(m_hi), n)
    sigma = rng.uniform(*pr["sigma"], n)
    return pi0, mu, sigma

def predict(pi0, mu, sigma, share6, cfg, with_quantiles):
    M, T = cfg["month_days"], cfg["horizon_days"]
    curve = np.stack([share6 * mix_cdf(m * M, pi0, mu, sigma, T) for m in range(1, 6)])  # 5 x N
    q = None
    if with_quantiles:
        q = np.stack([mix_quantile(p, pi0, mu, sigma, T) for p in (0.25, 0.5, 0.75)])   # 3 x N
    return curve, q

def calibrate_one(area_t, kind, cfg, rng, use_quantiles=True):
    tol = dict(cfg["tolerance"]); abc = cfg["abc"]
    if not use_quantiles:
        tol["curve_abs_pp"] = cfg["structural_sensitivity"]["curve_abs_pp"]
    obs_curve = np.array(area_t["cum_first_event_pct"][kind][1:6])
    share6 = area_t["cum_first_event_pct"][kind][6]
    qt = area_t["quantiles_days"].get(kind) if (kind in ACTIVE and use_quantiles) else None
    obs_q = np.array([qt["q1"], qt["median"], qt["q3"]]) if qt else None
    acc = []; draws = 0; n_acc_total = 0
    while draws < abc["max_draws"]:
        n = abc["batch"]; draws += n
        pi0, mu, sigma = _prior(rng, n, cfg, kind)
        curve, _ = predict(pi0, mu, sigma, share6, cfg, False)
        ce = np.abs(curve - obs_curve[:, None]).max(0)
        keep = ce <= tol["curve_abs_pp"]          # cheap pre-filter, then quantiles on survivors
        pi0, mu, sigma, ce = pi0[keep], mu[keep], sigma[keep], ce[keep]
        if obs_q is not None and len(pi0):
            _, q = predict(pi0, mu, sigma, share6, cfg, True)
            qe = np.abs(q - obs_q[:, None]).max(0)
            ok = qe <= tol["quantile_abs_days"]
            pi0, mu, sigma, ce, qe = pi0[ok], mu[ok], sigma[ok], ce[ok], qe[ok]
        else:
            qe = np.zeros(len(pi0))
        n_acc_total += len(pi0)
        for i in range(len(pi0)):
            acc.append((float(pi0[i]), float(mu[i]), float(sigma[i]), float(ce[i]), float(qe[i])))
        if len(acc) >= abc["target_particles"]:
            break
    acc = acc[: abc["target_particles"]]
    a = np.array(acc) if acc else np.zeros((0, 5))
    return {
        "kind": kind, "share_month6_pct": share6, "n_particles": len(acc), "n_draws": draws,
        "acceptance_rate": n_acc_total / draws, "n_accepted_total": n_acc_total,
        "particles": {"pi0": a[:, 0].round(6).tolist(), "mu": a[:, 1].round(6).tolist(), "sigma": a[:, 2].round(6).tolist()},
        "accepted_curve_err_pp_max": float(a[:, 3].max()) if len(a) else None,
        "accepted_quantile_err_days_max": float(a[:, 4].max()) if len(a) and obs_q is not None else None,
        "posterior_median_days": float(np.exp(np.median(a[:, 1]))) if len(a) else None,
        "posterior_pi0_median": float(np.median(a[:, 0])) if len(a) else None,
    }

def run(areas=None, use_quantiles=True, out_name="posterior.json"):
    cfg = load_json(CONFIG_DIR / "calibration.json")
    targets = load_json(BUILD_DIR / "targets.json")
    out = {"targets_used": "Taulukko 4.5 curves + Taulukko 4.1 quartiles" if use_quantiles else "Taulukko 4.5 curves only (structural sensitivity variant)",
           "method": "ABC rejection (uniform/log-uniform priors, accept iff all targets within pre-declared tolerance)",
           "config": cfg, "areas": {}}
    for ai, a in enumerate(areas or AREAS):
        out["areas"][a] = {}
        for ki, kind in enumerate(EVENTS):
            rng = np.random.default_rng([cfg["abc"]["seed"], ai, ki])
            t0 = time.time()
            r = calibrate_one(targets["areas"][a], kind, cfg, rng, use_quantiles)
            r["seconds"] = round(time.time() - t0, 2)
            out["areas"][a][kind] = r
            print(f"{a:12s} {kind:12s} particles={r['n_particles']:4d} draws={r['n_draws']:>8d} "
                  f"acc={r['acceptance_rate']:.2e} med={r['posterior_median_days']} pi0={r['posterior_pi0_median']} {r['seconds']}s", flush=True)
    dump_json(out, BUILD_DIR / out_name)
    return out

def calibrate_area(area, target_particles=None, seed=None):
    """One collaborative area as a self-contained job (for a batch fan-out); returns the posterior block."""
    cfg = load_json(CONFIG_DIR / "calibration.json")
    if target_particles:
        cfg["abc"]["target_particles"] = int(target_particles)
        cfg["abc"]["max_draws"] = max(cfg["abc"]["max_draws"], 20000 * int(target_particles))
    if seed is not None:
        cfg["abc"]["seed"] = int(seed)
    targets = load_json(BUILD_DIR / "targets.json")
    ai = AREAS.index(area); out = {"area": area, "config": cfg, "events": {}}
    for ki, kind in enumerate(EVENTS):
        out["events"][kind] = calibrate_one(targets["areas"][area], kind, cfg, np.random.default_rng([cfg["abc"]["seed"], ai, ki]))
    return out

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--area", action="append")
    ap.add_argument("--curve-only", action="store_true", help="sensitivity variant: ignore Taulukko 4.1 quartiles")
    a = ap.parse_args()
    run(a.area, use_quantiles=not a.curve_only, out_name="posterior_curve_only.json" if a.curve_only else "posterior.json")
