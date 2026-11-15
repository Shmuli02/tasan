#!/usr/bin/env python3
"""Tasan Extract corpus v2 — HARD / held-out phrasing families.

SYNTHETIC only. Templates are deliberately disjoint from the v1 regex
keyword set. Do not tune the regex on the test split.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import ALERT_DAY, EVENT_TYPES, SEED_DEFAULT, SYNTHETIC_BANNER  # noqa: E402
import generate as v1  # noqa: E402

CORPUS_ID = "tasan-extract-synthetic-v2"
SEED_DEFAULT_V2 = 20261142

FI_MONTH_PART = [
    "tammikuuta", "helmikuuta", "maaliskuuta", "huhtikuuta", "toukokuuta",
    "kesäkuuta", "heinäkuuta", "elokuuta", "syyskuuta", "lokakuuta",
    "marraskuuta", "joulukuuta",
]
FI_MONTH_GEN = [
    "tammikuun", "helmikuun", "maaliskuun", "huhtikuun", "toukokuun",
    "kesäkuun", "heinäkuun", "elokuun", "syyskuun", "lokakuun",
    "marraskuun", "joulukuun",
]
SV_MONTH = [
    "januari", "februari", "mars", "april", "maj", "juni",
    "juli", "augusti", "september", "oktober", "november", "december",
]
EN_MONTH = [
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December",
]
FI_WD = ["maanantaina", "tiistaina", "keskiviikkona", "torstaina", "perjantaina", "lauantaina", "sunnuntaina"]
SV_WD_ON = ["på måndagen", "på tisdagen", "på onsdagen", "på torsdagen", "på fredagen", "på lördagen", "på söndagen"]
EN_WD = ["on Monday", "on Tuesday", "on Wednesday", "on Thursday", "on Friday", "on Saturday", "on Sunday"]


def iso(d: date) -> str:
    return d.isoformat()


def format_date_v2(event: date, note: date, lang: str, rng: random.Random, prefer_relative: bool) -> str:
    """Resolvable date forms the v1 regex was not written for."""
    delta = (note - event).days
    rel = None
    if delta == 1:
        rel = {"fi": "eilen", "sv": "igår", "en": "yesterday"}[lang]
    elif delta == 2:
        rel = {"fi": "toissapäivänä", "sv": "i förrgår", "en": "the day before yesterday"}[lang]
    elif event == v1.last_weekday_before(note, event.weekday()) and event.weekday() != note.weekday():
        if lang == "fi":
            rel = FI_WD[event.weekday()]  # "tiistaina" (not "viime tiistaina" — also used, but bare weekday relative to note)
        elif lang == "sv":
            rel = SV_WD_ON[event.weekday()]
        else:
            rel = EN_WD[event.weekday()]

    if rel and (prefer_relative or rng.random() < 0.22):
        return rel

    iso_week = event.isocalendar()
    styles = ["spelled", "spelled", "spelled_gen", "week_wd", "numeric"]
    if prefer_relative:
        styles = ["spelled", "spelled_gen", "week_wd", "spelled"]
    style = rng.choice(styles)
    if style == "spelled":
        if lang == "fi":
            return f"{event.day}. {FI_MONTH_PART[event.month - 1]} {event.year}"
        if lang == "sv":
            return f"den {event.day} {SV_MONTH[event.month - 1]} {event.year}"
        return f"{event.day} {EN_MONTH[event.month - 1]} {event.year}"
    if style == "spelled_gen":
        if lang == "fi":
            return f"{FI_MONTH_GEN[event.month - 1]} {event.day}. päivänä {event.year}"
        if lang == "sv":
            return f"{SV_MONTH[event.month - 1]} den {event.day} år {event.year}"
        return f"{EN_MONTH[event.month - 1]} the {event.day}, {event.year}"
    if style == "week_wd":
        if lang == "fi":
            return f"viikolla {iso_week[1]} {FI_WD[event.weekday()]} ({event.year})"
        if lang == "sv":
            return f"vecka {iso_week[1]} {SV_WD_ON[event.weekday()]} ({event.year})"
        return f"in week {iso_week[1]} {EN_WD[event.weekday()]} ({event.year})"
    # numeric but unusual (not the v1 default d.m.yyyy)
    if lang == "sv":
        return f"{event.year}-{event.month:02d}-{event.day:02d}"
    return f"{event.day:02d}-{event.month:02d}-{event.year}"


def event_sentence_v2(typ: str, dstr: str, lang: str, rng: random.Random, extra: dict) -> str:
    """Phrasings disjoint from eval/regex_baseline.py KEYWORDS."""
    histo = extra.get("histo") or {"fi": "adenokarsinooma", "sv": "adenokarcinom", "en": "adenocarcinoma"}[lang]
    treat = extra.get("treat_phrase") or {"fi": "kuratiivinen hoito", "sv": "kurativ behandling", "en": "curative treatment"}[lang]
    if typ == "referral_received":
        opts = {
            "fi": [
                f"Konsultaatiopyyntö kirjattiin saapuneeksi {dstr}.",
                f"Lähete saapui toimistoon {dstr} (kirjoituspäivä on eri, ks. alla).",
                f"Asiakirja merkittiin saapuneeksi keuhkoyksikköön {dstr}.",
                f"Pyyntö tuli perille {dstr}.",
            ],
            "sv": [
                f"Konsultationsbegäran registrerades som inkommen {dstr}.",
                f"Handlingen antecknades som mottagen på enheten {dstr}.",
                f"Begäran nådde kliniken {dstr}.",
            ],
            "en": [
                f"The consultation request was logged as having arrived on {dstr}.",
                f"The document was marked as having reached the unit on {dstr}.",
                f"The request came through on {dstr}.",
            ],
        }
    elif typ == "ct_done":
        opts = {
            "fi": [
                f"Kerroskuvaus toteutettiin {dstr}.",
                f"Leikekuvaus on suoritettu {dstr}.",
                f"Kuvantaminen tehtiin {dstr} (varaus oli aiemmin).",
                f"Tutkimus käytiin kuvaamassa {dstr}.",
            ],
            "sv": [
                f"Skiktröntgen genomfördes {dstr}.",
                f"Bildtagningen utfördes {dstr} (tiden var bokad tidigare).",
                f"Undersökningen avbildades {dstr}.",
            ],
            "en": [
                f"Cross-sectional imaging was carried out on {dstr}.",
                f"The scan itself took place on {dstr} (the slot had been booked earlier).",
                f"Imaging was completed on {dstr}.",
            ],
        }
    elif typ == "biopsy_done":
        opts = {
            "fi": [
                f"Näyte otettiin tähystyksessä {dstr}.",
                f"Kudosnäytteet haettiin toimenpiteessä {dstr}.",
                f"Tähystyksen yhteydessä punktionäyte {dstr}.",
            ],
            "sv": [
                f"Prov togs i samband med speglingen {dstr}.",
                f"Vävnadsprover hämtades vid åtgärden {dstr}.",
            ],
            "en": [
                f"Tissue was obtained during the endoscopy on {dstr}.",
                f"Sampling was carried out at the procedure on {dstr}.",
            ],
        }
    elif typ == "pathology_result":
        opts = {
            "fi": [
                f"Mikroskooppinen lausunto valmistui {dstr}: {histo}.",
                f"Morforloginen tulos tuli {dstr} ({histo}).",
                f"Laboratorio ilmoitti histologian {dstr}: {histo}.",
            ],
            "sv": [
                f"Mikroskopiskt utlåtande blev klart {dstr}: {histo}.",
                f"Laboratoriet meddelade histologin {dstr}: {histo}.",
            ],
            "en": [
                f"The microscopic report was issued on {dstr}: {histo}.",
                f"The lab released the histology on {dstr}: {histo}.",
            ],
        }
    elif typ == "mdt_decision":
        opts = {
            "fi": [
                f"Tiimikokous pidettiin {dstr} ja suositus kirjattiin.",
                f"Yhteispalaveri järjestettiin {dstr}; linja muodostettiin siellä.",
                f"Kokoontuminen {dstr}: eri erikoisalojen yhteinen kanta merkitty.",
            ],
            "sv": [
                f"Teamcirkeln hölls {dstr} och rekommendationen antecknades.",
                f"Gemensamt möte {dstr}: den samlade bedömningen skrevs in.",
            ],
            "en": [
                f"The team huddle was held on {dstr} and the recommendation was written down.",
                f"A joint case conference took place on {dstr}; the shared view was recorded.",
            ],
        }
    elif typ == "treatment_decision":
        opts = {
            "fi": [
                f"Valittiin etenemistapa {dstr}: {treat}.",
                f"Sovittiin hoitomuodosta {dstr} ({treat}).",
                f"Kliininen valinta tehtiin {dstr}: {treat}.",
            ],
            "sv": [
                f"Man valde väg framåt {dstr}: {treat}.",
                f"Överenskommelse om behandlingsform {dstr} ({treat}).",
            ],
            "en": [
                f"The way forward was chosen on {dstr}: {treat}.",
                f"An agreement on the modality was reached on {dstr} ({treat}).",
            ],
        }
    elif typ == "treatment_start":
        opts = {
            "fi": [
                f"Toimenpide toteutui {dstr} ({treat}).",
                f"Aktiivinen hoito käynnistyi {dstr}.",
                f"Ensimmäinen hoitokerta oli {dstr}.",
            ],
            "sv": [
                f"Åtgärden genomfördes {dstr} ({treat}).",
                f"Den aktiva behandlingen kom i gång {dstr}.",
            ],
            "en": [
                f"The procedure went ahead on {dstr} ({treat}).",
                f"Active therapy got under way on {dstr}.",
            ],
        }
    else:
        raise ValueError(typ)
    return rng.choice(opts[lang])


def written_vs_received(lang: str, written: date, received: date, note: date, rng: random.Random) -> tuple[str, date]:
    """Referral written on `written`, received on `received`. Gold is received."""
    w = format_date_v2(written, note, lang, rng, False)
    r = format_date_v2(received, note, lang, rng, False)
    sent = {
        "fi": f"Konsultaatiopyyntö laadittiin {w}, mutta se kirjattiin saapuneeksi vasta {r}.",
        "sv": f"Konsultationsbegäran skrevs {w}, men registrerades som inkommen först {r}.",
        "en": f"The consultation request was written on {w}, but was only logged as having arrived on {r}.",
    }[lang]
    return sent, received


def booked_vs_done(lang: str, typ: str, booked: date, done: date, note: date, rng: random.Random) -> tuple[str, date]:
    b = format_date_v2(booked, note, lang, rng, False)
    d = format_date_v2(done, note, lang, rng, False)
    if typ == "ct_done":
        sent = {
            "fi": f"Kuvausaika merkittiin kalenteriin {b}; itse tutkimus toteutettiin {d}.",
            "sv": f"Bildtiden lades in i kalendern {b}; själva undersökningen genomfördes {d}.",
            "en": f"The scan slot was put in the calendar on {b}; the examination itself was carried out on {d}.",
        }[lang]
    else:
        sent = {
            "fi": f"Toimenpide varattiin {b}, mutta näyte otettiin vasta {d}.",
            "sv": f"Åtgärden bokades {b}, men provet togs först {d}.",
            "en": f"The procedure was booked on {b}, but sampling only took place on {d}.",
        }[lang]
    return sent, done


def old_note_block(lang: str, birth: date, rng: random.Random) -> str:
    old = date(rng.randint(2014, 2023), rng.randint(1, 12), rng.randint(1, 28))
    od = f"{old.day}.{old.month}.{old.year}"
    bd = f"{birth.day}.{birth.month}.{birth.year}"
    return {
        "fi": (
            f"— ote vanhasta kirjauksesta {od}: syntymäaika {bd}; "
            f"sappirakon poisto {od}; ei liity nykyiseen keuhkoselvittelyyn. —\n"
        ),
        "sv": (
            f"— utdrag ur äldre anteckning {od}: födelsedatum {bd}; "
            f"galloperation {od}; hör inte till den aktuella lungutredningen. —\n"
        ),
        "en": (
            f"— excerpt from an older note dated {od}: date of birth {bd}; "
            f"cholecystectomy {od}; unrelated to the present lung work-up. —\n"
        ),
    }[lang]


def v2_negations(lang: str, note: date, rng: random.Random) -> list[str]:
    future = note + timedelta(days=rng.randint(4, 16))
    fut = format_date_v2(future, note, lang, rng, False)
    return {
        "fi": [
            f"Kuvantaminen on vasta ajanvaraus {fut}, sitä ei ole toteutettu.",
            "Tähystys peruttiin viime hetkellä eikä näytettä saatu.",
            "Tiimikokousta ei järjestetty tällä käynnillä, se on siirretty.",
            "Aktiivista hoitoa ei ole aloitettu, vasta pohditaan vaihtoehtoja.",
        ],
        "sv": [
            f"Bildtagningen är än så länge bara en bokad tid {fut} och har inte genomförts.",
            "Speglingen ställdes in i sista stund och inget prov togs.",
            "Något teammöte hölls inte vid detta besök.",
            "Aktiv behandling har inte kommit i gång.",
        ],
        "en": [
            f"Imaging is only a reserved slot on {fut} and has not been carried out.",
            "The endoscopy was called off at short notice and no sample was obtained.",
            "No team huddle was arranged at this visit; it was deferred.",
            "Active therapy has not got under way; options are still being weighed.",
        ],
    }[lang]


def ocr_noise(s: str, rng: random.Random, rate: float) -> str:
    """Light OCR-like noise that avoids breaking digits in dates."""
    if rate <= 0:
        return s
    out = []
    i = 0
    while i < len(s):
        ch = s[i]
        # never touch digits or adjacent date punctuation
        if ch.isdigit() or (ch in ".-/" and i > 0 and (s[i - 1].isdigit() or (i + 1 < len(s) and s[i + 1].isdigit()))):
            out.append(ch)
            i += 1
            continue
        if rng.random() < rate and ch.isalpha():
            op = rng.choice(["space", "hyphen", "confuse", "none", "none"])
            if op == "space" and i + 1 < len(s) and s[i + 1].isalpha():
                out.append(ch)
                out.append(" ")
            elif op == "hyphen" and i + 1 < len(s) and s[i + 1].isalpha():
                out.append(ch)
                out.append("-")
            elif op == "confuse":
                table = {"o": "0", "O": "0", "l": "1", "I": "1", "m": "rn"}
                out.append(table.get(ch, ch))
            else:
                out.append(ch)
        else:
            out.append(ch)
        i += 1
    return "".join(out)


def header(meta: dict) -> str:
    lines = [
        "=" * 78,
        SYNTHETIC_BANNER,
        f"corpus_id: {CORPUS_ID}",
        f"patient_id: {meta['patient_id']}",
        f"document_id: {meta['document_id']}",
        f"document_type: {meta['document_type']}",
        f"language: {meta['lang']}",
        f"note_date: {meta['note_date']}",
        f"display_name: {meta['display_name']} (invented)",
        "DO NOT treat this text as a clinical record. Corpus v2, held-out phrasing.",
        "=" * 78,
        "",
    ]
    return "\n".join(lines)


def dictated_wrap(lang: str, sentences: list[str], rng: random.Random) -> str:
    fillers = {
        "fi": ["Öö, ", "Kirjataanpa auki: ", "Siis, ", "Potilaan kohdalla ", "Lyhyesti: "],
        "sv": ["Alltså, ", "Vi antecknar: ", "Kort sagt: ", "Vad gäller patienten "],
        "en": ["Um, ", "Let me dictate this: ", "Briefly, ", "In this case "],
    }[lang]
    body = " ".join(s.strip() for s in sentences)
    return rng.choice(fillers) + body + "\n"


def render_document_v2(p: dict, dplan: dict, rng: random.Random) -> tuple[str, list[dict]]:
    lang = dplan["lang"]
    note: date = dplan["note_date"]
    typo_rate = dplan.get("extras", {}).get("typo_rate", 0.0)
    if typo_rate == 0 and rng.random() < 0.25:
        typo_rate = 0.05
    prefer_rel = dplan.get("extras", {}).get("prefer_relative", False) or p["archetype"] == "relative_only"
    ocr_rate = 0.03 if p["archetype"] not in ("typo_heavy",) else 0.06
    if p["archetype"] == "typo_heavy":
        typo_rate = max(typo_rate, 0.18)
        ocr_rate = 0.08
    hospital = rng.choice(v1.HOSPITALS[lang])
    finding = rng.choice(v1.FINDINGS[lang])
    histo = rng.choice(v1.HISTO[lang])
    treat = rng.choice(v1.TREATMENTS[lang])
    extra = {"histo": histo, "treat_phrase": treat[1], "finding": finding}
    birth = date.fromisoformat(p["birth_date"])
    event_dates = {k: date.fromisoformat(v) for k, v in p["event_dates"].items()}

    b = v1.Builder()
    b.add(v1.salutation(lang, p["display_name"], p["patient_id"], hospital, note, birth, rng))

    # Free-flowing intro rather than the v1 "Käynnin syy" line
    intro = {
        "fi": "Diktoitu merkintä keuhkoselvittelystä (synteettinen harjoitusteksti).\n",
        "sv": "Dikterad anteckning från lungutredningen (syntetisk övningstext).\n",
        "en": "Dictated entry from the lung work-up (synthetic training text).\n",
    }[lang]
    if not dplan.get("extras", {}).get("telegram"):
        b.add(intro)

    event_lines: list[tuple[str, date, str]] = []  # typ, date, sentence — shuffled later

    # Written vs received for referral when we introduce it
    if "referral_received" in dplan["introduce"] and "referral_received" in event_dates:
        rec = event_dates["referral_received"]
        written = rec - timedelta(days=rng.randint(1, 6))
        sent, gold_d = written_vs_received(lang, written, rec, note, rng)
        event_lines.append(("referral_received", gold_d, sent if sent.endswith("\n") else sent + "\n"))

    if "ct_done" in dplan["introduce"] and "ct_done" in event_dates:
        done = event_dates["ct_done"]
        booked = done - timedelta(days=rng.randint(2, 8))
        if rng.random() < 0.7:
            sent, gold_d = booked_vs_done(lang, "ct_done", booked, done, note, rng)
        else:
            dstr = format_date_v2(done, note, lang, rng, prefer_rel)
            sent = event_sentence_v2("ct_done", dstr, lang, rng, extra)
            gold_d = done
        if not sent.endswith("\n"):
            sent += "\n"
        # finding after the event, not inside the gold span
        event_lines.append(("ct_done", gold_d, sent))
        b_flag = ("finding", {
            "fi": f"Kuvissa erottui {finding}.\n",
            "sv": f"På bilderna sågs {finding}.\n",
            "en": f"The pictures showed {finding}.\n",
        }[lang])
        event_lines.append(b_flag)  # type: ignore

    for typ in dplan["introduce"]:
        if typ in ("referral_received", "ct_done"):
            continue
        if typ not in event_dates:
            continue
        ed = event_dates[typ]
        if typ == "biopsy_done" and rng.random() < 0.55:
            booked = ed - timedelta(days=rng.randint(2, 7))
            sent, gold_d = booked_vs_done(lang, typ, booked, ed, note, rng)
        else:
            dstr = format_date_v2(ed, note, lang, rng, prefer_rel)
            sent = event_sentence_v2(typ, dstr, lang, rng, extra)
            gold_d = ed
        if not sent.endswith("\n"):
            sent += "\n"
        event_lines.append((typ, gold_d, sent))

    # Accurate history with v2 phrasing (still gold)
    for typ in dplan["history"]:
        if typ not in event_dates:
            continue
        if typ in dplan["introduce"]:
            continue
        ed = event_dates[typ]
        dstr = format_date_v2(ed, note, lang, rng, prefer_rel)
        sent = event_sentence_v2(typ, dstr, lang, rng, extra)
        if not sent.endswith("\n"):
            sent += "\n"
        event_lines.append((typ, ed, sent))

    if dplan.get("extras", {}).get("conflict_ct"):
        wrong = dplan["extras"]["conflict_ct"]
        dstr = format_date_v2(wrong, note, lang, rng, prefer_rel)
        sent = event_sentence_v2("ct_done", dstr, lang, rng, extra)
        if not sent.endswith("\n"):
            sent += "\n"
        event_lines.append(("ct_done", wrong, sent))

    # OUT OF ORDER: shuffle event lines so the pathway is not chronological
    events_only = [x for x in event_lines if x[0] != "finding"]
    findings = [x for x in event_lines if x[0] == "finding"]
    rng.shuffle(events_only)
    mixed = events_only + findings
    if rng.random() < 0.55 and len(mixed) >= 2:
        # dictated paragraph for a subset, rest as sentences
        n_dict = rng.randint(1, len(mixed))
        dict_part, rest = mixed[:n_dict], mixed[n_dict:]
        narr_sents = []
        pending_gold = []
        for item in dict_part:
            if item[0] == "finding":
                narr_sents.append(item[1].strip())
            else:
                typ, ed, sent = item
                narr_sents.append(sent.strip())
                pending_gold.append((typ, ed, sent.strip()))
        paragraph = dictated_wrap(lang, narr_sents, rng)
        # If we merge into one paragraph, evidence_span must still be a substring.
        # Keep each event sentence as its own add_event BEFORE the wrap? Safer: add events
        # as individual sentences (possibly shuffled) and add a dictated filler around them.
        # We'll output shuffled individual sentences plus a dictated wrapper line.
        b.add(dictated_wrap(lang, [" ".join(narr_sents)], rng).split("\n")[0] + "\n" if False else "")
        # simpler reliable path: add shuffled sentences as events
        for item in dict_part:
            if item[0] == "finding":
                b.add(item[1])
            else:
                typ, ed, sent = item
                b.add_event(typ, ed, sent)
        for item in rest:
            if item[0] == "finding":
                b.add(item[1])
            else:
                typ, ed, sent = item
                b.add_event(typ, ed, sent)
    else:
        for item in mixed:
            if item[0] == "finding":
                b.add(item[1])
            else:
                typ, ed, sent = item
                b.add_event(typ, ed, sent)

    # Negations / plans (not gold) — v2 wording
    n_neg = 2 if dplan.get("extras", {}).get("force_negations") or dplan.get("extras", {}).get("cancelled_biopsy") else (0 if dplan.get("extras", {}).get("telegram") else (1 if rng.random() < 0.55 else 0))
    if dplan.get("extras", {}).get("cancelled_biopsy"):
        b.add({
            "fi": "Tähystys peruttiin viime hetkellä eikä näytettä saatu tuolloin.\n",
            "sv": "Speglingen ställdes in i sista stund och inget prov togs då.\n",
            "en": "The endoscopy was called off at short notice and no sample was obtained then.\n",
        }[lang])
    if n_neg:
        negs = v2_negations(lang, note, rng)
        rng.shuffle(negs)
        for s in negs[:n_neg]:
            b.add(s + "\n")

    if dplan.get("extras", {}).get("wait_note"):
        b.add({
            "fi": "Jatko on auki. Aktiivista hoitoa ei ole käynnistetty tässä vaiheessa.\n",
            "sv": "Fortsättningen är öppen. Aktiv behandling har inte kommit i gång än.\n",
            "en": "Next steps remain open. Active therapy has not got under way at this stage.\n",
        }[lang])

    # Copy-pasted older note + distractors (ambiguous "tammikuun alussa" etc.)
    if rng.random() < 0.7 or p["archetype"] == "distractor":
        b.add(old_note_block(lang, birth, rng))
    vague = {
        "fi": "Aiemmin jossain tammikuun alussa oli käynyt kontrollissa; tarkkaa päivää ei ole tässä.\n",
        "sv": "Tidigare, någon gång i början av januari, hade hen ett kontrollbesök; exakt dag saknas här.\n",
        "en": "Previously, sometime in early January, there was a follow-up visit; the exact day is not in this note.\n",
    }[lang]
    if rng.random() < 0.4 or p["archetype"] == "distractor":
        b.add(vague)

    n_dist = 2 if p["archetype"] == "distractor" else rng.randint(0, 1)
    for s in v1.distractors(lang, birth, rng, n_dist):
        b.add(s + "\n")

    if dplan.get("extras", {}).get("telegram"):
        b.add({
            "fi": "\n(Synteettinen lyhyt diktoitu merkintä.)\n",
            "sv": "\n(Syntetisk kort dikterad anteckning.)\n",
            "en": "\n(Synthetic short dictated note.)\n",
        }[lang])
    else:
        b.add({
            "fi": "\nKirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.\n",
            "sv": "\nAntecknat av: syntetisk testanvändare. Detta är inte en verklig journal.\n",
            "en": "\nEntered by: synthetic test user. This is not a real clinical record.\n",
        }[lang])

    body, gold = b.render(rng, typo_rate)
    if ocr_rate:
        # apply OCR per gold-safe path: typo already applied; OCR on full body and update spans
        new_body, new_gold = _ocr_body_preserve_spans(body, gold, rng, ocr_rate)
        body, gold = new_body, new_gold
    return body, gold


def _ocr_body_preserve_spans(body: str, gold: list[dict], rng: random.Random, rate: float) -> tuple[str, list[dict]]:
    """Apply OCR to non-span text; lightly to spans but keep them matching."""
    # Transform each span independently, then the leftover text.
    # Simplest safe approach: only OCR regions that are not inside any evidence_span.
    spans = []
    for g in gold:
        i = body.find(g["evidence_span"])
        if i < 0:
            return body, gold
        spans.append((i, i + len(g["evidence_span"]), g))
    spans.sort()
    out = []
    new_gold = []
    cursor = 0
    for a, b, g in spans:
        out.append(ocr_noise(body[cursor:a], rng, rate))
        noisy_span = ocr_noise(body[a:b], rng, rate * 0.4)
        start = sum(len(x) for x in out)
        out.append(noisy_span)
        ng = dict(g)
        ng["evidence_span"] = noisy_span.strip() or g["evidence_span"]
        new_gold.append(ng)
        cursor = b
    out.append(ocr_noise(body[cursor:], rng, rate))
    text = "".join(out)
    for g in new_gold:
        if g["evidence_span"] not in text:
            # fall back to original if we broke a span
            return body, gold
    return text, new_gold


def assign_splits(patients: list[dict], rng: random.Random) -> None:
    """40 dev / 80 test, stratified by archetype. Tune regex on dev only."""
    by = {}
    for p in patients:
        by.setdefault(p["archetype"], []).append(p)
    dev_n = 0
    for arch, group in by.items():
        rng.shuffle(group)
        n_dev = max(1, round(len(group) * 40 / 120)) if len(group) >= 2 else 0
        # keep total near 40
        for p in group:
            p["split"] = None
        for p in group[:n_dev]:
            p["split"] = "dev"
            dev_n += 1
        for p in group[n_dev:]:
            p["split"] = "test"
    # adjust to exactly 40 dev
    test = [p for p in patients if p["split"] == "test"]
    dev = [p for p in patients if p["split"] == "dev"]
    rng.shuffle(test)
    rng.shuffle(dev)
    while len(dev) > 40:
        p = dev.pop()
        p["split"] = "test"
    while len(dev) < 40 and test:
        p = test.pop()
        p["split"] = "dev"
        dev.append(p)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED_DEFAULT_V2)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "data_v2")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    # Reuse v1 patient/event planning so we keep 120 patients / 600 docs / hard tags,
    # but render with held-out phrasing and new IDs.
    patients_plan = v1.plan_corpus(rng)
    v1.assign_languages(patients_plan, rng)
    assign_splits(patients_plan, random.Random(args.seed + 7))

    out: Path = args.out
    doc_dir = out / "documents"
    if doc_dir.exists():
        for f in doc_dir.glob("*.txt"):
            f.unlink()
    doc_dir.mkdir(parents=True, exist_ok=True)

    all_docs = []
    patients_out = []
    lang_counts = Counter()
    type_counts = Counter()
    event_counts = Counter()
    split_docs = Counter()

    for p in patients_plan:
        # new id space so v1 easy set stays untouched
        old_id = p["patient_id"]
        num = old_id.split("P")[-1]
        pid = f"SYN2-P{num}"
        p["patient_id"] = pid
        p["display_name"] = p["display_name"].replace(old_id, pid)
        rendered = []
        for i, dplan in enumerate(p["doc_plan"], start=1):
            if isinstance(dplan["note_date"], str):
                dplan["note_date"] = date.fromisoformat(dplan["note_date"])
            doc_id = f"{pid}-{dplan['document_type']}-{i:02d}"
            meta = {
                "patient_id": pid,
                "document_id": doc_id,
                "document_type": dplan["document_type"],
                "lang": dplan["lang"],
                "note_date": iso(dplan["note_date"]),
                "display_name": p["display_name"],
            }
            body, gold = render_document_v2(p, dplan, rng)
            text = header(meta) + body
            for g in gold:
                if g["evidence_span"] not in text:
                    raise AssertionError(f"{doc_id}: span lost: {g}")
            path = doc_dir / f"{doc_id}.txt"
            path.write_text(text, encoding="utf-8")
            rec = {
                "document_id": doc_id,
                "patient_id": pid,
                "document_type": dplan["document_type"],
                "lang": dplan["lang"],
                "note_date": iso(dplan["note_date"]),
                "path": str(path.relative_to(out)),
                "events": gold,
                "n_chars": len(text),
                "synthetic": True,
                "split": p["split"],
                "corpus_id": CORPUS_ID,
            }
            all_docs.append(rec)
            rendered.append(rec)
            lang_counts[dplan["lang"]] += 1
            type_counts[dplan["document_type"]] += 1
            split_docs[p["split"]] += 1
            for g in gold:
                event_counts[g["type"]] += 1

        pl = v1.patient_level_gold(p, rendered)
        patients_out.append({
            "patient_id": pid,
            "display_name": p["display_name"],
            "sex": p["sex"],
            "birth_date": p["birth_date"],
            "archetype": p["archetype"],
            "hard_tags": p["hard_tags"],
            "split": p["split"],
            "document_ids": [d["document_id"] for d in rendered],
            "synthetic": True,
            "corpus_id": CORPUS_ID,
            **pl,
        })

    n = len(all_docs)
    stats = {
        "corpus_id": CORPUS_ID,
        "synthetic": True,
        "seed": args.seed,
        "n_documents": n,
        "n_patients": len(patients_out),
        "splits": {
            "dev_patients": sum(1 for p in patients_out if p["split"] == "dev"),
            "test_patients": sum(1 for p in patients_out if p["split"] == "test"),
            "dev_documents": split_docs["dev"],
            "test_documents": split_docs["test"],
        },
        "languages": dict(lang_counts),
        "language_share": {k: round(v / n, 4) for k, v in lang_counts.items()},
        "document_types": dict(type_counts),
        "event_mentions": dict(event_counts),
        "n_alerts": sum(1 for p in patients_out if p["alert"]),
        "n_with_referral": sum(1 for p in patients_out if p["referral_date"]),
        "n_with_treatment_start": sum(1 for p in patients_out if p["treatment_start_date"]),
        "archetypes": dict(Counter(p["archetype"] for p in patients_out)),
        "alert_rule": f"day_count >= {ALERT_DAY} and no treatment_start",
        "merge_rule": "latest_document_wins",
        "split_rule": "40 patients dev / 80 test, stratified by archetype; regex may be tuned on dev only",
    }
    gold = {
        "corpus_id": CORPUS_ID,
        "synthetic": True,
        "seed": args.seed,
        "event_types": EVENT_TYPES,
        "documents": {
            d["document_id"]: {
                "events": d["events"],
                "note_date": d["note_date"],
                "patient_id": d["patient_id"],
                "split": d["split"],
            }
            for d in all_docs
        },
        "patients": {p["patient_id"]: p for p in patients_out},
    }
    (out / "documents.jsonl").write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in all_docs) + "\n", encoding="utf-8")
    (out / "patients.json").write_text(json.dumps(patients_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "gold.json").write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "splits.json").write_text(json.dumps({
        "dev": [p["patient_id"] for p in patients_out if p["split"] == "dev"],
        "test": [p["patient_id"] for p in patients_out if p["split"] == "test"],
        "rule": stats["split_rule"],
    }, indent=2) + "\n", encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps({
        "corpus_id": CORPUS_ID,
        "synthetic": True,
        "seed": args.seed,
        "documents": [{k: d[k] for k in ("document_id", "patient_id", "document_type", "lang", "note_date", "path", "split")} for d in all_docs],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if n < 580 or n > 620:
        print(f"WARNING: expected ~600 documents, got {n}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
