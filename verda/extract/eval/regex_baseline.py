#!/usr/bin/env python3
"""Rule/regex extractor — a non-LLM floor for Tasan Extract.

SYNTHETIC corpus only. Resolves relative dates against the document note_date.
Skips obvious negations/plans ('suunniteltu', 'peruttiin', 'not performed', ...).
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import EVENT_TYPES  # noqa: E402

# Keyword patterns per event type (FI / SV / EN). Order matters only within a type.
KEYWORDS = {
    "referral_received": [
        r"lähete\s+(?:saapunut|saapui|kirjattu|vastaanotettu)",
        r"esh-lähete",
        r"remiss(?:en)?\s+(?:inkommen|mottogs|registrerad)",
        r"specialistremiss",
        r"referral\s+(?:received|was\s+registered|registered)",
        r"specialist referral",
    ],
    "ct_done": [
        r"pet-tt\s+tehty",
        r"keuhko-tt\s+tehty",
        r"thoraxin\s+tt\s+tehty",
        r"tietokonetomografia",
        r"tt-tutkimus\s+tehty",
        r"\btt\s+tehty",
        r"pet-dt\s+utförd",
        r"dt\s+torax\s+utförd",
        r"datortomografi",
        r"pet-ct\s+performed",
        r"chest\s+ct\s+performed",
        r"ct\s+thorax\s+was\s+carried\s+out",
        r"ct\s+performed",
    ],
    "biopsy_done": [
        r"biopsiat\s+otettu",
        r"biopsia\s+tehty",
        r"ebus-bronkoskopia\s+suoritettu",
        r"bronkoskopia\s+ja\s+biopsia",
        r"bronkoskopia",
        r"biopsier\s+(?:tagna|togs)",
        r"bronkoskopi\s+och\s+biopsi",
        r"ebus-bronkoskopi",
        r"biopsies\s+(?:were\s+obtained|taken)",
        r"bronchoscopy\s+and\s+biopsy",
        r"ebus\s+bronchoscopy",
        r"bronchoscopy",
    ],
    "pathology_result": [
        r"pad-vastaus",
        r"patologin\s+lausunto",
        r"histologinen\s+vastaus",
        r"pad-svar",
        r"patologiskt\s+utlåtande",
        r"histologiskt\s+svar",
        r"pathology\s+result",
        r"histopathology\s+report",
        r"pad\s+result",
    ],
    "mdt_decision": [
        r"moniammatillinen\s+kokous",
        r"\bmdt\b",
        r"hoitokokous",
        r"multidisciplinär\s+konferens",
        r"\bmdk\b",
        r"vårdkonferens",
        r"multidisciplinary\s+(?:meeting|conference)",
        r"mdt\s+conference",
    ],
    "treatment_decision": [
        r"hoitopäätös",
        r"\blinjaus\b",
        r"päätettiin\s+",
        r"behandlingsbeslut",
        r"beslutades\s+",
        r"treatment\s+decision",
        r"it\s+was\s+decided",
    ],
    "treatment_start": [
        r"leikkaus\s*\([^)]*\)\s*tehty",
        r"leikkaus\s+tehty",
        r"kiilaresektio\s+suoritettu",
        r"sbrt-sädehoito\s+aloitettu",
        r"sädehoito\s+aloitettu",
        r"sytostaattihoito\s+aloitettu",
        r"solunsalpaajahoito\s+käynnistetty",
        r"hoito\s+aloitettu",
        r"operation\s*\([^)]*\)\s*utförd",
        r"kilresektion\s+utförd",
        r"sbrt-strålbehandling\s+påbörjad",
        r"strålbehandling\s+påbörjad",
        r"cytostatikabehandling\s+påbörjad",
        r"cellgiftsbehandling\s+startad",
        r"behandling\s+påbörjad",
        r"surgery\s*\([^)]*\)\s*performed",
        r"wedge\s+resection\s+performed",
        r"sbrt\s+radiotherapy\s+started",
        r"radiotherapy\s+started",
        r"chemotherapy\s+started",
        r"cytotoxic\s+therapy\s+commenced",
        r"treatment\s+started",
    ],
}

# If these appear in the same sentence as a keyword, do not emit an event.
NEGATION = re.compile(
    r"(?:"
    r"suunniteltu|ei\s+vielä\s+tehty|peruttiin|ei\s+tehty|ei\s+pidetty|"
    r"ei\s+ole\s+aloitettu|varattu\b|vasta\s+suunnitelmissa|siirtyy|"
    r"planerad|ännu\s+inte\s+utförd|ställdes\s+in|utfördes\s+inte|"
    r"har\s+inte\s+påbörjats|flyttas|"
    r"planned\s+for|not\s+yet\s+performed|was\s+cancelled|was\s+not\s+performed|"
    r"has\s+not\s+been\s+started|postponed|not\s+been\s+started|only\s+planned|"
    r"not\s+done|was\s+not\s+done"
    r")",
    re.IGNORECASE,
)

DATE_NUM = re.compile(
    r"(?P<iso>\b(\d{4})-(\d{2})-(\d{2})\b)"
    r"|(?P<dmy>\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b)"
    r"|(?P<dm>\b(\d{1,2})\.(\d{1,2})(?!\.\d)\b)"
    r"|(?P<slash>\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b)"
)

RELATIVE = [
    (re.compile(r"\beilen\b|\bigår\b|\byesterday\b", re.I), lambda n, _: n - timedelta(days=1)),
    (re.compile(r"\btoissapäivänä\b|\bi förrgår\b|\bthe day before yesterday\b", re.I), lambda n, _: n - timedelta(days=2)),
    (re.compile(r"\bkaksi viikkoa sitten\b|\bför två veckor sedan\b|\btwo weeks ago\b", re.I), lambda n, _: n - timedelta(days=14)),
    (re.compile(r"\bviikko sitten\b|\bför en vecka sedan\b|\ba week ago\b", re.I), lambda n, _: n - timedelta(days=7)),
]

WEEKDAY_FI = {"maanantaina": 0, "tiistaina": 1, "keskiviikkona": 2, "torstaina": 3, "perjantaina": 4, "lauantaina": 5, "sunnuntaina": 6}
WEEKDAY_SV = {"i måndags": 0, "i tisdags": 1, "i onsdags": 2, "i torsdags": 3, "i fredags": 4, "i lördags": 5, "i söndags": 6}
WEEKDAY_EN = {"last monday": 0, "last tuesday": 1, "last wednesday": 2, "last thursday": 3, "last friday": 4, "last saturday": 5, "last sunday": 6}

VIIME = re.compile(r"viime\s+(maanantaina|tiistaina|keskiviikkona|torstaina|perjantaina|lauantaina|sunnuntaina)", re.I)
SV_WD = re.compile(r"\b(i måndags|i tisdags|i onsdags|i torsdags|i fredags|i lördags|i söndags)\b", re.I)
EN_WD = re.compile(r"\b(last monday|last tuesday|last wednesday|last thursday|last friday|last saturday|last sunday)\b", re.I)

SENT_SPLIT = re.compile(r"(?<=[\.\!\?\n])\s+")


def _year(y: int, note: date) -> int:
    if y < 100:
        y += 2000
        # 2-digit years near century, still 20xx for this corpus
    return y


def parse_numeric_dates(text: str, note: date) -> list[tuple[int, int, date, str]]:
    found = []
    for m in DATE_NUM.finditer(text):
        try:
            if m.group("iso"):
                d = date(int(m.group(2)), int(m.group(3)), int(m.group(4)))
            elif m.group("dmy"):
                dd, mm, yy = int(m.group(6)), int(m.group(7)), _year(int(m.group(8)), note)
                d = date(yy, mm, dd)
            elif m.group("dm"):
                dd, mm = int(m.group(10)), int(m.group(11))
                d = date(note.year, mm, dd)
                # if that would be months in the future relative to the note, try previous year
                if d > note + timedelta(days=14):
                    d = date(note.year - 1, mm, dd)
            else:
                dd, mm = int(m.group(13)), int(m.group(14))
                yy = _year(int(m.group(15)), note) if m.group(15) else note.year
                d = date(yy, mm, dd)
                if not m.group(15) and d > note + timedelta(days=14):
                    d = date(note.year - 1, mm, dd)
        except ValueError:
            continue
        found.append((m.start(), m.end(), d, m.group(0)))
    return found


def last_weekday_before(note: date, weekday: int) -> date:
    delta = (note.weekday() - weekday) % 7
    if delta == 0:
        delta = 7
    return note - timedelta(days=delta)


def parse_relative_dates(text: str, note: date) -> list[tuple[int, int, date, str]]:
    found = []
    for rx, fn in RELATIVE:
        for m in rx.finditer(text):
            found.append((m.start(), m.end(), fn(note, m), m.group(0)))
    for m in VIIME.finditer(text):
        wd = WEEKDAY_FI[m.group(1).lower()]
        found.append((m.start(), m.end(), last_weekday_before(note, wd), m.group(0)))
    for m in SV_WD.finditer(text):
        wd = WEEKDAY_SV[m.group(1).lower()]
        found.append((m.start(), m.end(), last_weekday_before(note, wd), m.group(0)))
    for m in EN_WD.finditer(text):
        wd = WEEKDAY_EN[m.group(1).lower()]
        found.append((m.start(), m.end(), last_weekday_before(note, wd), m.group(0)))
    return found


def sentences(text: str) -> list[tuple[int, int, str]]:
    """Return (start, end, sentence) over the body."""
    out = []
    start = 0
    for m in re.finditer(r"\n|(?<=[\.!?])\s+", text):
        end = m.start()
        if end > start:
            out.append((start, end, text[start:end]))
        start = m.end()
    if start < len(text):
        out.append((start, len(text), text[start:]))
    return out


def extract_document(text: str, note: date) -> list[dict]:
    """Return predicted events for one document."""
    # Do not extract from the synthetic header block
    body = text
    if "=====" in text:
        # skip first banner block
        parts = text.split("=====", 2)
        if len(parts) == 3:
            offset = len(parts[0]) + len("=====") + len(parts[1]) + len("=====")
            body = text[offset:]
            prefix = text[:offset]
        else:
            prefix = ""
            offset = 0
    else:
        prefix = ""
        offset = 0

    dates = parse_numeric_dates(body, note) + parse_relative_dates(body, note)
    sents = sentences(body)
    events = []
    used_types = set()

    for typ, patterns in KEYWORDS.items():
        best = None
        for pat in patterns:
            for m in re.finditer(pat, body, flags=re.IGNORECASE):
                # sentence containing the match
                sent = next((s for s in sents if s[0] <= m.start() < s[1]), None)
                if sent is None:
                    continue
                s0, s1, stext = sent
                if NEGATION.search(stext):
                    continue
                # nearest date in the same sentence, else within 80 chars
                candidates = []
                for a, b, d, raw in dates:
                    if s0 <= a < s1:
                        candidates.append((0, abs((a + b) // 2 - m.start()), a, b, d, raw))
                    elif abs(a - m.start()) <= 80 or abs(b - m.end()) <= 80:
                        candidates.append((1, abs((a + b) // 2 - m.start()), a, b, d, raw))
                if not candidates:
                    continue
                candidates.sort()
                _tier, _dist, a, b, d, raw = candidates[0]
                span = stext.strip()
                rec = {
                    "type": typ,
                    "date": d.isoformat(),
                    "evidence_span": span,
                    "confidence": 0.45 if _tier == 0 else 0.3,
                    "matcher": pat,
                    "date_text": raw,
                }
                # prefer same-sentence + first (more specific) pattern
                score = (_tier, _dist)
                if best is None or score < best[0]:
                    best = (score, rec)
        if best and typ not in used_types:
            events.append(best[1])
            used_types.add(typ)
    return events


def extract_corpus(corpus_dir: Path) -> dict:
    docs_meta = [json.loads(l) for l in (corpus_dir / "documents.jsonl").read_text(encoding="utf-8").splitlines() if l]
    predictions = {"documents": {}, "system": "regex_baseline", "synthetic": True}
    for meta in docs_meta:
        text = (corpus_dir / meta["path"]).read_text(encoding="utf-8")
        note = date.fromisoformat(meta["note_date"])
        ev = extract_document(text, note)
        predictions["documents"][meta["document_id"]] = {
            "patient_id": meta["patient_id"],
            "note_date": meta["note_date"],
            "events": ev,
        }
    return predictions


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--corpus", type=Path, default=Path(__file__).resolve().parents[1] / "corpus" / "data")
    ap.add_argument("--out", type=Path, default=Path(__file__).resolve().parent / "results" / "regex_predictions.json")
    args = ap.parse_args()
    pred = extract_corpus(args.corpus)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(pred, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    n = sum(len(d["events"]) for d in pred["documents"].values())
    print(f"wrote {args.out} ({len(pred['documents'])} docs, {n} predicted events)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
