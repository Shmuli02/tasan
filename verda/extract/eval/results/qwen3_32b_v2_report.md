# qwen3-32b-awq on tasan-extract-synthetic-v2

SYNTHETIC corpus — no real patient data.

## all (600 docs, 120 patients)
- Exact micro P/R/F1: **0.765 / 0.720 / 0.742**
- ±1 day micro F1: **0.763**
- Day-28 alert accuracy 0.958 (P 0.913, R 0.875, F1 0.894)
- Per-type exact F1: referral_received=0.761, ct_done=0.705, biopsy_done=0.759, pathology_result=0.721, mdt_decision=0.777, treatment_decision=0.773, treatment_start=0.652

## dev (199 docs, 40 patients)
- Exact micro P/R/F1: **0.765 / 0.730 / 0.747**
- ±1 day micro F1: **0.766**
- Day-28 alert accuracy 0.950 (P 1.000, R 0.778, F1 0.875)
- Per-type exact F1: referral_received=0.754, ct_done=0.722, biopsy_done=0.769, pathology_result=0.698, mdt_decision=0.746, treatment_decision=0.872, treatment_start=0.667

## test (401 docs, 80 patients)
- Exact micro P/R/F1: **0.765 / 0.715 / 0.739**
- ±1 day micro F1: **0.761**
- Day-28 alert accuracy 0.963 (P 0.875, R 0.933, F1 0.903)
- Per-type exact F1: referral_received=0.764, ct_done=0.697, biopsy_done=0.754, pathology_result=0.732, mdt_decision=0.791, treatment_decision=0.726, treatment_start=0.646

