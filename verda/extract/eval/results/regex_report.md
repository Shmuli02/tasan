# Extraction eval — regex_baseline

- Corpus: `tasan-extract-synthetic-v1` (SYNTHETIC, seed 20261114)
- Documents: 600, patients: 120
- Predictions: `/workspace/junction-new/verda/extract/eval/results/regex_predictions.json`

## Document-level event extraction

### Exact date match

| type | precision | recall | F1 | support | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| referral_received | 0.988 | 0.952 | 0.969 | 580 | 552 | 7 | 28 |
| ct_done | 0.985 | 0.952 | 0.968 | 476 | 453 | 7 | 23 |
| biopsy_done | 0.959 | 0.943 | 0.951 | 351 | 331 | 14 | 20 |
| pathology_result | 0.955 | 0.918 | 0.936 | 256 | 235 | 11 | 21 |
| mdt_decision | 0.980 | 0.966 | 0.973 | 205 | 198 | 4 | 7 |
| treatment_decision | 0.953 | 0.910 | 0.931 | 155 | 141 | 7 | 14 |
| treatment_start | 1.000 | 0.951 | 0.975 | 82 | 78 | 0 | 4 |
| **micro** | 0.976 | 0.944 | 0.960 | 2105 | 1988 | 50 | 117 |
| **macro** | 0.974 | 0.942 | 0.958 |  |  |  |  |

### Date match within ±1 day

| type | precision | recall | F1 | support | TP | FP | FN |
|---|---:|---:|---:|---:|---:|---:|---:|
| referral_received | 1.000 | 0.964 | 0.982 | 580 | 559 | 0 | 21 |
| ct_done | 1.000 | 0.966 | 0.983 | 476 | 460 | 0 | 16 |
| biopsy_done | 0.994 | 0.977 | 0.986 | 351 | 343 | 2 | 8 |
| pathology_result | 0.996 | 0.957 | 0.976 | 256 | 245 | 1 | 11 |
| mdt_decision | 1.000 | 0.985 | 0.993 | 205 | 202 | 0 | 3 |
| treatment_decision | 0.993 | 0.948 | 0.970 | 155 | 147 | 1 | 8 |
| treatment_start | 1.000 | 0.951 | 0.975 | 82 | 78 | 0 | 4 |
| **micro** | 0.998 | 0.966 | 0.982 | 2105 | 2034 | 4 | 71 |
| **macro** | 0.998 | 0.964 | 0.981 |  |  |  |  |

## Patient-level day-28 alert

- Accuracy: **0.975** (117/120)
- Precision: 0.914, recall: 1.000, F1: 0.955
- Confusion: TP=32 FP=3 FN=0 TN=85
- day_count MAE (patients with referral on both sides): 0.009 (n=115)
- Rule: day_count >= 28 and no treatment_start; merge=latest_document_wins

_All labels are from the synthetic gold corpus. No real patient data._

## Where the rule floor breaks (same predictions)

These slices are why an open-weight model is still the hero, even though overall regex F1 is high on templated v1 text. After an optional later paraphrase pass, the regex floor is expected to drop further.

| slice | docs | exact P / R / F1 | ±1 day F1 |
|---|---:|---|---:|
| typo_heavy | 20 | 0.982 / 0.730 / **0.837** | 0.837 |
| relative_only | 25 | 0.898 / 0.880 / **0.889** | 0.980 |
| negation | 20 | 1.000 / 0.948 / 0.973 | 0.973 |
| cancelled | 16 | 0.964 / 0.946 / 0.955 | 0.991 |
| overall | 600 | 0.976 / 0.944 / 0.960 | 0.982 |

The three false-positive day-28 alerts are all missed `treatment_start` mentions (one typo-heavy, one negation, one early-treated), so the clock looks open when gold says treatment has begun.
