PY ?= python3
N_RUNS ?= 1000
SEED ?= 1
WORKERS ?= 8
IMAGE ?= tasan-twin:0.1.0

.PHONY: all targets calibrate ppc params run aggregate validate image image-test dryrun clean
all: targets calibrate ppc params run aggregate validate

targets:   ; $(PY) -m twin.build_targets
calibrate: ; $(PY) -m twin.calibrate && $(PY) -m twin.calibrate --curve-only
ppc:       ; $(PY) -m twin.ppc
params:    ; $(PY) -m twin.params
run:       ; $(PY) -m twin.runner --n-runs $(N_RUNS) --seed $(SEED) --workers $(WORKERS) --out results
aggregate: ; $(PY) -m twin.aggregate --results results
validate:  ; $(PY) -m twin.validate
dryrun:    ; $(PY) -m twin.verda_dryrun
image:     ; docker build -t $(IMAGE) .
image-test:
	docker run --rm -e TASAN_COUNTY=21 -e TASAN_SCENARIO=zero_effect -e TASAN_N_RUNS=200 $(IMAGE) python -m twin.cli run
clean:     ; rm -rf results/* build/validation_report.json
