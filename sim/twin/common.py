"""Shared paths, constants and numpy-only math (no scipy dependency)."""
from __future__ import annotations
import hashlib, json, os
from pathlib import Path
import numpy as np

SIM_DIR = Path(__file__).resolve().parent.parent
CONFIG_DIR = SIM_DIR / "config"
BUILD_DIR = Path(os.environ.get("TASAN_BUILD_DIR", SIM_DIR / "build"))
# Sourced data lives one level up (junction-new/data). Only build_targets reads it;
# the container ships the built targets/posterior so it needs no access to data/.
DATA_DIR = Path(os.environ.get("TASAN_DATA_DIR", SIM_DIR.parent / "data"))

CHIP = "MODEL OUTPUT · assumptions shown · not a forecast"
EVENTS = ["surgery", "radiotherapy", "drug", "palliative", "death"]  # + "none" (no first event by 6 mo)
ACTIVE = ["surgery", "radiotherapy", "drug"]
AREAS = ["YTA-ETELA", "YTA-ITA", "YTA-LANSI", "YTA-POHJOIS", "YTA-SISA"]

# Words that must never appear in any output (guardrail 2 of VERDA_PLAN).
FORBIDDEN = [
    "lives saved", "life saved", "lives_saved", "deaths averted", "deaths_averted", "death averted",
    "deaths prevented", "deaths_prevented", "lives gained", "life-years", "life years", "lyg", "qaly",
    "survival", "mortality", "curative_share_effect", "pelastettu", "pelastetut", "henkeä",
    "estetyt kuolemat", "kuolleisuus",
]

def load_json(p):
    with open(p, encoding="utf-8") as f:
        return json.load(f)

def dump_json(obj, p):
    p = Path(p); p.parent.mkdir(parents=True, exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        json.dump(obj, f, ensure_ascii=False, indent=1, sort_keys=False)

def sha256_file(p) -> str:
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def erf(x):
    """Abramowitz & Stegun 7.1.26, |error| < 1.5e-7."""
    x = np.asarray(x, dtype=float)
    s = np.sign(x); a = np.abs(x)
    t = 1.0 / (1.0 + 0.3275911 * a)
    y = 1.0 - (((((1.061405429 * t - 1.453152027) * t) + 1.421413741) * t - 0.284496736) * t + 0.254829592) * t * np.exp(-a * a)
    return s * y

def norm_cdf(z):
    return 0.5 * (1.0 + erf(np.asarray(z) / np.sqrt(2.0)))

def norm_ppf(p):
    """Acklam's inverse normal CDF (relative error ~1e-9)."""
    p = np.clip(np.asarray(p, dtype=float), 1e-15, 1 - 1e-15)
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02, 1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02, 6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00, -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    out = np.empty_like(p)
    lo, hi = p < 0.02425, p > 1 - 0.02425
    mid = ~(lo | hi)
    q = np.sqrt(-2 * np.log(p[lo]))
    out[lo] = (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p[mid] - 0.5; r = q * q
    out[mid] = (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)
    q = np.sqrt(-2 * np.log(1 - p[hi]))
    out[hi] = -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    return out

def lognorm_cdf(t, mu, sigma):
    t = np.maximum(np.asarray(t, dtype=float), 1e-12)
    return norm_cdf((np.log(t) - mu) / sigma)

def mix_cdf(t, pi0, mu, sigma, T):
    """CDF of time-to-event conditional on the event happening by T days:
    point mass pi0 at day 0 + (1-pi0) lognormal(mu, sigma), truncated at T."""
    LT = lognorm_cdf(T, mu, sigma)
    num = pi0 + (1 - pi0) * lognorm_cdf(np.minimum(t, T), mu, sigma)
    return num / (pi0 + (1 - pi0) * LT)

def mix_quantile(p, pi0, mu, sigma, T, iters=48):
    """Vectorised bisection quantile of mix_cdf; returns 0 where the point mass covers p."""
    pi0, mu, sigma = np.broadcast_arrays(np.asarray(pi0, float), np.asarray(mu, float), np.asarray(sigma, float))
    lo = np.zeros(pi0.shape); hi = np.full(pi0.shape, float(T))
    for _ in range(iters):
        m = 0.5 * (lo + hi)
        f = mix_cdf(m, pi0, mu, sigma, T)
        go_hi = f >= p
        hi = np.where(go_hi, m, hi); lo = np.where(go_hi, lo, m)
    q = 0.5 * (lo + hi)
    at0 = mix_cdf(0.0, pi0, mu, sigma, T) >= p
    return np.where(at0, 0.0, q)

def sample_mix(rng, n, pi0, mu, sigma, T):
    """Draw n times (days, continuous) from the truncated mixture by inverse CDF."""
    LT = float(lognorm_cdf(T, mu, sigma))
    w0 = pi0 / (pi0 + (1 - pi0) * LT)
    u0 = rng.random(n); u = rng.random(n)
    x = np.exp(mu + sigma * norm_ppf(np.clip(u * LT, 1e-15, 1 - 1e-15)))
    return np.where(u0 < w0, 0.0, np.minimum(x, T))
