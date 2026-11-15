#!/usr/bin/env python3
"""Generate a seeded, reproducible SYNTHETIC lung-pathway corpus for Tasan Extract.

No real patients. No LLM. Templates + combinatorial variation.
Every document file starts with a SYNTHETIC banner.
"""
from __future__ import annotations

import argparse
import json
import random
import sys
from collections import Counter
from copy import deepcopy
from datetime import date, timedelta
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from common import (  # noqa: E402
    ALERT_DAY,
    CORPUS_ID,
    DOC_TYPES,
    EVENT_TYPES,
    SEED_DEFAULT,
    SYNTHETIC_BANNER,
)

WEEKDAYS_FI = [
    "maanantaina",
    "tiistaina",
    "keskiviikkona",
    "torstaina",
    "perjantaina",
    "lauantaina",
    "sunnuntaina",
]
WEEKDAYS_SV = [
    "i måndags",
    "i tisdags",
    "i onsdags",
    "i torsdags",
    "i fredags",
    "i lördags",
    "i söndags",
]
WEEKDAYS_EN = [
    "last Monday",
    "last Tuesday",
    "last Wednesday",
    "last Thursday",
    "last Friday",
    "last Saturday",
    "last Sunday",
]

# Obviously invented names — not intended to refer to anyone real.
NAMES = [
    ("Aino Synteettinen", "F", "fi"),
    ("Matti Mallipotilas", "M", "fi"),
    ("Eeva Esimerkki", "F", "fi"),
    ("Yrjö Yksikkötesti", "M", "fi"),
    ("Kirsi Keksitty", "F", "fi"),
    ("Pekka Paikkamerkki", "M", "fi"),
    ("Laura Loremten", "F", "fi"),
    ("Hannu Harjoitus", "M", "fi"),
    ("Sari Sijaisnimi", "F", "fi"),
    ("Olli Oletettu", "M", "fi"),
    ("Tuula Testinen", "F", "fi"),
    ("Kari Keinotekoinen", "M", "fi"),
    ("Ritva Rakennettu", "F", "fi"),
    ("Juhani Jäljitelmä", "M", "fi"),
    ("Anna Anonyymi", "F", "fi"),
    ("Nils Fiktiv", "M", "sv"),
    ("Eva Påhittad", "F", "sv"),
    ("Lars Låtsas", "M", "sv"),
    ("Ingrid Inventerad", "F", "sv"),
    ("Johan Testdata", "M", "sv"),
    ("Karin Konstruerad", "F", "sv"),
    ("Erik Exempelsson", "M", "sv"),
    ("Jane Synthetic", "F", "en"),
    ("John Placeholder", "M", "en"),
    ("Mary Fictitious", "F", "en"),
    ("Alan Invented", "M", "en"),
    ("Helen Mockpatient", "F", "en"),
    ("Peter Samplecase", "M", "en"),
]

HOSPITALS = {
    "fi": [
        "Synteettisen hyvinvointialueen keskussairaala",
        "Mallikylän keuhkoklinikka",
        "Keksityn yliopistollinen sairaala",
    ],
    "sv": [
        "Fiktiva välfärdsområdets centralsjukhus",
        "Påhittade lungkliniken",
        "Testdata universitetssjukhus",
    ],
    "en": [
        "Synthetic Wellbeing County Hospital",
        "Placeholder Lung Clinic",
        "Invented University Hospital",
    ],
}

FINDINGS = {
    "fi": [
        "oikean ylälohkon 3,1 cm tuumori",
        "vasemman alalohkon 2,4 cm muutos",
        "oikean keskilohohon 4,0 cm massa",
        "vasemman ylälohkon 1,8 cm kyhmy ja välikarsinan imusolmukkeet",
    ],
    "sv": [
        "en 3,1 cm tumör i höger övre lob",
        "en 2,4 cm förändring i vänster nedre lob",
        "en 4,0 cm massa i höger mellannlob",
        "en 1,8 cm knuta i vänster övre lob och mediastinala lymfkörtlar",
    ],
    "en": [
        "a 3.1 cm tumour in the right upper lobe",
        "a 2.4 cm lesion in the left lower lobe",
        "a 4.0 cm mass in the right middle lobe",
        "a 1.8 cm nodule in the left upper lobe with mediastinal nodes",
    ],
}

HISTO = {
    "fi": [
        "adenokarsinooma",
        "levyepiteelikarsinooma",
        "pienisoluinen keuhkosyöpä",
        "NSCLC, ei tarkemmin luokiteltu",
    ],
    "sv": [
        "adenokarcinom",
        "skivepitelkarcinom",
        "småcellig lungcancer",
        "NSCLC, ej närmare klassificerad",
    ],
    "en": [
        "adenocarcinoma",
        "squamous cell carcinoma",
        "small-cell lung cancer",
        "NSCLC, not otherwise specified",
    ],
}

TREATMENTS = {
    "fi": [
        ("surgery", "kuratiivinen lobektomia", "Leikkaus (lobektomia) tehty {d}."),
        ("surgery", "kiilaresektio", "Kiilaresektio suoritettu {d}."),
        ("rt", "SBRT", "SBRT-sädehoito aloitettu {d}."),
        ("rt", "sädehoito", "Sädehoito aloitettu {d}."),
        ("chemo", "sytostaatti", "Sytostaattihoito aloitettu {d}."),
        ("chemo", "solunsalpaaja", "Solunsalpaajahoito käynnistetty {d}."),
    ],
    "sv": [
        ("surgery", "kurativ lobektomi", "Operation (lobektomi) utförd {d}."),
        ("surgery", "kilresektion", "Kilresektion utförd {d}."),
        ("rt", "SBRT", "SBRT-strålbehandling påbörjad {d}."),
        ("rt", "strålbehandling", "Strålbehandling påbörjad {d}."),
        ("chemo", "cytostatika", "Cytostatikabehandling påbörjad {d}."),
        ("chemo", "cellgifter", "Cellgiftsbehandling startad {d}."),
    ],
    "en": [
        ("surgery", "curative lobectomy", "Surgery (lobectomy) performed on {d}."),
        ("surgery", "wedge resection", "Wedge resection performed on {d}."),
        ("rt", "SBRT", "SBRT radiotherapy started on {d}."),
        ("rt", "radiotherapy", "Radiotherapy started on {d}."),
        ("chemo", "chemotherapy", "Chemotherapy started on {d}."),
        ("chemo", "cytotoxic therapy", "Cytotoxic therapy commenced on {d}."),
    ],
}


def iso(d: date) -> str:
    return d.isoformat()


def last_weekday_before(note: date, weekday: int) -> date:
    """Most recent `weekday` (Mon=0) strictly before `note`."""
    delta = (note.weekday() - weekday) % 7
    if delta == 0:
        delta = 7
    return note - timedelta(days=delta)


def format_date(event: date, note: date, lang: str, rng: random.Random, prefer_relative: bool) -> str:
    """Render `event` as it would appear in a note written on `note`."""
    delta = (note - event).days
    rel = None
    if delta == 1:
        rel = {"fi": "eilen", "sv": "igår", "en": "yesterday"}[lang]
    elif delta == 2:
        rel = {"fi": "toissapäivänä", "sv": "i förrgår", "en": "the day before yesterday"}[lang]
    elif 6 <= delta <= 8:
        rel = {"fi": "viikko sitten", "sv": "för en vecka sedan", "en": "a week ago"}[lang]
    elif 13 <= delta <= 15:
        rel = {"fi": "kaksi viikkoa sitten", "sv": "för två veckor sedan", "en": "two weeks ago"}[lang]
    else:
        prev = last_weekday_before(note, event.weekday())
        if event == prev and event.weekday() != note.weekday():
            if lang == "fi":
                rel = f"viime {WEEKDAYS_FI[event.weekday()]}"
            elif lang == "sv":
                rel = WEEKDAYS_SV[event.weekday()]
            else:
                rel = WEEKDAYS_EN[event.weekday()]

    # Relative only when it actually resolves, and either requested or randomly chosen.
    if rel and (prefer_relative or rng.random() < 0.18):
        return rel

    styles = [
        "dmy",
        "dmy",
        "dmy",
        "dmy2",
        "dm",
        "slash",
        "iso",
    ]
    style = rng.choice(styles)
    if style == "dmy":
        return f"{event.day}.{event.month}.{event.year}"
    if style == "dmy2":
        return f"{event.day}.{event.month}.{event.year % 100:02d}"
    if style == "dm":
        return f"{event.day}.{event.month}"
    if style == "slash":
        if rng.random() < 0.5:
            return f"{event.day}/{event.month}/{event.year}"
        return f"{event.day}/{event.month}"
    return event.isoformat()


def typo_word(w: str, rng: random.Random) -> str:
    if len(w) < 4 or any(c.isdigit() for c in w):
        return w
    letters = list(w)
    # never break obvious date-like punctuation-only tokens
    ops = []
    if any(c in "äöåÄÖÅ" for c in w):
        ops.append("deaccent")
    ops.extend(["swap", "drop", "double"])
    op = rng.choice(ops)
    if op == "deaccent":
        table = str.maketrans("äöåÄÖÅ", "aoaAOA")
        return w.translate(table)
    idx = rng.randint(0, len(letters) - 1)
    if op == "swap" and idx < len(letters) - 1 and letters[idx].isalpha() and letters[idx + 1].isalpha():
        letters[idx], letters[idx + 1] = letters[idx + 1], letters[idx]
    elif op == "drop" and letters[idx].isalpha():
        letters.pop(idx)
    elif op == "double" and letters[idx].isalpha():
        letters.insert(idx, letters[idx])
    return "".join(letters)


def typo_sentence(s: str, rng: random.Random, rate: float) -> str:
    words = s.split(" ")
    out = []
    for w in words:
        if not w:
            out.append(w)
            continue
        lead, core, trail = "", w, ""
        while core and core[0] in "([\"'":
            lead += core[0]
            core = core[1:]
        while core and core[-1] in ".,;:!?)]\"'":
            trail = core[-1] + trail
            core = core[:-1]
        if core and rng.random() < rate:
            core = typo_word(core, rng)
        out.append(lead + core + trail)
    return " ".join(out)


class Builder:
    def __init__(self):
        self.chunks: list[tuple[str, str, dict | None]] = []

    def add(self, text: str) -> None:
        if text:
            self.chunks.append(("text", text, None))

    def add_event(self, typ: str, d: date, sentence: str) -> None:
        if not sentence.endswith("\n") and not sentence.endswith(" "):
            # event sentences are stored without forcing newline; caller includes \n
            pass
        self.chunks.append(("event", sentence, {"type": typ, "date": iso(d)}))

    def render(self, rng: random.Random, typo_rate: float) -> tuple[str, list[dict]]:
        parts: list[str] = []
        gold: list[dict] = []
        for kind, raw, meta in self.chunks:
            text = typo_sentence(raw, rng, typo_rate) if typo_rate > 0 else raw
            if kind == "event" and meta:
                span = text.strip()
                gold.append({
                    "type": meta["type"],
                    "date": meta["date"],
                    "evidence_span": span,
                })
            parts.append(text)
        body = "".join(parts)
        for g in gold:
            if g["evidence_span"] not in body:
                raise AssertionError(f"evidence span not in body: {g}")
        return body, gold


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
        "DO NOT treat this text as a clinical record.",
        "=" * 78,
        "",
    ]
    return "\n".join(lines)


def salutation(lang: str, name: str, pid: str, hospital: str, note: date, birth: date, rng: random.Random) -> str:
    nd = f"{note.day}.{note.month}.{note.year}"
    bd = f"{birth.day}.{birth.month}.{birth.year}"
    if lang == "fi":
        return (
            f"{hospital}\n"
            f"Kirjauspäivä {nd}. Potilas: {name} ({pid}), s. {bd}.\n"
            f"SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.\n\n"
        )
    if lang == "sv":
        return (
            f"{hospital}\n"
            f"Anteckningsdatum {nd}. Patient: {name} ({pid}), f. {bd}.\n"
            f"SYNTETISK patientjournal, ingen verklig person.\n\n"
        )
    return (
        f"{hospital}\n"
        f"Note date {nd}. Patient: {name} ({pid}), DOB {bd}.\n"
        f"SYNTHETIC record, not a real person.\n\n"
    )


def _clean_date_dots(s: str) -> str:
    """Avoid '14.11..' when a day.month. form already ends with a dot."""
    while ".." in s:
        s = s.replace("..", ".")
    return s


def event_sentence(typ: str, dstr: str, lang: str, rng: random.Random, extra: dict) -> str:

    finding = extra.get("finding", "")
    histo = extra.get("histo", "")
    treat = extra.get("treat_phrase", "")
    if typ == "referral_received":
        opts = {
            "fi": [
                f"Lähete saapunut keuhkoklinikalle {dstr}.",
                f"Lähete kirjattu {dstr}.",
                f"ESH-lähete vastaanotettu {dstr}.",
                f"Keuhkoklinikan lähete saapui {dstr}.",
            ],
            "sv": [
                f"Remiss inkommen till lungkliniken {dstr}.",
                f"Remissen mottogs {dstr}.",
                f"Specialistremiss registrerad {dstr}.",
            ],
            "en": [
                f"Referral received by the lung clinic on {dstr}.",
                f"The referral was registered on {dstr}.",
                f"Specialist referral received {dstr}.",
            ],
        }
    elif typ == "ct_done":
        opts = {
            "fi": [
                f"Thoraxin TT tehty {dstr}.",
                f"Tietokonetomografia (TT) suoritettiin {dstr}.",
                f"Keuhko-TT tehty {dstr}.",
                f"PET-TT tehty {dstr}.",
                f"TT-tutkimus tehty {dstr}.",
            ],
            "sv": [
                f"DT torax utförd {dstr}.",
                f"Datortomografi (DT) genomfördes {dstr}.",
                f"PET-DT utförd {dstr}.",
            ],
            "en": [
                f"Chest CT performed on {dstr}.",
                f"CT thorax was carried out on {dstr}.",
                f"PET-CT performed on {dstr}.",
            ],
        }
    elif typ == "biopsy_done":
        opts = {
            "fi": [
                f"Bronkoskopia ja biopsia tehty {dstr}.",
                f"EBUS-bronkoskopia suoritettu {dstr}; biopsiat otettu.",
                f"Biopsiat otettu bronkoskopiassa {dstr}.",
                f"Bronkoskopia {dstr}, näytteet otettu.",
            ],
            "sv": [
                f"Bronkoskopi och biopsi utförd {dstr}.",
                f"EBUS-bronkoskopi genomförd {dstr}; biopsier tagna.",
                f"Biopsier togs vid bronkoskopi {dstr}.",
            ],
            "en": [
                f"Bronchoscopy and biopsy performed on {dstr}.",
                f"EBUS bronchoscopy carried out on {dstr}; biopsies taken.",
                f"Biopsies were obtained during bronchoscopy on {dstr}.",
            ],
        }
    elif typ == "pathology_result":
        h = histo or {"fi": "adenokarsinooma", "sv": "adenokarcinom", "en": "adenocarcinoma"}[lang]
        opts = {
            "fi": [
                f"PAD-vastaus valmistui {dstr}: {h}.",
                f"Patologin lausunto {dstr}: {h}.",
                f"Histologinen vastaus saapui {dstr} ({h}).",
            ],
            "sv": [
                f"PAD-svar klart {dstr}: {h}.",
                f"Patologiskt utlåtande {dstr}: {h}.",
                f"Histologiskt svar inkom {dstr} ({h}).",
            ],
            "en": [
                f"Pathology result issued on {dstr}: {h}.",
                f"Histopathology report dated {dstr}: {h}.",
                f"PAD result available {dstr} ({h}).",
            ],
        }
    elif typ == "mdt_decision":
        opts = {
            "fi": [
                f"Moniammatillinen kokous (MDT) {dstr}: suositellaan etenemistä hoitoon.",
                f"MDT {dstr}: hoitolinja vahvistettu.",
                f"Hoitokokous {dstr}: moniammatillinen suositus kirjattu.",
            ],
            "sv": [
                f"Multidisciplinär konferens (MDK) {dstr}: rekommendation om behandling.",
                f"MDT/MDK {dstr}: behandlingslinje bekräftad.",
                f"Vårdkonferens {dstr}: multidisciplinär rekommendation.",
            ],
            "en": [
                f"Multidisciplinary meeting (MDT) on {dstr}: recommend proceeding to treatment.",
                f"MDT on {dstr}: treatment pathway confirmed.",
                f"MDT conference {dstr}: multidisciplinary recommendation recorded.",
            ],
        }
    elif typ == "treatment_decision":
        t = treat or {"fi": "kuratiivinen hoito", "sv": "kurativ behandling", "en": "curative treatment"}[lang]
        opts = {
            "fi": [
                f"Hoitopäätös {dstr}: {t}.",
                f"Linjaus {dstr}: {t}.",
                f"Päätettiin {dstr} aloittaa {t}.",
            ],
            "sv": [
                f"Behandlingsbeslut {dstr}: {t}.",
                f"Beslutades {dstr} att gå vidare med {t}.",
            ],
            "en": [
                f"Treatment decision on {dstr}: {t}.",
                f"It was decided on {dstr} to proceed with {t}.",
            ],
        }
    elif typ == "treatment_start":
        tmpl = extra.get("treat_start_tmpl")
        if tmpl:
            return _clean_date_dots(tmpl.format(d=dstr))
        opts = {
            "fi": [f"Hoito aloitettu {dstr}."],
            "sv": [f"Behandling påbörjad {dstr}."],
            "en": [f"Treatment started on {dstr}."],
        }
    else:
        raise ValueError(typ)
    return _clean_date_dots(rng.choice(opts[lang]))


def finding_sentence(lang: str, finding: str) -> str:
    return {
        "fi": f"Kuvauksessa todettiin {finding}.",
        "sv": f"Bildfynd: {finding}.",
        "en": f"Imaging showed {finding}.",
    }[lang]


def distractors(lang: str, birth: date, rng: random.Random, n: int) -> list[str]:
    old = date(rng.randint(2012, 2024), rng.randint(1, 12), rng.randint(1, 28))
    old2 = date(rng.randint(2010, 2023), rng.randint(1, 12), rng.randint(1, 28))
    bd = f"{birth.day}.{birth.month}.{birth.year}"
    od = f"{old.day}.{old.month}.{old.year}"
    od2 = f"{old2.day}.{old2.month}.{old2.year}"
    pool = {
        "fi": [
            f"Syntymäaika {bd} tarkistettu väestötiedoista.",
            f"Sappirakon poisto tehty {od} (ei liity nykyiseen selvittelyyn).",
            f"Edellinen keuhkokuume hoidettu {od2}.",
            f"Lonkkaproteesi operoitu {od}.",
            f"Kontrollilaboratoriokokeet tilattu, vastaukset eivät ole tässä kirjauksessa.",
            f"Potilas tupakoinut aiemmin; vieroitusohjaus annettu.",
        ],
        "sv": [
            f"Födelsedatum {bd} kontrollerat i befolkningsuppgifterna.",
            f"Gallblåsan opererades bort {od} (ej relaterat till nuvarande utredning).",
            f"Föregående pneumoni behandlad {od2}.",
            f"Höftprotes opererad {od}.",
            f"Kontrollprov har beställts; svaren finns inte i denna anteckning.",
        ],
        "en": [
            f"Date of birth {bd} confirmed from the population register.",
            f"Cholecystectomy performed on {od} (unrelated to the present work-up).",
            f"Previous pneumonia treated on {od2}.",
            f"Hip replacement on {od}.",
            f"Laboratory tests have been ordered; results are not in this note.",
        ],
    }[lang]
    rng.shuffle(pool)
    return pool[:n]


def negation_sentences(lang: str, note: date, rng: random.Random) -> list[str]:
    """Planned or cancelled events — must NOT be labelled as done."""
    future = note + timedelta(days=rng.randint(3, 14))
    fut = f"{future.day}.{future.month}.{future.year}"
    pool = {
        "fi": [
            f"TT suunniteltu {fut} (ei vielä tehty).",
            "Biopsia peruttiin potilaan toiveesta.",
            "Bronkoskopiaa ei tehty tässä käynnissä.",
            "MDT siirtyy ensi viikkoon, kokousta ei pidetty tänään.",
            "Hoitoa ei ole aloitettu.",
            f"PET-TT varattu {fut}, tutkimus on vasta suunnitelmissa.",
        ],
        "sv": [
            f"DT planerad {fut} (ännu inte utförd).",
            "Biopsin ställdes in på patientens önskan.",
            "Bronkoskopi utfördes inte vid detta besök.",
            "MDK flyttas till nästa vecka; ingen konferens hölls idag.",
            "Behandling har inte påbörjats.",
        ],
        "en": [
            f"CT planned for {fut} (not yet performed).",
            "The biopsy was cancelled at the patient's request.",
            "Bronchoscopy was not performed at this visit.",
            "The MDT is postponed; no meeting was held today.",
            "Treatment has not been started.",
            f"PET-CT booked for {fut}, still only planned.",
        ],
    }[lang]
    rng.shuffle(pool)
    return pool


def closing(lang: str, rng: random.Random) -> str:
    return {
        "fi": "\nKirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.\n",
        "sv": "\nAntecknat av: syntetisk testanvändare. Detta är inte en verklig journal.\n",
        "en": "\nEntered by: synthetic test user. This is not a real clinical record.\n",
    }[lang]


def planned_offsets(archetype: str, rng: random.Random) -> dict:
    """Return event_type -> days after referral (None = event absent). Referral is day 0 if present."""
    ev = {t: None for t in EVENT_TYPES}

    def mid(a, b):
        return rng.randint(a, b)

    if archetype == "no_referral":
        ev["ct_done"] = mid(0, 5)
        ev["biopsy_done"] = ev["ct_done"] + mid(3, 10)
        ev["pathology_result"] = ev["biopsy_done"] + mid(4, 10)
        ev["mdt_decision"] = ev["pathology_result"] + mid(2, 8)
        return ev

    ev["referral_received"] = 0
    ev["ct_done"] = mid(3, 16)

    if archetype in ("mid", "telegram") and rng.random() < 0.4:
        # stop after CT or biopsy
        if rng.random() < 0.5:
            ev["biopsy_done"] = ev["ct_done"] + mid(3, 12)
        return ev

    ev["biopsy_done"] = ev["ct_done"] + mid(3, 12)
    ev["pathology_result"] = ev["biopsy_done"] + mid(3, 12)

    if archetype == "mid" and rng.random() < 0.5:
        ev["mdt_decision"] = ev["pathology_result"] + mid(2, 8)
        return ev

    ev["mdt_decision"] = ev["pathology_result"] + mid(2, 8)
    ev["treatment_decision"] = ev["mdt_decision"] + mid(0, 3)

    if archetype == "late_wait":
        return ev  # no treatment start; clock will be pushed later
    if archetype == "boundary_alert_28":
        return ev

    if archetype == "early_treated":
        ev["treatment_start"] = mid(12, 20)
        if ev["treatment_start"] <= ev["treatment_decision"]:
            ev["treatment_start"] = ev["treatment_decision"] + mid(5, 10)
            if ev["treatment_start"] > 20:
                # shift earlier events back so start can stay <= 20
                ev["treatment_start"] = 18
                ev["treatment_decision"] = min(ev["treatment_decision"], 10)
                ev["mdt_decision"] = min(ev["mdt_decision"], ev["treatment_decision"])
        return ev
    if archetype == "boundary_treated_28":
        ev["treatment_start"] = 28
        if ev["treatment_decision"] >= 28:
            ev["treatment_decision"] = 21
            ev["mdt_decision"] = min(ev["mdt_decision"], 21)
        return ev
    if archetype == "boundary_29":
        ev["treatment_start"] = 29
        if ev["treatment_decision"] >= 29:
            ev["treatment_decision"] = 22
        return ev

    # default complete / typo / relative / mixed / etc.
    if rng.random() < 0.7 or archetype in ("complete_treated", "complete_7", "distractor"):
        ev["treatment_start"] = ev["treatment_decision"] + mid(7, 24)
    return ev


# Map primary event -> default document type that first reports it
PRIMARY_DOC = {
    "referral_received": "referral_letter",
    "ct_done": "ct_report",
    "biopsy_done": "biopsy_note",
    "pathology_result": "pathology_report",
    "mdt_decision": "mdt_minutes",
    "treatment_decision": "oncology_note",
    "treatment_start": "discharge_summary",
}


TARGET_DOCS = {
    "complete_treated": 5,
    "mid": 5,
    "late_wait": 4,
    "early_treated": 5,
    "complete_7": 6,
    "no_referral": 4,
    "relative_only": 5,
    "typo_heavy": 5,
    "negation": 5,
    "conflicting": 5,
    "mixed": 5,
    "distractor": 6,
    "telegram": 4,
    "cancelled": 4,
    "boundary_alert_28": 5,
    "boundary_treated_28": 5,
    "boundary_29": 5,
}


def _history_for(introduce, dates, present, rng, heavy=False):
    earlier = []
    intro_dates = [dates[t] for t in introduce if t in dates]
    cutoff = min(intro_dates) if intro_dates else None
    for e in present:
        if e in introduce or e not in dates:
            continue
        if cutoff is not None and dates[e] < cutoff:
            earlier.append(e)
    if not earlier:
        return []
    if heavy or rng.random() < 0.6:
        return earlier
    # sometimes only a subset
    k = rng.randint(1, len(earlier))
    return earlier[:k]


def merge_docs(docs: list[dict], target: int, rng: random.Random) -> list[dict]:
    docs = sorted(docs, key=lambda d: d["note_date"])
    while len(docs) > target:
        i = rng.randrange(0, len(docs) - 1)
        a, b = docs[i], docs[i + 1]
        b["introduce"] = list(dict.fromkeys(a["introduce"] + b["introduce"]))
        hist = list(dict.fromkeys(a["history"] + b["history"]))
        b["history"] = [h for h in hist if h not in b["introduce"]]
        # keep the later document_type (more downstream)
        extras = dict(a.get("extras") or {})
        extras.update(b.get("extras") or {})
        b["extras"] = extras
        docs.pop(i)
    return docs


def pad_docs(docs: list[dict], target: int, dates: dict, present: list, rng: random.Random) -> list[dict]:
    docs = sorted(docs, key=lambda d: d["note_date"])
    while len(docs) < target:
        last = docs[-1]["note_date"] if docs else list(dates.values())[0]
        note = last + timedelta(days=rng.randint(2, 6))
        docs.append({
            "document_type": "oncology_note",
            "note_date": note,
            "introduce": [],
            "history": list(present),
            "extras": {"wait_note": True},
        })
    return docs


def plan_documents_for_patient(p: dict, rng: random.Random) -> list[dict]:
    """Create a document plan packed to a per-archetype target count (~600 docs overall)."""
    arch = p["archetype"]
    referral_anchor = p["anchor_date"]
    ev_days = p["event_days"]
    dates = {}
    for t, off in ev_days.items():
        if off is not None:
            dates[t] = referral_anchor + timedelta(days=off)

    present = [t for t in EVENT_TYPES if t in dates]
    docs: list[dict] = []

    def add_doc(dtype, note, introduce, history=None, extras=None):
        docs.append({
            "document_type": dtype,
            "note_date": note,
            "introduce": list(introduce),
            "history": list(history or []),
            "extras": extras or {},
        })

    for t in present:
        dtype = PRIMARY_DOC[t]
        delay = rng.randint(0, 2)
        note = dates[t] + timedelta(days=delay)
        history = _history_for([t], dates, present, rng, heavy=(arch == "distractor"))
        add_doc(dtype, note, [t], history)

    if arch in ("late_wait", "boundary_alert_28") and p.get("clock_offset") is not None:
        last_evt = max(dates.values())
        note = referral_anchor + timedelta(days=p["clock_offset"])
        if note <= last_evt:
            note = last_evt + timedelta(days=3)
        add_doc("oncology_note", note, [], present, {"wait_note": True})

    if arch == "cancelled" and "biopsy_done" in dates:
        cancel_note = dates["biopsy_done"] - timedelta(days=rng.randint(4, 8))
        if "ct_done" in dates and cancel_note <= dates["ct_done"]:
            cancel_note = dates["ct_done"] + timedelta(days=1)
        add_doc("biopsy_note", cancel_note, [], [e for e in present if dates[e] < cancel_note], {"cancelled_biopsy": True})

    if arch == "conflicting" and "ct_done" in dates:
        shift = rng.choice([-2, 2, 3])
        wrong = dates["ct_done"] + timedelta(days=shift)
        later = max(d["note_date"] for d in docs) + timedelta(days=1)
        add_doc("oncology_note", later, [], [e for e in present if e != "ct_done"], {"conflict_ct": wrong})

    target = TARGET_DOCS[arch]
    if arch == "mid" and p.get("extra_doc"):
        target += 1
    # One patient bumped to make the corpus exactly 600 (see pad of SYN last complete_7).
    if p.get("plus_one"):
        target += 1

    docs = merge_docs(docs, target, rng)
    docs = pad_docs(docs, target, dates, present, rng)

    if arch == "telegram":
        for d in docs:
            d["extras"]["telegram"] = True
    if arch == "relative_only":
        for d in docs:
            d["extras"]["prefer_relative"] = True
    if arch == "typo_heavy":
        for d in docs:
            d["extras"]["typo_rate"] = 0.28
    if arch == "negation":
        for d in docs:
            d["extras"]["force_negations"] = True
    if arch == "distractor":
        for d in docs:
            if d["document_type"] in ("discharge_summary", "oncology_note"):
                d["extras"]["heavy_distractors"] = True

    docs.sort(key=lambda d: d["note_date"])
    if arch == "boundary_alert_28" and "referral_received" in dates:
        day28 = dates["referral_received"] + timedelta(days=28)
        for d in docs:
            if d["note_date"] > day28:
                d["note_date"] = day28
        # guarantee a note dated exactly day 28
        if not any(d["note_date"] == day28 for d in docs):
            docs[-1]["note_date"] = day28
            docs[-1]["extras"]["wait_note"] = True
        docs.sort(key=lambda d: d["note_date"])
    assert len(docs) == target, (arch, len(docs), target)
    return docs, dates


def plan_corpus(rng: random.Random) -> list[dict]:
    archetypes = (
        ["complete_treated"] * 30
        + ["mid"] * 20
        + ["late_wait"] * 12
        + ["early_treated"] * 8
        + ["complete_7"] * 6
        + ["no_referral"] * 5
        + ["relative_only"] * 5
        + ["typo_heavy"] * 4
        + ["negation"] * 4
        + ["conflicting"] * 4
        + ["mixed"] * 4
        + ["distractor"] * 3
        + ["telegram"] * 3
        + ["cancelled"] * 4
        + ["boundary_alert_28"] * 2
        + ["boundary_treated_28"] * 2
        + ["boundary_29"] * 2
        # 30+20+12+8+6+5+5+4+4+4+4+3+3+4+2+2+2 = 118; add 2 complete
        + ["complete_treated"] * 2
    )
    assert len(archetypes) == 120, len(archetypes)
    # 14 of the mid patients get an extra oncology doc
    mid_extra = set()
    mid_idx = [i for i, a in enumerate(archetypes) if a == "mid"]
    rng.shuffle(mid_idx)
    mid_extra.update(mid_idx[:14])

    patients = []
    for i, arch in enumerate(archetypes):
        pid = f"SYN-P{i+1:04d}"
        name, sex, name_lang = NAMES[i % len(NAMES)]
        # unique-ish invented surname tag
        name = f"{name} {pid}"
        birth = date(rng.randint(1938, 1968), rng.randint(1, 12), rng.randint(1, 28))
        ev_days = planned_offsets(arch, rng)
        if arch == "no_referral":
            anchor = date(2026, rng.randint(2, 8), rng.randint(1, 28))
        else:
            anchor = date(2026, rng.randint(1, 8), rng.randint(1, 28))
        if arch in ("late_wait",):
            clock_offset = rng.randint(32, 70)
        elif arch == "boundary_alert_28":
            clock_offset = 28
        else:
            clock_offset = None
        p = {
            "patient_id": pid,
            "display_name": name,
            "sex": sex,
            "birth_date": iso(birth),
            "name_lang": name_lang,
            "archetype": arch,
            "anchor_date": anchor,
            "event_days": ev_days,
            "clock_offset": clock_offset,
            "extra_doc": i in mid_extra,
            "plus_one": (arch == "complete_7" and not any(x.get("plus_one") for x in patients)),
            "hard_tags": [arch] if arch not in ("complete_treated", "mid", "complete_7", "early_treated") else [],
        }
        doc_plan, dates = plan_documents_for_patient(p, rng)
        p["doc_plan"] = doc_plan
        p["event_dates"] = {k: iso(v) for k, v in dates.items()}
        patients.append(p)
    return patients


def assign_languages(patients: list[dict], rng: random.Random) -> None:
    docs = [(pi, di) for pi, p in enumerate(patients) for di, _ in enumerate(p["doc_plan"])]
    n = len(docs)
    n_fi = int(round(n * 0.75))
    n_sv = int(round(n * 0.15))
    n_en = n - n_fi - n_sv
    langs = ["fi"] * n_fi + ["sv"] * n_sv + ["en"] * n_en
    assert len(langs) == n

    # Prefer mixing within a patient: assign sequentially per patient with a shuffle of a quota bag.
    rng.shuffle(langs)
    # Reorder assignment: first give each patient a primary lang (weighted fi), then leftover bag.
    # Simpler reliable quota: shuffle docs but pick one doc per mixed patient first from sv/en.
    for p in patients:
        p["_primary_lang"] = "fi"
    # 18 primary sv, 12 primary en patients, rest fi — then bump mix
    idx = list(range(len(patients)))
    rng.shuffle(idx)
    for j in idx[:18]:
        patients[j]["_primary_lang"] = "sv"
    for j in idx[18:30]:
        patients[j]["_primary_lang"] = "en"

    # First pass: all docs get primary lang
    for p in patients:
        for d in p["doc_plan"]:
            d["lang"] = p["_primary_lang"]
        if p["archetype"] == "mixed" or rng.random() < 0.45:
            p["_want_mix"] = True
        else:
            p["_want_mix"] = p["archetype"] == "mixed"

    # Count and convert docs to hit quota
    def counts():
        c = Counter(d["lang"] for p in patients for d in p["doc_plan"])
        return c

    # Convert some fi docs to sv/en and vice versa to hit exact quotas, preferring mix patients
    target = {"fi": n_fi, "sv": n_sv, "en": n_en}
    c = counts()
    # flatten list of doc refs
    refs = [(p, d) for p in patients for d in p["doc_plan"]]
    rng.shuffle(refs)
    for need_lang, need_n in target.items():
        while c[need_lang] < need_n:
            # take from the most overrepresented
            over = max((l for l in ("fi", "sv", "en") if c[l] > target[l]), key=lambda l: c[l] - target[l], default=None)
            if not over:
                break
            for p, d in refs:
                if d["lang"] == over:
                    # keep at least one primary-lang doc if possible
                    same = sum(1 for x in p["doc_plan"] if x["lang"] == over)
                    if same <= 1 and p["_primary_lang"] == over and len(p["doc_plan"]) > 1:
                        continue
                    d["lang"] = need_lang
                    c[over] -= 1
                    c[need_lang] += 1
                    break
            else:
                break
    # Force mixed archetype to have >=2 langs when they have >=2 docs
    for p in patients:
        if p["archetype"] == "mixed" and len(p["doc_plan"]) >= 2:
            langs_here = {d["lang"] for d in p["doc_plan"]}
            if len(langs_here) == 1:
                p["doc_plan"][-1]["lang"] = "sv" if p["doc_plan"][0]["lang"] != "sv" else "en"

    # Spread minority languages across patients (keep global counts) so more patients are mixed.
    def patient_langs(p):
        return {d["lang"] for d in p["doc_plan"]}
    mono_fi = [p for p in patients if patient_langs(p) == {"fi"} and len(p["doc_plan"]) >= 2]
    minority = []
    for p in patients:
        for d in p["doc_plan"]:
            if d["lang"] in ("sv", "en"):
                minority.append((p, d))
    rng.shuffle(mono_fi)
    rng.shuffle(minority)
    # Swap one minority doc into many fi-only patients, taking a fi doc back.
    used_docs = set()
    for p_fi, (p_src, d_src) in zip(mono_fi, minority):
        if id(d_src) in used_docs:
            continue
        # don't un-mix a mixed-archetype patient down to 1 lang
        src_langs = patient_langs(p_src)
        if p_src is p_fi:
            continue
        if p_src["archetype"] == "mixed" and len(src_langs) == 2:
            # only swap if src still has another minority or another doc in same lang
            if sum(1 for d in p_src["doc_plan"] if d["lang"] == d_src["lang"]) < 2 and len(src_langs) <= 2:
                continue
        fi_doc = next((d for d in p_fi["doc_plan"] if d["lang"] == "fi"), None)
        if not fi_doc:
            continue
        d_src["lang"], fi_doc["lang"] = fi_doc["lang"], d_src["lang"]
        used_docs.add(id(d_src))


def render_document(p: dict, dplan: dict, rng: random.Random) -> tuple[str, list[dict], dict]:
    lang = dplan["lang"]
    note: date = dplan["note_date"]
    typo_rate = dplan.get("extras", {}).get("typo_rate", 0.0)
    # mild typo chance even on normal docs
    if typo_rate == 0 and rng.random() < 0.35:
        typo_rate = 0.06
    prefer_rel = dplan.get("extras", {}).get("prefer_relative", False)
    hospital = rng.choice(HOSPITALS[lang])
    finding = rng.choice(FINDINGS[lang])
    histo = rng.choice(HISTO[lang])
    treat = rng.choice(TREATMENTS[lang])
    extra = {
        "finding": finding,
        "histo": histo,
        "treat_phrase": treat[1],
        "treat_start_tmpl": treat[2],
    }
    birth = date.fromisoformat(p["birth_date"])
    pid = p["patient_id"]
    name = p["display_name"]

    event_dates = {k: date.fromisoformat(v) for k, v in p["event_dates"].items()}
    b = Builder()
    telegram = dplan.get("extras", {}).get("telegram", False)

    b.add(salutation(lang, name, pid, hospital, note, birth, rng))

    if not telegram:
        intro = {
            "fi": "Käynnin syy: keuhkosyöpäepäilyn selvittely (synteettinen esimerkki).\n",
            "sv": "Besöksorsak: utredning av misstänkt lungcancer (syntetiskt exempel).\n",
            "en": "Reason for visit: work-up of suspected lung cancer (synthetic example).\n",
        }[lang]
        b.add(intro)

    # History (accurate copy-paste) — labelled
    for typ in dplan["history"]:
        if typ not in event_dates:
            continue
        ed = event_dates[typ]
        dstr = format_date(ed, note, lang, rng, prefer_rel)
        sent = event_sentence(typ, dstr, lang, rng, extra)
        if not sent.endswith("\n"):
            sent = sent + "\n"
        prefix = {
            "fi": "Esitiedot: ",
            "sv": "Föregående uppgifter: ",
            "en": "History: ",
        }[lang]
        # only prefix some history lines
        line = (prefix + sent[0].lower() + sent[1:]) if (not telegram and rng.random() < 0.4) else sent
        b.add_event(typ, ed, line)

    # Conflicting later CT — introduce a ct_done with the wrong/shifted date (doc-level gold)
    if dplan.get("extras", {}).get("conflict_ct"):
        wrong = dplan["extras"]["conflict_ct"]
        dstr = format_date(wrong, note, lang, rng, prefer_rel)
        sent = event_sentence("ct_done", dstr, lang, rng, extra)
        if not sent.endswith("\n"):
            sent += "\n"
        b.add_event("ct_done", wrong, sent)

    # Primary / introduced events
    for typ in dplan["introduce"]:
        ed = event_dates[typ]
        dstr = format_date(ed, note, lang, rng, prefer_rel)
        sent = event_sentence(typ, dstr, lang, rng, extra)
        if typ == "ct_done" and not telegram:
            sent = sent + " " + finding_sentence(lang, finding)
        if not sent.endswith("\n"):
            sent += "\n"
        b.add_event(typ, ed, sent)

    # Negations / plans (not gold)
    force_neg = dplan.get("extras", {}).get("force_negations") or dplan.get("extras", {}).get("cancelled_biopsy")
    if dplan.get("extras", {}).get("cancelled_biopsy"):
        cancel = {
            "fi": "Biopsia peruttiin potilaan toiveesta; toimenpidettä ei tehty.\n",
            "sv": "Biopsin ställdes in på patientens önskan; åtgärden utfördes inte.\n",
            "en": "The biopsy was cancelled at the patient's request; the procedure was not done.\n",
        }[lang]
        b.add(cancel)
    n_neg = 2 if force_neg else (0 if telegram else (1 if rng.random() < 0.4 else 0))
    if n_neg:
        for s in negation_sentences(lang, note, rng)[:n_neg]:
            b.add(s + "\n")

    # Wait note flavour
    if dplan.get("extras", {}).get("wait_note"):
        wait = {
            "fi": "Odotetaan jatkotoimia. Hoitoa ei ole aloitettu tässä vaiheessa.\n",
            "sv": "Inväntar nästa steg. Behandling har inte påbörjats i detta skede.\n",
            "en": "Awaiting next steps. Treatment has not been started at this stage.\n",
        }[lang]
        b.add(wait)

    # Distractors
    n_dist = 3 if dplan.get("extras", {}).get("heavy_distractors") or p["archetype"] == "distractor" else (0 if telegram else rng.randint(1, 2))
    if dplan["document_type"] == "discharge_summary":
        n_dist = max(n_dist, 2)
    for s in distractors(lang, birth, rng, n_dist):
        b.add(s + "\n")

    if not telegram:
        b.add(closing(lang, rng))
    else:
        b.add({
            "fi": "\n(Synteettinen lyhyt kirjaus.)\n",
            "sv": "\n(Syntetisk kort anteckning.)\n",
            "en": "\n(Synthetic short note.)\n",
        }[lang])

    body, gold = b.render(rng, typo_rate)
    return body, gold, extra


def patient_level_gold(p: dict, documents: list[dict]) -> dict:
    """Merge events: the chronologically latest document that mentions a type wins."""
    # documents must be in any order; use note_date
    latest: dict[str, tuple[date, str]] = {}
    for doc in sorted(documents, key=lambda x: x["note_date"]):
        nd = date.fromisoformat(doc["note_date"])
        for ev in doc["events"]:
            latest[ev["type"]] = (date.fromisoformat(ev["date"]), doc["document_id"])
    merged = {t: iso(latest[t][0]) for t in EVENT_TYPES if t in latest}
    sources = {t: latest[t][1] for t in merged}
    clock = max(date.fromisoformat(d["note_date"]) for d in documents)
    ref = date.fromisoformat(merged["referral_received"]) if "referral_received" in merged else None
    start = date.fromisoformat(merged["treatment_start"]) if "treatment_start" in merged else None
    day_count = (clock - ref).days if ref else None
    alert = bool(day_count is not None and day_count >= ALERT_DAY and start is None)
    return {
        "merged_events": merged,
        "merged_event_source_doc": sources,
        "clock_as_of": iso(clock),
        "referral_date": iso(ref) if ref else None,
        "treatment_start_date": iso(start) if start else None,
        "day_count": day_count,
        "alert": alert,
        "merge_rule": "latest_document_wins",
        "alert_rule": f"day_count >= {ALERT_DAY} and no treatment_start",
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, default=SEED_DEFAULT)
    ap.add_argument("--out", type=Path, default=Path(__file__).parent / "data")
    args = ap.parse_args()
    rng = random.Random(args.seed)

    patients_plan = plan_corpus(rng)
    assign_languages(patients_plan, rng)

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

    for p in patients_plan:
        pid = p["patient_id"]
        rendered_docs = []
        for i, dplan in enumerate(p["doc_plan"], start=1):
            # ensure note_date is a date
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
            body, gold, _extra = render_document(p, dplan, rng)
            text = header(meta) + body
            # re-validate spans after header prepend: spans are in body, still in text
            for g in gold:
                if g["evidence_span"] not in text:
                    raise AssertionError(f"{doc_id}: span lost after header: {g}")
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
            }
            all_docs.append(rec)
            rendered_docs.append(rec)
            lang_counts[dplan["lang"]] += 1
            type_counts[dplan["document_type"]] += 1
            for g in gold:
                event_counts[g["type"]] += 1

        pl = patient_level_gold(p, rendered_docs)
        patients_out.append({
            "patient_id": pid,
            "display_name": p["display_name"],
            "sex": p["sex"],
            "birth_date": p["birth_date"],
            "archetype": p["archetype"],
            "hard_tags": p["hard_tags"],
            "document_ids": [d["document_id"] for d in rendered_docs],
            "synthetic": True,
            **pl,
        })

    n = len(all_docs)
    stats = {
        "corpus_id": CORPUS_ID,
        "synthetic": True,
        "seed": args.seed,
        "n_documents": n,
        "n_patients": len(patients_out),
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
    }

    gold = {
        "corpus_id": CORPUS_ID,
        "synthetic": True,
        "seed": args.seed,
        "event_types": EVENT_TYPES,
        "documents": {d["document_id"]: {"events": d["events"], "note_date": d["note_date"], "patient_id": d["patient_id"]} for d in all_docs},
        "patients": {p["patient_id"]: p for p in patients_out},
    }

    (out / "documents.jsonl").write_text(
        "\n".join(json.dumps(d, ensure_ascii=False) for d in all_docs) + "\n",
        encoding="utf-8",
    )
    (out / "patients.json").write_text(json.dumps(patients_out, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "gold.json").write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "stats.json").write_text(json.dumps(stats, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "manifest.json").write_text(json.dumps({
        "corpus_id": CORPUS_ID,
        "synthetic": True,
        "seed": args.seed,
        "documents": [{k: d[k] for k in ("document_id", "patient_id", "document_type", "lang", "note_date", "path")} for d in all_docs],
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(json.dumps(stats, ensure_ascii=False, indent=2))
    if n < 580 or n > 620:
        print(f"WARNING: expected ~600 documents, got {n}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
