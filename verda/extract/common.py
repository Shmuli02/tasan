"""Shared constants for Tasan Extract. All data is SYNTHETIC."""

EVENT_TYPES = [
    "referral_received",
    "ct_done",
    "biopsy_done",
    "pathology_result",
    "mdt_decision",
    "treatment_decision",
    "treatment_start",
]

ALERT_DAY = 28
SEED_DEFAULT = 20261114
CORPUS_ID = "tasan-extract-synthetic-v1"

SYNTHETIC_BANNER = (
    "SYNTHETIC DOCUMENT — NOT A REAL PATIENT — Tasan Extract eval corpus. "
    "No real personal data. All names, dates and findings are invented."
)

DOC_TYPES = [
    "referral_letter",
    "ct_report",
    "biopsy_note",
    "pathology_report",
    "mdt_minutes",
    "oncology_note",
    "discharge_summary",
]

LANGS = ("fi", "sv", "en")
