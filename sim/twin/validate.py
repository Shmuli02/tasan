"""Scripted validation gate (VERDA_PLAN go/no-go).  `python -m twin.validate` -> exit 0 only if every check passes.

Checks
  1 inputs        sourced CSVs present; targets rebuilt from them; month-6 shares sum to 100 +- 0.3
  2 calibration   posterior predictive fit per area within pre-declared tolerance (curve <= 1.5 pp, quartiles <= 7 d)
  3 zero_effect   zero-effect scenario reproduces baseline for all 22 counties (tolerance 0.1 pp; expected exactly 0)
  4 forbidden     no output contains 'lives saved', 'deaths averted', survival/mortality wording etc.
  5 reproducible  same seed -> byte-identical results (runtime excluded); different seed -> different results
  6 provenance    every model input has a source or an ASSUMPTION/DESIGN label
  7 cli           container entrypoint (CLI with env vars) runs one job and exits 0
  8 server        Verda batch-job HTTP contract: GET /health 200, one POST /run -> 200 JSON, process exits 0
  9 docker        image builds and runs one job (SKIPPED with reason if no container runtime is installed)
"""
from __future__ import annotations
import json, os, shutil, socket, subprocess, sys, tempfile, time, urllib.request
from pathlib import Path
from .common import SIM_DIR, BUILD_DIR, CONFIG_DIR, DATA_DIR, FORBIDDEN, load_json, dump_json
from . import build_targets, ppc, params
from .model import Inputs, run_job, METRICS, DX_ONLY

RESULTS = []

def check(name, ok, detail, skipped=False):
    RESULTS.append({"check": name, "status": "SKIPPED" if skipped else ("PASS" if ok else "FAIL"), "detail": detail})
    print(f"[{'SKIP' if skipped else ('PASS' if ok else 'FAIL')}] {name}: {json.dumps(detail, ensure_ascii=False)[:600]}", flush=True)

def c_inputs():
    files = ["csv/lung_report2024_first_event_cumulative_by_yta.csv", "csv/lung_derived_first_active_treatment_by_month_yta.csv",
             "csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv", "csv/lung_report2024_treatment_6m_by_yta.csv",
             "csv/lung_report2026_treatment_by_wsc.csv", "TREATMENT_TARGETS.md", "SOURCES.md"]
    missing = [f for f in files if not (DATA_DIR / f).exists()]
    t = build_targets.build()
    sums = {a: v["month6_sum_pct"] for a, v in t["areas"].items()}
    ok = not missing and len(t["counties"]) == 22 and all(abs(s - 100) <= 0.3 for s in sums.values())
    check("1 inputs", ok, {"missing": missing, "n_counties": len(t["counties"]), "month6_sum_pct": sums})

def c_calibration():
    r = ppc.run()
    det = {a: {"curve_max_err_pp": v["worst_curve_err_pp"], "quartile_max_err_days": v["worst_quantile_err_days"],
               "derived_first_active_months_inside_ci": f"{v['derived_first_active']['months_inside_ci']}/6", "pass": v["pass"]}
           for a, v in r["areas"].items()}
    check("2 calibration", r["pass"], {"tolerance": {k: r["tolerance"][k] for k in ("curve_abs_pp", "quantile_abs_days")}, "areas": det})

def c_zero(inp, n_runs):
    worst = 0.0; worst_cross = 0.0; bad = []
    for code in sorted(inp.counties):
        z = run_job(code, "zero_effect", 11, n_runs, inp); b = run_job(code, "baseline", 11, n_runs, inp)
        for m in METRICS:
            if m in DX_ONLY:
                continue
            for stat in ("mean", "p2_5", "median", "p97_5"):
                d = z["delta_vs_baseline"][m][stat]
                worst = max(worst, abs(d or 0))
                x, y = z["scenario_arm"][m][stat], b["baseline"][m][stat]
                if x is not None and y is not None:
                    worst_cross = max(worst_cross, abs(x - y))
        if worst > 0.1 or worst_cross > 0.1:
            bad.append(code)
    check("3 zero_effect", not bad, {"counties": len(inp.counties), "n_runs": n_runs, "tolerance_pp": 0.1,
                                      "max_abs_paired_delta": worst, "max_abs_diff_vs_separate_baseline_job": worst_cross, "failing": bad})

def _scan(paths):
    hits = []
    for p in paths:
        txt = Path(p).read_text(encoding="utf-8", errors="ignore").lower()
        for w in FORBIDDEN:
            if w in txt:
                hits.append((str(p), w))
    return hits

def c_forbidden(tmp):
    out = Path(tmp) / "fb"
    subprocess.run([sys.executable, "-m", "twin.runner", "--n-runs", "50", "--out", str(out), "--workers", "4"], check=True, cwd=SIM_DIR, capture_output=True)
    subprocess.run([sys.executable, "-m", "twin.aggregate", "--results", str(out)], check=True, cwd=SIM_DIR, capture_output=True)
    files = list(out.rglob("*.json")) + list(out.rglob("*.csv"))
    res_dir = SIM_DIR / "results"
    files += list(res_dir.rglob("*.json")) + list(res_dir.rglob("*.csv"))
    hits = _scan(files)
    # also the forbidden list must not be emptied by accident
    check("4 forbidden", not hits and len(FORBIDDEN) >= 10, {"files_scanned": len(files), "phrases": len(FORBIDDEN), "hits": hits[:10]})

def c_repro(inp):
    def strip(r):
        r = dict(r); r.pop("runtime_seconds"); return json.dumps(r, sort_keys=True)
    a = strip(run_job("21", "high", 42, 300, inp)); b = strip(run_job("21", "high", 42, 300, inp))
    c = strip(run_job("21", "high", 43, 300, inp))
    check("5 reproducible", a == b and a != c, {"same_seed_identical": a == b, "different_seed_differs": a != c,
                                                "sha_seed42": __import__("hashlib").sha256(a.encode()).hexdigest()[:16]})

def c_provenance():
    reg = params.build(); P = reg["parameters"]
    problems = []
    for p in P:
        if p["kind"] not in ("sourced", "calibrated", "derived", "assumption", "design"):
            problems.append((p["id"], "bad kind"))
        if not p.get("source"):
            problems.append((p["id"], "no source"))
        if p["kind"] in ("assumption", "design") and not (p.get("label") or "").upper().startswith(("ASSUMPTION", "DESIGN")):
            problems.append((p["id"], "assumption without label"))
    groups = {p["group"] for p in P}
    missing = [g for g in reg["model_inputs"] if g not in groups]
    # every scenario with an effect must cite a study or carry ASSUMPTION
    for s in load_json(CONFIG_DIR / "scenarios.json")["scenarios"]:
        if s.get("intervention") and not s.get("source"):
            problems.append((s["id"], "scenario without source"))
    kinds = {}
    for p in P:
        kinds[p["kind"]] = kinds.get(p["kind"], 0) + 1
    check("6 provenance", not problems and not missing, {"n_parameters": len(P), "by_kind": kinds, "missing_model_inputs": missing, "problems": problems[:10]})

def c_cli(tmp):
    env = dict(os.environ, TASAN_COUNTY="21", TASAN_SCENARIO="zero_effect", TASAN_SEED="3", TASAN_N_RUNS="100", TASAN_OUT=str(Path(tmp) / "cli"))
    p = subprocess.run([sys.executable, "-m", "twin.cli", "run"], cwd=SIM_DIR, env=env, capture_output=True, text=True)
    f = Path(tmp) / "cli" / "zero_effect" / "21.json"
    ok = p.returncode == 0 and f.exists() and (f.with_suffix(".csv")).exists()
    check("7 cli", ok, {"exit_code": p.returncode, "stdout": p.stdout.strip()[-250:], "stderr": p.stderr.strip()[-300:]})

def c_server(tmp):
    s = socket.socket(); s.bind(("127.0.0.1", 0)); port = s.getsockname()[1]; s.close()
    env = dict(os.environ, PORT=str(port), TASAN_OUT=str(Path(tmp) / "srv"))
    proc = subprocess.Popen([sys.executable, "-m", "twin.server"], cwd=SIM_DIR, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    try:
        h = None
        for _ in range(50):
            try:
                h = urllib.request.urlopen(f"http://127.0.0.1:{port}/health", timeout=1).status; break
            except Exception:
                time.sleep(0.1)
        req = urllib.request.Request(f"http://127.0.0.1:{port}/run?county=14&scenario=low&seed=5&n_runs=100", method="POST", data=b"")
        body = json.loads(urllib.request.urlopen(req, timeout=60).read())
        rc = proc.wait(timeout=20)
        ok = h == 200 and body.get("job", {}).get("county") == "14" and rc == 0
        check("8 server", ok, {"health": h, "job": body.get("job"), "process_exit_code": rc})
    except Exception as e:
        proc.kill(); check("8 server", False, {"error": str(e)})

def c_docker():
    rt = shutil.which("docker") or shutil.which("podman")
    if not rt:
        check("9 docker", True, {"reason": "no docker/podman binary on this machine; container entrypoints validated directly via checks 7 and 8"}, skipped=True); return
    tag = "tasan-twin:validate"
    b = subprocess.run([rt, "build", "-t", tag, "."], cwd=SIM_DIR, capture_output=True, text=True)
    if b.returncode != 0:
        check("9 docker", False, {"build_stderr": b.stderr[-500:]}); return
    r = subprocess.run([rt, "run", "--rm", "-e", "TASAN_COUNTY=21", "-e", "TASAN_SCENARIO=baseline", "-e", "TASAN_N_RUNS=100", tag,
                        "python", "-m", "twin.cli", "run"], capture_output=True, text=True)
    check("9 docker", r.returncode == 0, {"runtime": rt, "stdout": r.stdout[-300:], "stderr": r.stderr[-300:]})

def main():
    t0 = time.time()
    with tempfile.TemporaryDirectory() as tmp:
        c_inputs(); c_calibration()
        inp = Inputs()
        c_zero(inp, int(os.environ.get("TASAN_VALIDATE_RUNS", "300")))
        c_forbidden(tmp); c_repro(inp); c_provenance(); c_cli(tmp); c_server(tmp); c_docker()
    ok = all(r["status"] != "FAIL" for r in RESULTS)
    rep = {"overall": "PASS" if ok else "FAIL", "seconds": round(time.time() - t0, 1),
           "checked_at_local": time.strftime("%Y-%m-%d %H:%M %Z"), "checks": RESULTS, "provenance": Inputs().provenance}
    dump_json(rep, BUILD_DIR / "validation_report.json")
    print(f"\nOVERALL: {rep['overall']} ({rep['seconds']}s) -> build/validation_report.json")
    return 0 if ok else 1

if __name__ == "__main__":
    sys.exit(main())
