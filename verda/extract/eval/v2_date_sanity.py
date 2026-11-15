#!/usr/bin/env python3
"""Sanity-check corpus v2 dates: resolvable by a careful human? literal date coverage?

Does not retune the official regex. Reports why exact F1 was 0.000.
"""
from __future__ import annotations

import json
import re
import sys
from collections import Counter, defaultdict
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from eval.regex_baseline import KEYWORDS, extract_document, parse_numeric_dates, parse_relative_dates

ROOT = Path(__file__).resolve().parents[1] / "corpus" / "data_v2"
OUT = Path(__file__).resolve().parent / "results"

FI_MONTH = {
    "tammikuuta": 1, "helmikuuta": 2, "maaliskuuta": 3, "huhtikuuta": 4,
    "toukokuuta": 5, "kesakuuta": 6, "kesäkuuta": 6, "heinakuuta": 7, "heinäkuuta": 7,
    "elokuuta": 8, "syyskuuta": 9, "lokakuuta": 10, "marraskuuta": 11, "joulukuuta": 12,
}
FI_MONTH_GEN = {
    "tammikuun": 1, "helmikuun": 2, "maaliskuun": 3, "huhtikuun": 4,
    "toukokuun": 5, "kesäkuun": 6, "heinakuun": 7, "elokuun": 8,
    "syyskuun": 9, "lokakuun": 10, "marraskuun": 11, "joulukuun": 12,
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
SV_WD = {"måndagen": 0, "tisdagen": 1, "onsdagen": 2, "torsdagen": 3, "fredagen": 4, "lördagen": 5, "söndagen": 6,
         "på måndagen": 0, "på tisdagen": 1, "på onsdagen": 2, "på torsdagen": 3, "på fredagen": 4, "på lördagen": 5, "på söndagen": 6}
EN_WD = {"monday": 0, "tuesday": 1, "wednesday": 2, "thursday": 3, "friday": 4, "saturday": 5, "sunday": 6,
         "on monday": 0, "on tuesday": 1, "on wednesday": 2, "on thursday": 3, "on friday": 4, "on saturday": 5, "on sunday": 6}

# Also generator SV_WD_ON / EN forms — inspect one file if needed later.

NUM_ISO = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})\b")
NUM_DMY_DOT = re.compile(r"\b(\d{1,2})\.(\d{1,2})\.(\d{2,4})\b")
NUM_DMY_DASH = re.compile(r"\b(\d{2})-(\d{2})-(\d{4})\b")  # v2 unusual numeric
NUM_SLASH = re.compile(r"\b(\d{1,2})/(\d{1,2})(?:/(\d{2,4}))?\b")
FI_SPELLED = re.compile(r"\b(\d{1,2})\.\s*(" + "|".join(FI_MONTH) + r")\s+(\d{4})\b", re.I)
FI_GEN = re.compile(r"\b(" + "|".join(FI_MONTH_GEN) + r")\s+(\d{1,2})\.\s*päivänä\s+(\d{4})\b", re.I)
SV_SPELLED = re.compile(r"\bden\s+(\d{1,2})\s+(" + "|".join(SV_MONTH) + r")\s+(\d{4})\b", re.I)
SV_GEN = re.compile(r"\b(" + "|".join(SV_MONTH) + r")\s+den\s+(\d{1,2})\s+år\s+(\d{4})\b", re.I)
EN_SPELLED = re.compile(r"\b(\d{1,2})\s+(" + "|".join(EN_MONTH) + r")\s+(\d{4})\b", re.I)
EN_GEN = re.compile(r"\b(" + "|".join(EN_MONTH) + r")\s+the\s+(\d{1,2}),\s+(\d{4})\b", re.I)
FI_WEEK = re.compile(r"\bviikolla\s+(\d{1,2})\s+(" + "|".join(FI_WD) + r")\s*\((\d{4})\)", re.I)
SV_WEEK = re.compile(r"\bvecka\s+(\d{1,2})\s+(på\s+)?(" + "|".join(sorted(SV_WD, key=len, reverse=True)) + r")\s*\((\d{4})\)", re.I)
EN_WEEK = re.compile(r"\bin week\s+(\d{1,2})\s+(on\s+)?(" + "|".join(sorted(EN_WD, key=len, reverse=True)) + r")\s*\((\d{4})\)", re.I)
REL_YDAY = re.compile(r"\b(eilen|igår|yesterday)\b", re.I)
REL_2DAY = re.compile(r"\b(toissapäivänä|i förrgår|the day before yesterday)\b", re.I)
BARE_FI_WD = re.compile(r"\b(" + "|".join(FI_WD) + r")\b", re.I)

# Literal calendar dates (not relative-only)
LITERAL_ANY = re.compile(
    r"(" + "|".join([
        r"\b\d{4}-\d{2}-\d{2}\b",
        r"\b\d{1,2}\.\d{1,2}\.\d{2,4}\b",
        r"\b\d{2}-\d{2}-\d{4}\b",
        r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b",
        r"\b\d{1,2}\.\s*(?:" + "|".join(FI_MONTH) + r")\s+\d{4}\b",
        r"\b(?:" + "|".join(FI_MONTH_GEN) + r")\s+\d{1,2}\.\s*päivänä\s+\d{4}\b",
        r"\bden\s+\d{1,2}\s+(?:" + "|".join(SV_MONTH) + r")\s+\d{4}\b",
        r"\b(?:" + "|".join(SV_MONTH) + r")\s+den\s+\d{1,2}\s+år\s+\d{4}\b",
        r"\b\d{1,2}\s+(?:" + "|".join(EN_MONTH) + r")\s+\d{4}\b",
        r"\b(?:" + "|".join(EN_MONTH) + r")\s+the\s+\d{1,2},\s+\d{4}\b",
        r"\bviikolla\s+\d{1,2}\s+(?:" + "|".join(FI_WD) + r")\s*\(\d{4}\)",
        r"\bvecka\s+\d{1,2}\s+(?:på\s+)?(?:" + "|".join(SV_WD) + r")\s*\(\d{4}\)",
        r"\bin week\s+\d{1,2}\s+(?:on\s+)?(?:" + "|".join(EN_WD) + r")\s*\(\d{4}\)",
    ]) + r")",
    re.I,
)


def _from_iso_week(year: int, week: int, weekday: int) -> date:
    # ISO weekday 0=Mon
    return date.fromisocalendar(year, week, weekday + 1)


def last_weekday_before(note: date, weekday: int) -> date:
    d = note - timedelta(days=1)
    while d.weekday() != weekday:
        d -= timedelta(days=1)
    return d


def classify_and_parse(span: str, note: date) -> tuple[str, list[date]]:
    """Classify the gold evidence surface form and parse dates from it."""
    found: list[date] = []
    kinds: list[str] = []
    for rx, kind, fn in (
        (FI_SPELLED, "spelled_fi", lambda m: date(int(m.group(3)), FI_MONTH[m.group(2).lower()], int(m.group(1)))),
        (FI_GEN, "spelled_gen_fi", lambda m: date(int(m.group(3)), FI_MONTH_GEN[m.group(1).lower()], int(m.group(2)))),
        (SV_SPELLED, "spelled_sv", lambda m: date(int(m.group(3)), SV_MONTH[m.group(2).lower()], int(m.group(1)))),
        (SV_GEN, "spelled_gen_sv", lambda m: date(int(m.group(3)), SV_MONTH[m.group(1).lower()], int(m.group(2)))),
        (EN_SPELLED, "spelled_en", lambda m: date(int(m.group(3)), EN_MONTH[m.group(2).lower()], int(m.group(1)))),
        (EN_GEN, "spelled_gen_en", lambda m: date(int(m.group(3)), EN_MONTH[m.group(1).lower()], int(m.group(2)))),
        (FI_WEEK, "iso_week_fi", lambda m: _from_iso_week(int(m.group(3)), int(m.group(1)), FI_WD[m.group(2).lower()])),
        (NUM_ISO, "numeric_iso", lambda m: date(int(m.group(1)), int(m.group(2)), int(m.group(3)))),
        (NUM_DMY_DOT, "numeric_dmy_dot", lambda m: date(int(m.group(3)) if int(m.group(3)) > 100 else 2000 + int(m.group(3)), int(m.group(2)), int(m.group(1)))),
        (NUM_DMY_DASH, "numeric_dmy_dash", lambda m: date(int(m.group(3)), int(m.group(2)), int(m.group(1)))),
    ):
        for m in rx.finditer(span):
            try:
                found.append(fn(m))
                kinds.append(kind)
            except ValueError:
                kinds.append(kind + "_invalid")
    # weeks SV/EN
    for m in SV_WEEK.finditer(span):
        wd = (m.group(3) or "").lower()
        # map
        key = wd if wd in SV_WD else ("på " + wd if ("på " + wd) in SV_WD else wd)
        if key in SV_WD:
            try:
                found.append(_from_iso_week(int(m.group(4)), int(m.group(1)), SV_WD[key]))
                kinds.append("iso_week_sv")
            except ValueError:
                kinds.append("iso_week_sv_invalid")
    for m in EN_WEEK.finditer(span):
        wd = (m.group(3) or "").lower()
        key = wd if wd in EN_WD else ("on " + wd if ("on " + wd) in EN_WD else wd)
        if key in EN_WD:
            try:
                found.append(_from_iso_week(int(m.group(4)), int(m.group(1)), EN_WD[key]))
                kinds.append("iso_week_en")
            except ValueError:
                kinds.append("iso_week_en_invalid")
    if REL_YDAY.search(span):
        found.append(note - timedelta(days=1))
        kinds.append("relative_yesterday")
    if REL_2DAY.search(span):
        found.append(note - timedelta(days=2))
        kinds.append("relative_2days")
    # bare weekday only if nothing else more specific (except maybe two dates in written-vs-received)
    if not kinds:
        m = BARE_FI_WD.search(span)
        if m:
            found.append(last_weekday_before(note, FI_WD[m.group(1).lower()]))
            kinds.append("bare_weekday_fi")
    if not kinds:
        # last resort: v1 numeric/relative parsers
        for _a, _b, d, _s in parse_numeric_dates(span, note) + parse_relative_dates(span, note):
            found.append(d)
            kinds.append("v1_parser")
    if not kinds:
        return "unparsed", []
    # primary kind: prefer non-relative if mixed
    primary = kinds[0]
    if len(set(kinds)) > 1:
        primary = "mixed:" + ",".join(sorted(set(kinds)))
    return primary, found


def body_of(text: str) -> str:
    if "======\n" in text:
        return text.rsplit("======\n", 1)[-1]
    return text


def main() -> None:
    docs = []
    with open(ROOT / "documents.jsonl") as f:
        for line in f:
            rec = json.loads(line)
            rec["text"] = (ROOT / rec["path"]).read_text()
            docs.append(rec)
    gold = json.loads((ROOT / "gold.json").read_text())
    pats = gold["patients"]
    if isinstance(pats, dict):
        pats = list(pats.values())

    kind_c = Counter()
    recoverable = 0
    unrecoverable = []
    week_mismatch = []
    keyword_hits = Counter()
    n_events = 0
    notes_literal = 0
    notes_literal_body = 0
    notes_literal_gold = 0
    notes_numeric_v1 = 0
    gold_has_literal = 0
    split_rec = defaultdict(lambda: [0, 0])
    span_not_in_text = 0

    # v1 regex keyword presence (any typ) in body
    compiled = {typ: [re.compile(p, re.I) for p in pats] for typ, pats in KEYWORDS.items()}

    n_kw_sentence = 0
    n_kw_and_v1_date = 0

    for rec in docs:
        text = rec["text"]
        body = body_of(text)
        note = date.fromisoformat(rec["note_date"])
        lit = list(LITERAL_ANY.finditer(text))
        lit_body = list(LITERAL_ANY.finditer(body))
        if lit:
            notes_literal += 1
        if lit_body:
            notes_literal_body += 1
        if parse_numeric_dates(body, note):
            notes_numeric_v1 += 1
        gold_lit = False
        all_ok = True
        for ev in rec["events"]:
            n_events += 1
            span = ev["evidence_span"]
            if span not in text:
                span_not_in_text += 1
                all_ok = False
                unrecoverable.append((rec["document_id"], ev["type"], ev["date"], "span_missing", span[:80]))
                continue
            kind, parsed = classify_and_parse(span, note)
            kind_c[kind] += 1
            gold_d = date.fromisoformat(ev["date"])
            if any(d == gold_d for d in parsed):
                recoverable += 1
            else:
                all_ok = False
                unrecoverable.append((rec["document_id"], ev["type"], ev["date"], kind, parsed, span[:120]))
                if "week" in kind and parsed:
                    week_mismatch.append((ev["date"], [d.isoformat() for d in parsed], span))
            if re.search(
                r"\d{4}-\d{2}-\d{2}|\d{1,2}\.\d{1,2}\.\d{2,4}|\d{2}-\d{2}-\d{4}|"
                r"huhtikuuta|tammikuuta|helmikuuta|maaliskuuta|toukokuuta|kesäkuuta|heinakuuta|"
                r"elokuuta|syyskuuta|lokakuuta|marraskuuta|joulukuuta|"
                r"tammikuun|helmikuun|maaliskuun|huhtikuun|toukokuun|kesäkuun|heinakuun|"
                r"elokuun|syyskuun|lokakuun|marraskuun|joulukuun|"
                r"january|february|march|april|june|july|august|september|october|november|december|"
                r"januari|februari|april|juni|juli|augusti|oktober|"
                r"viikolla\s+\d|vecka\s+\d|in week\s+\d",
                span,
                re.I,
            ):
                gold_lit = True
                gold_has_literal += 1
        if gold_lit:
            notes_literal_gold += 1
        split = rec.get("split") or "na"
        split_rec[split][1] += len(rec["events"])
        # keyword overlap
        ev_types = {e["type"] for e in rec["events"]}
        for typ, rxs in compiled.items():
            if typ in ev_types and any(rx.search(body) for rx in rxs):
                keyword_hits[typ] += 1
                n_kw_sentence += 1

        # official regex
        pred = extract_document(text, note)

    # official already scored; recount quickly
    n_pred = 0
    n_tp = 0
    for rec in docs:
        note = date.fromisoformat(rec["note_date"])
        pred = extract_document(rec["text"], note)
        n_pred += len(pred)
        gold_set = {(e["type"], e["date"]) for e in rec["events"]}
        for e in pred:
            if (e["type"], e["date"]) in gold_set:
                n_tp += 1

    report = {
        "synthetic": True,
        "n_documents": len(docs),
        "n_events": n_events,
        "span_not_in_text": span_not_in_text,
        "gold_dates_recoverable_by_careful_parser": recoverable,
        "gold_dates_unrecoverable": len(unrecoverable),
        "recoverable_rate": round(recoverable / n_events, 4) if n_events else None,
        "notes_with_any_literal_date_string_full_file": notes_literal,
        "notes_with_any_literal_date_string_body": notes_literal_body,
        "notes_where_a_gold_span_has_literal_or_week_or_spelled_date": notes_literal_gold,
        "notes_with_v1_regex_numeric_date_in_body": notes_numeric_v1,
        "gold_events_with_literal_or_week_or_spelled": gold_has_literal,
        "surface_kinds": dict(kind_c.most_common()),
        "v1_keyword_hits_on_v2_body_by_type": dict(keyword_hits),
        "official_regex_predicted_events": n_pred,
        "official_regex_exact_tp": n_tp,
        "unrecoverable_examples": [
            {
                "document_id": u[0],
                "type": u[1],
                "gold": u[2],
                "kind": u[3],
                "parsed": [d.isoformat() if hasattr(d, "isoformat") else str(d) for d in (u[4] if len(u) > 5 else [])] if not isinstance(u[4], str) else u[4],
                "span": u[-1],
            }
            for u in unrecoverable[:25]
        ],
    }
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "v2_date_sanity.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")

    def pct(n, d):
        return f"{n}/{d} ({100*n/d:.1f}%)" if d else "n/a"

    md = []
    md.append("# v2 date sanity check (not a regex retune)\n")
    md.append("The official v1 regex is left unchanged. This file asks whether v2 gold is fair:\n")
    md.append(f"- Documents: {len(docs)}; gold events: {n_events}")
    md.append(f"- Evidence span found verbatim in the corpus file: {pct(n_events-span_not_in_text, n_events)}")
    md.append(f"- Gold dates a careful human-equivalent parser can recover from (evidence span + note_date): **{pct(recoverable, n_events)}**")
    md.append(f"- Official v1 regex predicted events on v2: **{n_pred}** (exact TP {n_tp}) — this is why exact F1 was 0.000\n")
    md.append("## Literal date strings\n")
    md.append("A “literal date string” here means an explicit calendar form a reader can resolve without only a relative word (`eilen` / `yesterday`). That includes ISO and dotted numeric dates, the v2 `dd-mm-yyyy` form, spelled month names (e.g. `14. huhtikuuta 2026`), and ISO-week forms (`viikolla 34 maanantaina (2026)`), which uniquely identify a day.\n")
    md.append(f"- Notes whose **body** contains at least one literal date string (including historical distractors): **{pct(notes_literal_body, len(docs))}**")
    md.append(f"- Notes whose gold evidence spans contain a literal / spelled / week date (not only `eilen` etc.): **{pct(notes_literal_gold, len(docs))}**")
    md.append(f"- Notes in which the **v1 regex numeric parser** finds any date in the body (ISO, `d.m.yyyy`, `d/m/yyyy` — **not** `dd-mm-yyyy`, spelled months, or ISO weeks): **{pct(notes_numeric_v1, len(docs))}**\n")
    md.append("## Gold surface forms (per event)\n")
    for k, n in kind_c.most_common():
        md.append(f"- `{k}`: {n}")
    md.append("\n## Why regex F1 is 0.000 (two stacked effects, not a broken gold file)\n")
    md.append("1. **Held-out keywords (intended).** v2 sentences were written to avoid the v1 keyword list (`ESH-lähete vastaanotettu`, `Thoraxin TT tehty`, …). A few v2 templates still share a verb (`Lähete saapui …`) but OCR splits (`Lä-hete`) often break even those. Keyword hits on v2 bodies, by type: " + ", ".join(f"{k}={v}" for k, v in keyword_hits.items()) + f" (out of {n_events} events).")
    md.append("2. **Date-format mismatch (also real, and harsher than a fair “messy clinical Finnish” test).** v2’s “numeric” style is `14-04-2026` (dashes, day-first). The v1 regex only accepts `2026-04-14`, `14.4.2026`, `14/4/2026`, or `14.4`. It does **not** parse spelled months or `viikolla 34 maanantaina (2026)`. Those week forms *are* uniquely resolvable with a calendar; a careful human can do it. So 0.000 is not “the gold dates are hidden”, but it is also not only lexical difficulty — a large share of gold dates are in formats the official parser was never taught.\n")
    if unrecoverable:
        md.append(f"## Unrecoverable examples ({len(unrecoverable)})\n")
        for u in unrecoverable[:15]:
            md.append(f"- `{u[0]}` {u[1]} gold={u[2]} kind={u[3]} span={u[-1]!r}")
    else:
        md.append("No gold event failed the careful parser: every gold date is recoverable from the note text plus `note_date`.\n")
    (OUT / "v2_date_sanity.md").write_text("\n".join(md) + "\n")
    print("\n".join(md))
    print("wrote", OUT / "v2_date_sanity.md")


if __name__ == "__main__":
    main()
