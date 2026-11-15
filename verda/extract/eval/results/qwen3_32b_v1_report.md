# qwen3-32b-awq on tasan-extract-synthetic-v1

SYNTHETIC corpus — no real patient data.

## all (600 docs, 120 patients)
- Exact micro P/R/F1: **0.955 / 0.953 / 0.954**
- ±1 day micro F1: **0.964**
- Day-28 alert accuracy 0.983 (P 1.000, R 0.938, F1 0.968)
- Per-type exact F1: referral_received=0.979, ct_done=0.973, biopsy_done=0.950, pathology_result=0.912, mdt_decision=0.942, treatment_decision=0.903, treatment_start=0.936

