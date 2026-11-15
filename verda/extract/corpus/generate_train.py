#!/usr/bin/env python3
"""SYNTHETIC train corpus for LoRA — disjoint from v2 dev/test template families.

IDs: SYNTR-P* / corpus_id tasan-extract-synthetic-train
Seed: 20261190
Never reads or copies corpus/data_v2/. Phrase banks are new (see LEAKAGE.md).
"""
from __future__ import annotations

import json
import random
from datetime import date, timedelta
from pathlib import Path

EVENT_TYPES = [
    "referral_received", "ct_done", "biopsy_done", "pathology_result",
    "mdt_decision", "treatment_decision", "treatment_start",
]
FI_MONTH = ["tammikuuta","helmikuuta","maaliskuuta","huhtikuuta","toukokuuta","kesäkuuta",
            "heinäkuuta","elokuuta","syyskuuta","lokakuuta","marraskuuta","joulukuuta"]
SV_MONTH = ["januari","februari","mars","april","maj","juni","juli","augusti","september","oktober","november","december"]
EN_MONTH = ["January","February","March","April","May","June","July","August","September","October","November","December"]
FI_WD = ["ma","ti","ke","to","pe","la","su"]
NAMES = {
    "fi": [("Aino", "Harjoitus"), ("Matti", "Mallinen"), ("Eeva", "Esimerkki")],
    "sv": [("Anna", "Testsson"), ("Erik", "Exempel")],
    "en": [("Jane", "Synthetic"), ("John", "Placeholder")],
}

# Banned v2 family anchors (unit-checked at the end).
BANNED = [
    "Konsultaatiopyyntö kirjattiin saapuneeksi",
    "Lähete saapui toimistoon",
    "Asiakirja merkittiin saapuneeksi keuhkoyksikköön",
    "Pyyntö tuli perille",
    "Kerroskuvaus toteutettiin",
    "Leikekuvaus on suoritettu",
    "Tutkimus käytiin kuvaamassa",
    "Konsultationsbegäran registrerades som inkommen",
    "The consultation request was logged as having arrived",
    "Cross-sectional imaging was carried out",
    "Tiimikokous pidettiin",
    "viikolla ",  # v2 ISO-week surface form
    "vecka ",
    "in week ",
]


def fmt_date(d: date, lang: str, rng: random.Random, note: date) -> str:
    styles = ["dotted", "dotted", "spelled", "iso", "short_wd"]
    style = rng.choice(styles)
    if style == "dotted":
        return f"{d.day}.{d.month}.{d.year}"
    if style == "iso":
        return d.isoformat()
    if style == "short_wd":
        return f"{FI_WD[d.weekday()] if lang=='fi' else d.strftime('%a')} {d.day}.{d.month}.{d.year}"
    if lang == "fi":
        return f"{d.day}. {FI_MONTH[d.month-1]} {d.year}"
    if lang == "sv":
        return f"den {d.day} {SV_MONTH[d.month-1]} {d.year}"
    return f"{d.day} {EN_MONTH[d.month-1]} {d.year}"


def sentence(typ: str, ds: str, lang: str, rng: random.Random, extra: dict) -> str:
    h = extra.get("histo", {"fi": "adenokarsinooma", "sv": "adenokarcinom", "en": "adenocarcinoma"}[lang])
    tr = extra.get("treat", {"fi": "lobektomia", "sv": "lobektomi", "en": "lobectomy"}[lang])
    bank = {
        "referral_received": {
            "fi": [f"Saapumispäivä merkitty potilastietojärjestelmään {ds}.",
                   f"Lähetemerkintä avattiin {ds}.",
                   f"Yksikkö otti läheteen käsittelyyn {ds}."],
            "sv": [f"Ankomstdatum slogs in i journalen {ds}.",
                   f"Enheten öppnade remissen {ds}."],
            "en": [f"Arrival was entered into the record on {ds}.",
                   f"The unit opened the referral on {ds}."],
        },
        "ct_done": {
            "fi": [f"Keuhkojen viipalekuvaus tehtiin {ds}.",
                   f"TT-sarja tallennettiin {ds}.",
                   f"Kuvausprotokolla ajettiin {ds}."],
            "sv": [f"Lungornas snittbilder togs {ds}.",
                   f"DT-serien sparades {ds}."],
            "en": [f"The chest slice series was acquired on {ds}.",
                   f"The tomographic acquisition was stored on {ds}."],
        },
        "biopsy_done": {
            "fi": [f"Näytteenotto tähystyksellä {ds}.",
                   f"Kudospala irrotettiin toimenpiteessä {ds}."],
            "sv": [f"Provtagning via spegling {ds}.",
                   f"Vävnadsbit togs vid åtgärd {ds}."],
            "en": [f"An endoscopic sample was taken on {ds}.",
                   f"A tissue fragment was removed at the procedure on {ds}."],
        },
        "pathology_result": {
            "fi": [f"Patologian tulos kirjattiin {ds} ({h}).",
                   f"Kudosanalyysi valmistui {ds}: {h}."],
            "sv": [f"Patologisvar antecknades {ds} ({h})."],
            "en": [f"Pathology was filed on {ds} ({h})."],
        },
        "mdt_decision": {
            "fi": [f"Moniammatillinen linjapalaveri {ds}; suositus kirjattu.",
                   f"Hoitoryhmä kokoontui {ds}."],
            "sv": [f"Vårdteamet samlades {ds} och antecknade rekommendationen."],
            "en": [f"The care team met on {ds} and recorded a recommendation."],
        },
        "treatment_decision": {
            "fi": [f"Hoidon valinta vahvistettiin {ds}: {tr}.",
                   f"Linja lukittiin {ds} ({tr})."],
            "sv": [f"Behandlingsvalet bekräftades {ds}: {tr}."],
            "en": [f"The treatment choice was confirmed on {ds}: {tr}."],
        },
        "treatment_start": {
            "fi": [f"Hoito käynnistyi {ds} ({tr}).",
                   f"Ensimmäinen hoitotoimi tehtiin {ds}."],
            "sv": [f"Behandlingen inleddes {ds} ({tr})."],
            "en": [f"Treatment commenced on {ds} ({tr})."],
        },
    }
    return rng.choice(bank[typ][lang])


def header(meta: dict) -> str:
    return (
        "==============================================================================\n"
        "SYNTHETIC DOCUMENT — NOT A REAL PATIENT — Tasan Extract train corpus. "
        "No real personal data. All names, dates and findings are invented.\n"
        f"corpus_id: {meta['corpus_id']}\n"
        f"patient_id: {meta['patient_id']}\n"
        f"document_id: {meta['document_id']}\n"
        f"document_type: {meta['document_type']}\n"
        f"language: {meta['lang']}\n"
        f"note_date: {meta['note_date']}\n"
        f"display_name: {meta['display_name']} (invented)\n"
        "DO NOT treat this text as a clinical record. Train split; disjoint from v2 eval families.\n"
        "==============================================================================\n"
    )


def main() -> None:
    out = Path(__file__).resolve().parent / "data_train"
    rng = random.Random(20261190)
    out.mkdir(parents=True, exist_ok=True)
    (out / "documents").mkdir(exist_ok=True)
    docs = []
    patients = []
    gold_docs = {}
    n_patients = 80
    for i in range(1, n_patients + 1):
        pid = f"SYNTR-P{i:04d}"
        lang = rng.choices(["fi", "sv", "en"], weights=[0.75, 0.15, 0.10])[0]
        first, last = rng.choice(NAMES[lang])
        display = f"{first} {last} {pid}"
        referral = date(2026, 1, 5) + timedelta(days=rng.randint(0, 200))
        # compact pathway
        ev_dates = {"referral_received": referral}
        cur = referral + timedelta(days=rng.randint(3, 10))
        ev_dates["ct_done"] = cur
        if rng.random() < 0.85:
            cur += timedelta(days=rng.randint(3, 10))
            ev_dates["biopsy_done"] = cur
        if "biopsy_done" in ev_dates and rng.random() < 0.85:
            cur += timedelta(days=rng.randint(4, 12))
            ev_dates["pathology_result"] = cur
        if "pathology_result" in ev_dates and rng.random() < 0.8:
            cur += timedelta(days=rng.randint(2, 8))
            ev_dates["mdt_decision"] = cur
        if "mdt_decision" in ev_dates and rng.random() < 0.8:
            ev_dates["treatment_decision"] = cur + timedelta(days=rng.randint(0, 3))
        if "treatment_decision" in ev_dates and rng.random() < 0.7:
            ev_dates["treatment_start"] = ev_dates["treatment_decision"] + timedelta(days=rng.randint(5, 20))
        extra = {"histo": rng.choice(["adenokarsinooma", "levyepiteelikarsinooma", "NSCLC"] if lang=="fi" else ["adenocarcinoma", "squamous-cell carcinoma"]),
                 "treat": rng.choice(["lobektomia", "sytostaatti", "SBRT"] if lang=="fi" else ["lobectomy", "chemotherapy", "SBRT"])}
        # 3–6 notes along the pathway
        types_order = [t for t in EVENT_TYPES if t in ev_dates]
        doc_types = ["referral_letter", "ct_report", "biopsy_note", "pathology_report", "mdt_minutes", "oncology_note", "discharge_summary"]
        n_docs = min(len(types_order), rng.randint(3, 5))
        cuts = sorted(rng.sample(range(len(types_order)), n_docs))
        doc_ids = []
        for j, cut in enumerate(cuts, 1):
            known = types_order[: cut + 1]
            last_ev = ev_dates[types_order[cut]]
            note = last_ev + timedelta(days=rng.randint(0, 2))
            dtype = doc_types[min(j - 1, len(doc_types) - 1)]
            did = f"{pid}-{dtype}-{j:02d}"
            events = []
            sents = []
            for typ in known:
                ds = fmt_date(ev_dates[typ], lang, rng, note)
                sent = sentence(typ, ds, lang, rng, extra)
                events.append({"type": typ, "date": ev_dates[typ].isoformat(), "evidence_span": sent})
                sents.append(sent)
            body = (
                f"{'Keksitty keuhkoyksikkö' if lang=='fi' else 'Fiktiv lungavdelning' if lang=='sv' else 'Placeholder lung unit'}\n"
                f"{'Kirjauspäivä' if lang=='fi' else 'Anteckningsdatum' if lang=='sv' else 'Note date'} {note.day}.{note.month}.{note.year}. "
                f"{'Potilas' if lang=='fi' else 'Patient'}: {display}, {'s.' if lang!='en' else 'DOB'} 1.1.1950.\n"
                f"{'SYNTEETTINEN' if lang=='fi' else 'SYNTETISK' if lang=='sv' else 'SYNTHETIC'} record, not a real person.\n\n"
                + "\n".join(sents)
                + f"\n\n{'Kirjaaja: synteettinen testikäyttäjä.' if lang=='fi' else 'Antecknat av: syntetisk testanvändare.' if lang=='sv' else 'Entered by: synthetic test user.'}\n"
            )
            meta = {
                "corpus_id": "tasan-extract-synthetic-train",
                "document_id": did,
                "patient_id": pid,
                "document_type": dtype,
                "lang": lang,
                "note_date": note.isoformat(),
                "display_name": display,
                "path": f"documents/{did}.txt",
                "events": events,
                "synthetic": True,
                "split": "train",
            }
            text = header(meta) + body
            for b in BANNED:
                if b.lower() in text.lower():
                    raise SystemExit(f"leakage: banned phrase {b!r} in {did}")
            (out / meta["path"]).write_text(text)
            rec = {k: meta[k] for k in meta}
            rec["n_chars"] = len(text)
            docs.append(rec)
            gold_docs[did] = {"events": events, "note_date": meta["note_date"], "patient_id": pid}
            doc_ids.append(did)
        ref = ev_dates["referral_received"]
        start = ev_dates.get("treatment_start")
        clock = date.fromisoformat(docs[-1]["note_date"])
        day_count = (clock - ref).days
        patients.append({
            "patient_id": pid, "display_name": display, "lang": lang,
            "document_ids": doc_ids, "synthetic": True, "split": "train",
            "merged_events": {k: v.isoformat() for k, v in ev_dates.items()},
            "referral_date": ref.isoformat(),
            "treatment_start_date": start.isoformat() if start else None,
            "day_count": day_count,
            "alert": bool(day_count >= 28 and start is None),
        })
    (out / "documents.jsonl").write_text("\n".join(json.dumps(d, ensure_ascii=False) for d in docs) + "\n")
    gold = {"corpus_id": "tasan-extract-synthetic-train", "synthetic": True, "seed": 20261190,
            "event_types": EVENT_TYPES, "documents": gold_docs,
            "patients": {p["patient_id"]: p for p in patients}}
    (out / "gold.json").write_text(json.dumps(gold, ensure_ascii=False, indent=2) + "\n")
    (out / "manifest.json").write_text(json.dumps({
        "corpus_id": "tasan-extract-synthetic-train", "synthetic": True, "seed": 20261190,
        "documents": [{k: d[k] for k in ("document_id","patient_id","document_type","lang","note_date","path","split")} for d in docs],
    }, ensure_ascii=False, indent=2) + "\n")
    # instruction jsonl for LoRA
    system = (Path(__file__).resolve().parents[1] / "prompt" / "system.txt").read_text()
    user_tmpl = (Path(__file__).resolve().parents[1] / "prompt" / "user_template.txt").read_text()
    rows = []
    for d in docs:
        text = (out / d["path"]).read_text()
        user = user_tmpl.format(note_date=d["note_date"], lang=d["lang"], text=text)
        assistant = json.dumps({
            "events": [
                {"type": e["type"], "date": e["date"], "date_text": None,
                 "evidence_span": e["evidence_span"], "confidence": 1.0}
                for e in d["events"]
            ]
        }, ensure_ascii=False)
        rows.append({"messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user + "\n\n/no_think\n"},
            {"role": "assistant", "content": assistant},
        ], "document_id": d["document_id"], "synthetic": True, "source": "train_templates"})
    (out / "train_sft.jsonl").write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n")
    (out / "LEAKAGE.md").write_text(
        "# Train / eval leakage controls\n\n"
        "This train corpus (`tasan-extract-synthetic-train`, IDs `SYNTR-P*`, seed 20261190) "
        "is **SYNTHETIC** and is built to stay off the v2 evaluation families.\n\n"
        "- It does **not** read `corpus/data_v2/` or reuse `SYN2-P*` patients.\n"
        "- Sentence banks in `generate_train.py` are new (e.g. *Saapumispäivä merkitty…*, "
        "*Keuhkojen viipalekuvaus tehtiin…*, *Hoitoryhmä kokoontui…*). A banned-substring "
        "check rejects v2 anchors such as *Konsultaatiopyyntö kirjattiin saapuneeksi*, "
        "*Kerroskuvaus toteutettiin*, *Tiimikokous pidettiin*, *viikolla N … (year)*.\n"
        "- Date styles are dotted / ISO / spelled / short weekday+date — not v2's "
        "`viikolla N maanantaina (2026)` form.\n"
        "- A v1 easy subset may be added (optionally GPU-paraphrased) as extra train rows. "
        "v1 templates are already disjoint from v2. v2 **dev and test are never used for training**.\n"
    )
    print(f"train docs={len(docs)} patients={len(patients)} sft={len(rows)} -> {out}")


if __name__ == "__main__":
    main()
