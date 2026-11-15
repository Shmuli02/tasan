#!/usr/bin/env python3
"""Careful, OCR-tolerant recovery of gold dates from note text + note_date."""
from __future__ import annotations

import re
from datetime import date, timedelta

FI_MONTH = {
    "tammikuuta": 1, "helmikuuta": 2, "maaliskuuta": 3, "huhtikuuta": 4,
    "toukokuuta": 5, "kesakuuta": 6, "kesäkuuta": 6, "heinakuuta": 7, "heinäkuuta": 7,
    "elokuuta": 8, "syyskuuta": 9, "lokakuuta": 10, "marraskuuta": 11, "joulukuuta": 12,
}
FI_GEN = {
    "tammikuun": 1, "helmikuun": 2, "maaliskuun": 3, "huhtikuun": 4,
    "toukokuun": 5, "kesakuun": 6, "kesäkuun": 6, "heinakuun": 7, "heinäkuun": 7,
    "elokuun": 8, "syyskuun": 9, "lokakuun": 10, "marraskuun": 11, "joulukuun": 12,
}
SV_MONTH = {
    "januari": 1, "februari": 2, "mars": 3, "april": 4, "maj": 5, "juni": 6,
    "juli": 7, "augusti": 8, "september": 9, "oktober": 10, "november": 11, "december": 12,
}
EN_MONTH = {
    "january": 1, "february": 2, "march": 3, "april": 4, "may": 5, "june": 6,
    "july": 7, "august": 8, "september": 9, "october": 10, "november": 11, "december": 12,
}
FI_WD = {"maanantaina": 0, "tiistaina": 1, "keskiviikkona": 2, "torstaina": 3, "perjantaina": 4, "lauantaina": 5, "sunnuntaina": 6}
SV_WD = {"måndagen": 0, "tisdagen": 1, "onsdagen": 2, "torsdagen": 3, "fredagen": 4, "lördagen": 5, "söndagen": 6}
EN_WD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6}


def soften(text: str) -> str:
    """Undo light OCR hyphenation only (kesä-kuuta, toissap-äivänä, p-å).

    Do not delete ordinary spaces — that glues 'vasta toissapäivänä' into one
    token and breaks word-boundary patterns such as viikolla N weekday (year).
    """
    t = text.replace("\u00ad", "")
    t = re.sub(r"(?<=\w)[-](?=\w)", "", t)
    return t


def last_weekday_before(note: date, weekday: int) -> date:
    d = note - timedelta(days=1)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def parse_dates(text: str, note: date) -> set[date]:
    t = soften(text)
    tl = t.lower()
    found: set[date] = set()

    def add(y, m, d):
        try:
            found.add(date(int(y), int(m), int(d)))
        except ValueError:
            pass

    for m in re.finditer(r"\b(\d{4})-(\d{2})-(\d{2})\b", t):
        add(m.group(1), m.group(2), m.group(3))
    for m in re.finditer(r"\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b", t):
        y = int(m.group(3))
        add(y if y > 100 else 2000 + y, m.group(2), m.group(1))
    for m in re.finditer(r"\b(\d{2})-(\d{2})-(\d{4})\b", t):
        add(m.group(3), m.group(2), m.group(1))
    months = {**FI_MONTH, **SV_MONTH, **EN_MONTH}
    mon_alt = "|".join(sorted(months, key=len, reverse=True))
    for m in re.finditer(rf"\b(\d{{1,2}})\.\s*({mon_alt})\s+(\d{{4}})\b", tl):
        add(m.group(3), months[m.group(2)], m.group(1))
    for m in re.finditer(rf"\bden\s+(\d{{1,2}})\s+({mon_alt})\s+(\d{{4}})\b", tl):
        add(m.group(3), months[m.group(2)], m.group(1))
    for m in re.finditer(rf"\b(\d{{1,2}})\s+({mon_alt})\s+(\d{{4}})\b", tl):
        add(m.group(3), months[m.group(2)], m.group(1))
    gen_alt = "|".join(sorted(FI_GEN, key=len, reverse=True))
    for m in re.finditer(rf"\b({gen_alt})\s+(\d{{1,2}})\.\s*päivänä\s+(\d{{4}})\b", tl):
        add(m.group(3), FI_GEN[m.group(1)], m.group(2))
    for m in re.finditer(rf"\b({mon_alt})\s+den\s+(\d{{1,2}})\s+år\s+(\d{{4}})\b", tl):
        add(m.group(3), months[m.group(1)], m.group(2))
    for m in re.finditer(rf"\b({mon_alt})\s+the\s+(\d{{1,2}}),\s+(\d{{4}})\b", tl):
        add(m.group(3), months[m.group(1)], m.group(2))
    for m in re.finditer(rf"\bviikolla\s+(\d{{1,2}})\s+({'|'.join(FI_WD)})\s*\((\d{{4}})\)", tl):
        try:
            found.add(date.fromisocalendar(int(m.group(3)), int(m.group(1)), FI_WD[m.group(2)] + 1))
        except ValueError:
            pass
    for m in re.finditer(rf"\bvecka\s+(\d{{1,2}})\s+(?:på\s+)?({'|'.join(SV_WD)})\s*\((\d{{4}})\)", tl):
        try:
            found.add(date.fromisocalendar(int(m.group(3)), int(m.group(1)), SV_WD[m.group(2)] + 1))
        except ValueError:
            pass
    for m in re.finditer(rf"\bin week\s+(\d{{1,2}})\s+(?:on\s+)?({'|'.join(EN_WD)})\s*\((\d{{4}})\)", tl):
        try:
            found.add(date.fromisocalendar(int(m.group(3)), int(m.group(1)), EN_WD[m.group(2)] + 1))
        except ValueError:
            pass
    if re.search(r"\b(eilen|igår|yesterday)\b", tl):
        found.add(note - timedelta(days=1))
    if re.search(r"\b(toissapäivänä|iförrgår|i förrgår|the day before yesterday)\b", tl):
        found.add(note - timedelta(days=2))
    for wd, i in FI_WD.items():
        if re.search(rf"\b{wd}\b", tl):
            found.add(last_weekday_before(note, i))
    for wd, i in SV_WD.items():
        if re.search(rf"\b(?:på\s+)?{wd}\b", tl):
            found.add(last_weekday_before(note, i))
    for wd, i in EN_WD.items():
        if re.search(rf"\b(?:on\s+)?{wd}\b", tl):
            found.add(last_weekday_before(note, i))
    return found


def gold_recoverable(text: str, note: date, gold_events: list[dict]) -> tuple[bool, list[str]]:
    missing = []
    parsed = parse_dates(text, note)
    # also accept ISO of gold appearing anywhere
    for ev in gold_events:
        d = date.fromisoformat(ev["date"])
        span = ev.get("evidence_span") or ""
        local = parse_dates(span, note) | parse_dates(text, note)
        if d not in local and ev["date"] not in text and ev["date"] not in soften(text):
            missing.append(f"{ev['type']}:{ev['date']}")
    return (not missing), missing
