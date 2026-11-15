#!/usr/bin/env bash
# Same steps as `make all` for machines without make. Usage: N_RUNS=2000 SEED=1 ./run_all.sh
set -euo pipefail
cd "$(dirname "$0")"
PY=${PY:-python3}; N_RUNS=${N_RUNS:-1000}; SEED=${SEED:-1}; WORKERS=${WORKERS:-8}
$PY -m twin.build_targets
$PY -m twin.calibrate
$PY -m twin.calibrate --curve-only
$PY -m twin.ppc
$PY -m twin.params
$PY -m twin.runner --n-runs "$N_RUNS" --seed "$SEED" --workers "$WORKERS" --out results
$PY -m twin.aggregate --results results
$PY -m twin.validate
