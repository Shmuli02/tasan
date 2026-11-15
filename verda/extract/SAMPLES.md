# Tasan Extract — SYNTHETIC showcase notes

> **SYNTHETIC DOCUMENT — NOT A REAL PATIENT.**
> All names, dates, findings and identifiers in this file are invented.
> Do not treat any of this text as a clinical record.
> Corpus IDs: `tasan-extract-synthetic-v1` (seed 20261114) and
> `tasan-extract-synthetic-v2` (seed 20261142, held-out phrasing).

## How this fake data was generated

These notes were built by the Tasan Extract **template generators** under
`verda/extract/corpus/`. No real EHR, no real person, and no copied clinical
text was used. Each patient is an invented record (`SYN-P*` / `SYN2-P*`) with a
Finnish/Swedish/English display name such as *Aino Synteettinen* or
*Matti Mallipotilas*, a made-up date of birth, and a planned lung-cancer
pathway timeline (referral → CT → biopsy → pathology → MDT → treatment
decision → treatment start). The generator writes the note text and the gold
event dates **together**, so the gold labels are known by construction.

**v1 (easy)** uses relatively regular clinical phrasing the regex baseline
was designed against (for example *ESH-lähete vastaanotettu 8.3.2026*).
It still injects typographical noise, historical distractor dates (old
cholecystectomy, hip replacement), and mixed-language patients.

**v2 (hard, held-out)** is a second corpus with the same event types and gold
dates but **wordings the regex was never tuned on**: consultation request
*written* versus *logged as arrived*, imaging *booked* versus *performed*,
ISO week numbers (*viikolla 34 maanantaina*), relative weekday phrases
(*eilen*, *perjantaina*), dictation artifacts, and split tokens. The official
regex score on v2 is from the **untuned** v1 patterns; the test split was not
used to add keywords. A later GPU paraphrase pass will rewrite a v2 subset
while a date-recoverability check keeps only notes whose gold dates can still
be read from the new wording. A paraphrased sibling of
`SYN2-P0010-referral_letter-01` will be added here after that run.

Every corpus file also carries a SYNTHETIC header with `corpus_id`,
`patient_id`, and `document_id`. The `text` fields in `samples.json` and
`app_export.json` are the **full corpus files** (header + body) so character
offsets stay stable. The excerpts below show the clinical body.

Event dates in this snapshot are **gold** (with char offsets into `text`).
Regex predictions are listed for comparison. After the Finnish GPU run the
same `note_id`s will be filled with Qwen3-32B JSON and `app_export.json`
will be regenerated with `source: "qwen3-32b"`.

This pack contains **10** notes: Finnish, Swedish and English;
referral, CT, bronchoscopy, MDT, typo-heavy, a day-28 alert, and two v2
held-out traps.

## Index

| # | note_id | lang | doc_type | day_count | alert | gold | regex |
|---|---------|------|----------|-----------|-------|------|-------|
| 1 | `SYN-P0002-referral_letter-01` | fi | referral_letter | 0 | False | 1 | 1 |
| 2 | `SYN-P0003-ct_report-02` | fi | ct_report | 5 | False | 2 | 2 |
| 3 | `SYN-P0002-biopsy_note-02` | fi | biopsy_note | 19 | False | 3 | 3 |
| 4 | `SYN-P0001-mdt_minutes-04` | fi | mdt_minutes | 32 | True | 3 | 3 |
| 5 | `SYN-P0002-mdt_minutes-03` | sv | mdt_minutes | 32 | True | 5 | 4 |
| 6 | `SYN-P0001-discharge_summary-05` | en | discharge_summary | 46 | False | 7 | 6 |
| 7 | `SYN-P0087-pathology_report-02` | fi | pathology_report | 34 | True | 4 | 4 |
| 8 | `SYN-P0051-oncology_note-04` | fi | oncology_note | 53 | True | 6 | 6 |
| 9 | `SYN2-P0010-referral_letter-01` | fi | referral_letter | 1 | False | 1 | 0 |
| 10 | `SYN2-P0014-ct_report-02` | fi | ct_report | 15 | False | 2 | 0 |

---

## 1. Finnish referral (v1, easy)

- **note_id:** `SYN-P0002-referral_letter-01`  
- **patient_id:** `SYN-P0002`  
- **lang / doc_type / note_date:** fi / `referral_letter` / 2026-03-08  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 0 / False  
- **patient-level gold clock:** day_count=50, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Keksityn yliopistollinen sairaala
Kirjauspäivä 8.3.2026. Potilas: Matti Mallipotilas SYN-P0002 (SYN-P0002), s. 11.11.1943.
SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.

Käynnin syy: keuhkosyöpäepäilyn selvittely (synteettinen esimerkki).
ESH-lähete vastaanotettu 8.3.2026.
Hoitoa ei ole aloitettu.
Sappirakon poisto tehty 15.2.2015 (ei liity nykyiseen selvittelyyn).
Kontrollilaboratoriokokeet tilattu, vastaukset eivät ole tässä kirjauksessa.

Kirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 804–838 | 1.0 | ESH-lähete vastaanotettu 8.3.2026. |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 804–838 | 0.45 | ESH-lähete vastaanotettu 8.3.2026. |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 804–838 | 0.95 | ESH-lähete vastaanotettu 8.3.2026. |


---

## 2. Finnish CT report (v1, easy)

- **note_id:** `SYN-P0003-ct_report-02`  
- **patient_id:** `SYN-P0003`  
- **lang / doc_type / note_date:** fi / `ct_report` / 2026-04-25  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 5 / False  
- **patient-level gold clock:** day_count=46, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Keksityn yliopistollinen sairaala
Kirjauspäivä 25.4.2026. Potilas: Eeva Esimerkki SYN-P0003 (SYN-P0003), s. 26.8.1948.
SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.

Käynnin syy: keuhkosyöpäepäilyn selvittely (synteettinen esimerkki).
Esitiedot: lähete saapunut keuhkoklinikalle 20.4.2026.
Thoraxin TT tehty 24/4/2026. Kuvauksessa todettiin vasemman alalohkon 2,4 cm muutos.
Lonkkaproteesi operoitu 10.11.2015.

Kirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-04-20 | 784–838 | 1.0 | Esitiedot: lähete saapunut keuhkoklinikalle 20.4.2026. |
| `ct_done` | 2026-04-24 | 839–923 | 1.0 | Thoraxin TT tehty 24/4/2026. Kuvauksessa todettiin vasemman alalohkon 2,4 cm muutos. |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-04-20 | 784–838 | 0.45 | Esitiedot: lähete saapunut keuhkoklinikalle 20.4.2026. |
| `ct_done` | 2026-04-24 | 839–867 | 0.45 | Thoraxin TT tehty 24/4/2026. |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-04-20 | 795–838 | 0.95 | lähete saapunut keuhkoklinikalle 20.4.2026. |
| `ct_done` | 2026-04-24 | 839–867 | 0.95 | Thoraxin TT tehty 24/4/2026. |


---

## 3. Finnish bronchoscopy / biopsy (v1, easy)

- **note_id:** `SYN-P0002-biopsy_note-02`  
- **patient_id:** `SYN-P0002`  
- **lang / doc_type / note_date:** fi / `biopsy_note` / 2026-03-27  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 19 / False  
- **patient-level gold clock:** day_count=50, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Keksityn yliopistollinen sairaala
Kirjauspäivä 27.3.2026. Potilas: Matti Mallipotilas SYN-P0002 (SYN-P0002), s. 11.11.1943.
SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.

Käynnin syy: keuhkosyöpäepäilyn selvittely (synteettinen esimerkki).
Esitiedot: lähete saapunut keuhkoklinikalle 8.3.26.
TT-tutkimus tehty 21/3/2026. Kuvauksessa todettiin vasemman ylälohkon 1,8 cm kyhmy ja välikarsinan imusolmukkeet.
Biopsiat otettu bronkoskopiassa 26.3.2026.
Kontrollilaboratoriokokeet tilattu, vastaukset eivät ole tässä kirjauksessa.
Lonkkaproteesi operoitu 24.8.2022.

Kirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 797–848 | 1.0 | Esitiedot: lähete saapunut keuhkoklinikalle 8.3.26. |
| `ct_done` | 2026-03-21 | 849–962 | 1.0 | TT-tutkimus tehty 21/3/2026. Kuvauksessa todettiin vasemman ylälohkon 1,8 cm kyhmy ja välikarsinan imusolmukkeet. |
| `biopsy_done` | 2026-03-26 | 963–1005 | 1.0 | Biopsiat otettu bronkoskopiassa 26.3.2026. |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 797–848 | 0.45 | Esitiedot: lähete saapunut keuhkoklinikalle 8.3.26. |
| `ct_done` | 2026-03-21 | 849–877 | 0.45 | TT-tutkimus tehty 21/3/2026. |
| `biopsy_done` | 2026-03-26 | 963–1005 | 0.45 | Biopsiat otettu bronkoskopiassa 26.3.2026. |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 808–848 | 0.95 | lähete saapunut keuhkoklinikalle 8.3.26. |
| `ct_done` | 2026-03-21 | 849–877 | 0.95 | TT-tutkimus tehty 21/3/2026. |
| `biopsy_done` | 2026-03-26 | 963–1005 | 0.95 | Biopsiat otettu bronkoskopiassa 26.3.2026. |


---

## 4. Finnish MDT minutes (v1, easy)

- **note_id:** `SYN-P0001-mdt_minutes-04`  
- **patient_id:** `SYN-P0001`  
- **lang / doc_type / note_date:** fi / `mdt_minutes` / 2026-08-17  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 32 / True  
- **patient-level gold clock:** day_count=46, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Keksityn yliopistollinen sairaala
Kirjauspäivä 17.8.2026. Potilas: Aino Synteettinen SYN-P0001 (SYN-P0001), s. 15.4.1945.
SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.

Käynnin syy: keuhkosyöpäepäilyn selvittely (synteettinen esimerkki).
Esitiedot: eSH-lähete vastaanotettu 16.7.26.
Keuhko-TT tehty 21.7.2026.
MDT 16/8: hoitolinja vahvistettu.
Biopsia peruttiin potilaan toiveesta.
Edellinen keuhkokuume hoidettu 20.9.2016.

Kirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-07-16 | 794–838 | 1.0 | Esitiedot: eSH-lähete vastaanotettu 16.7.26. |
| `ct_done` | 2026-07-21 | 839–865 | 1.0 | Keuhko-TT tehty 21.7.2026. |
| `mdt_decision` | 2026-08-16 | 866–899 | 1.0 | MDT 16/8: hoitolinja vahvistettu. |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-07-16 | 794–838 | 0.45 | Esitiedot: eSH-lähete vastaanotettu 16.7.26. |
| `ct_done` | 2026-07-21 | 839–865 | 0.45 | Keuhko-TT tehty 21.7.2026. |
| `mdt_decision` | 2026-08-16 | 866–899 | 0.45 | MDT 16/8: hoitolinja vahvistettu. |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-07-16 | 805–838 | 0.95 | eSH-lähete vastaanotettu 16.7.26. |
| `ct_done` | 2026-07-21 | 839–865 | 0.95 | Keuhko-TT tehty 21.7.2026. |
| `mdt_decision` | 2026-08-16 | 866–899 | 0.95 | MDT 16/8: hoitolinja vahvistettu. |


---

## 5. Swedish MDT minutes (v1)

- **note_id:** `SYN-P0002-mdt_minutes-03`  
- **patient_id:** `SYN-P0002`  
- **lang / doc_type / note_date:** sv / `mdt_minutes` / 2026-04-09  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 32 / True  
- **patient-level gold clock:** day_count=50, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Fiktiva valfardsomradets centralsjukhus
Anteckningsdatum 9.4.2026. Patient: Matti Mallipotilas SYN-P0002 (SYN-P0002), f. 11.11.1943.
SYNTETISK patientjournal, ingen verklig person.

Besöksorsak: utredning av misstänkt lungcancer (syntetiskt exempel).
Remissen mottogs 8.3.2026.
Föregående uppgifter: dT torax utförd 21.3.2026.
Biopsire togs vid bronkoskopi 26.3.26.
Histologiskt svar inkom i söndags (adenokarcinom).
Vårdkonferens 9.4.2026: multidisciplinär rekommendation.
Födelsedatum 11.11.1943 kontrollerat i befolkningsuppgitferna.
Gallblåsan opererades bort 18.3.2012 (ej relaterat till nuvarande utredning).

Antecknat av: syntetisk tetanvändare. Detta är inte en verklig journal.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 804–830 | 1.0 | Remissen mottogs 8.3.2026. |
| `ct_done` | 2026-03-21 | 831–879 | 1.0 | Föregående uppgifter: dT torax utförd 21.3.2026. |
| `biopsy_done` | 2026-03-26 | 880–918 | 1.0 | Biopsire togs vid bronkoskopi 26.3.26. |
| `pathology_result` | 2026-04-05 | 919–969 | 1.0 | Histologiskt svar inkom i söndags (adenokarcinom). |
| `mdt_decision` | 2026-04-09 | 970–1026 | 1.0 | Vårdkonferens 9.4.2026: multidisciplinär rekommendation. |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 804–830 | 0.45 | Remissen mottogs 8.3.2026. |
| `ct_done` | 2026-03-21 | 831–879 | 0.45 | Föregående uppgifter: dT torax utförd 21.3.2026. |
| `pathology_result` | 2026-04-05 | 919–969 | 0.45 | Histologiskt svar inkom i söndags (adenokarcinom). |
| `mdt_decision` | 2026-04-09 | 970–1026 | 0.45 | Vårdkonferens 9.4.2026: multidisciplinär rekommendation. |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-08 | 804–830 | 0.95 | Remissen mottogs 8.3.2026. |
| `ct_done` | 2026-03-21 | 853–879 | 0.95 | dT torax utförd 21.3.2026. |
| `biopsy_done` | 2026-03-26 | 880–918 | 0.95 | Biopsire togs vid bronkoskopi 26.3.26. |
| `pathology_result` | 2026-04-02 | 919–969 | 0.95 | Histologiskt svar inkom i söndags (adenokarcinom). |
| `mdt_decision` | 2026-04-09 | 970–1026 | 0.95 | Vårdkonferens 9.4.2026: multidisciplinär rekommendation. |


---

## 6. English discharge summary (v1, full pathway)

- **note_id:** `SYN-P0001-discharge_summary-05`  
- **patient_id:** `SYN-P0001`  
- **lang / doc_type / note_date:** en / `discharge_summary` / 2026-08-31  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 46 / False  
- **patient-level gold clock:** day_count=46, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Placeholder Lung Clinic
Note date 31.8.2026. Patient: Aino Synteettinen SYN-P0001 (SYN-P0001), DOB 15.4.1945.
SYNTHETIC record, not a real person.

Reason for visit: work-up of suspected lung cncer (synthetic eexample).
Specialist erferral received 16.7.2026.
CT thorax was carried out on 21.7.26.
Biopsies were obtained during bronchoscopy on 2026-08-01.
History: pathology result issued on 13.8: small-cell lung cancer.
Multidisciplinary meeting (MDT) on 16.8.2026: recommend proceeding to treatment.
It was decided on 18.8.26 to proceed with wedge resection.
Wedge resection performed on 31.8.2026.
Hip replacement on 21.10.2013.
Cholecystectomy performed on 21.10.2013 (unrelated to the present work-up).

Entered by: synthetic test user. This is not a reall clinical record.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-07-16 | 784–823 | 1.0 | Specialist erferral received 16.7.2026. |
| `ct_done` | 2026-07-21 | 824–861 | 1.0 | CT thorax was carried out on 21.7.26. |
| `biopsy_done` | 2026-08-01 | 862–919 | 1.0 | Biopsies were obtained during bronchoscopy on 2026-08-01. |
| `pathology_result` | 2026-08-13 | 920–985 | 1.0 | History: pathology result issued on 13.8: small-cell lung cancer. |
| `mdt_decision` | 2026-08-16 | 986–1066 | 1.0 | Multidisciplinary meeting (MDT) on 16.8.2026: recommend proceeding to treatment. |
| `treatment_decision` | 2026-08-18 | 1067–1125 | 1.0 | It was decided on 18.8.26 to proceed with wedge resection. |
| `treatment_start` | 2026-08-31 | 1126–1165 | 1.0 | Wedge resection performed on 31.8.2026. |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `ct_done` | 2026-07-21 | 824–861 | 0.45 | CT thorax was carried out on 21.7.26. |
| `biopsy_done` | 2026-08-01 | 862–919 | 0.45 | Biopsies were obtained during bronchoscopy on 2026-08-01. |
| `pathology_result` | 2026-08-13 | 920–985 | 0.45 | History: pathology result issued on 13.8: small-cell lung cancer. |
| `mdt_decision` | 2026-08-16 | 986–1066 | 0.45 | Multidisciplinary meeting (MDT) on 16.8.2026: recommend proceeding to treatment. |
| `treatment_decision` | 2026-08-18 | 1067–1125 | 0.45 | It was decided on 18.8.26 to proceed with wedge resection. |
| `treatment_start` | 2026-08-31 | 1126–1165 | 0.45 | Wedge resection performed on 31.8.2026. |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-07-16 | -1–-1 | 0.95 | Specialist referral received 16.7.2026. |
| `ct_done` | 2026-07-21 | 824–861 | 0.95 | CT thorax was carried out on 21.7.26. |
| `biopsy_done` | 2026-08-01 | 862–919 | 0.95 | Biopsies were obtained during bronchoscopy on 2026-08-01. |
| `pathology_result` | 2026-08-13 | 920–985 | 0.95 | History: pathology result issued on 13.8: small-cell lung cancer. |
| `mdt_decision` | 2026-08-16 | 986–1066 | 0.95 | Multidisciplinary meeting (MDT) on 16.8.2026: recommend proceeding to treatment. |
| `treatment_decision` | 2026-08-18 | 1067–1125 | 0.95 | It was decided on 18.8.26 to proceed with wedge resection. |
| `treatment_start` | 2026-08-31 | 1126–1165 | 0.95 | Wedge resection performed on 31.8.2026. |


---

## 7. Finnish pathology with typo_heavy noise (v1)

- **note_id:** `SYN-P0087-pathology_report-02`  
- **patient_id:** `SYN-P0087`  
- **lang / doc_type / note_date:** fi / `pathology_report` / 2026-09-05  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** typo_heavy  
- **day_count / alert (from this note's gold events vs note_date):** 34 / True  
- **patient-level gold clock:** day_count=53, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Kekistyn yliopistollinen sairaala
Kirjauspäivä 5.9.2026. Potilas: Eeeva Esimerkki SYN-P0087 (SYN-P0087), s. 12.6.1946.
SYNTEETTINEN potilaskerttomus, ei oikeaa heniklöä.

Käynnin syy: keuhkosyöpäepäilyn selvittely (synteetinen esimerkki).
ESH-lähete vastaanotettu 2.8.26.
Thoraxin TT tehty 14.8.2026. Kuvauksessa todettiin vasemman alalohkon 2,4 cm muutos.
Biopsiat otettuu bronkoskopiassa 2026-08-25.
Histologinen vastaus saapui 4.9 (NSCLC, ei tarkemmin luokiteltu).
Sappirakon poisto tehty 9.7.2012 (ei liity nyykiseen selvittelyyn).

Kirjaaja: synteettinen testikäytäjä. Tää ei ole oikea potilaskertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-08-02 | 798–830 | 1.0 | ESH-lähete vastaanotettu 2.8.26. |
| `ct_done` | 2026-08-14 | 831–915 | 1.0 | Thoraxin TT tehty 14.8.2026. Kuvauksessa todettiin vasemman alalohkon 2,4 cm muutos. |
| `biopsy_done` | 2026-08-25 | 916–960 | 1.0 | Biopsiat otettuu bronkoskopiassa 2026-08-25. |
| `pathology_result` | 2026-09-04 | 961–1026 | 1.0 | Histologinen vastaus saapui 4.9 (NSCLC, ei tarkemmin luokiteltu). |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-08-02 | 798–830 | 0.45 | ESH-lähete vastaanotettu 2.8.26. |
| `ct_done` | 2026-08-14 | 831–859 | 0.45 | Thoraxin TT tehty 14.8.2026. |
| `biopsy_done` | 2026-08-25 | 916–960 | 0.45 | Biopsiat otettuu bronkoskopiassa 2026-08-25. |
| `pathology_result` | 2026-09-04 | 961–1026 | 0.45 | Histologinen vastaus saapui 4.9 (NSCLC, ei tarkemmin luokiteltu). |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-08-02 | 798–830 | 0.95 | ESH-lähete vastaanotettu 2.8.26. |
| `ct_done` | 2026-08-14 | 831–859 | 0.95 | Thoraxin TT tehty 14.8.2026. |
| `biopsy_done` | 2026-08-25 | 916–960 | 0.95 | Biopsiat otettuu bronkoskopiassa 2026-08-25. |
| `pathology_result` | 2026-09-04 | 961–1026 | 0.95 | Histologinen vastaus saapui 4.9 (NSCLC, ei tarkemmin luokiteltu). |


---

## 8. Finnish oncology note, late wait, day-28 alert (v1)

- **note_id:** `SYN-P0051-oncology_note-04`  
- **patient_id:** `SYN-P0051`  
- **lang / doc_type / note_date:** fi / `oncology_note` / 2026-05-08  
- **corpus:** `tasan-extract-synthetic-v1`  
- **archetype:** late_wait  
- **day_count / alert (from this note's gold events vs note_date):** 53 / True  
- **patient-level gold clock:** day_count=53, alert=True  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Synteettisen hyvinvointialueen keskussairaala
Kirjauspäivä 8.5.2026. Potilas: Jane Synthetic SYN-P0051 (SYN-P0051), s. 19.2.1960.
SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.

Käynnin syy: keuhkosyöpäepäilyn selvittely (synteettinen esimerkki).
Lähete saapunut keuhkoklinikalle 16.3.26.
Thoraxin TT tehty 23.3.2026.
Esitiedot: bronkoskopia ja biopsia tehty 27.3.2026.
PAD-vastaus valmistui 8.4.2026: NSCLC, ei tarkemmin luokiteltu.
Esitiedot: moniammatillinen kokous (MDT) 12.4: suositellaan etenemistä hoitoon.
Hoitopäätös 2026-04-12: kuratiivinen lobektomia.
Odotetaan jatkotoimia. Hoitoa ei ole aloitettu tässä vaiheessa.
Syntymäaika 19.2.1960 tarkistettu väestötiedoista.
Sappirakon poisto tehty 14.6.2022 (ei liity nykyiseen selvittelyyn).

Kirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-16 | 803–844 | 1.0 | Lähete saapunut keuhkoklinikalle 16.3.26. |
| `ct_done` | 2026-03-23 | 845–873 | 1.0 | Thoraxin TT tehty 23.3.2026. |
| `biopsy_done` | 2026-03-27 | 874–925 | 1.0 | Esitiedot: bronkoskopia ja biopsia tehty 27.3.2026. |
| `pathology_result` | 2026-04-08 | 926–989 | 1.0 | PAD-vastaus valmistui 8.4.2026: NSCLC, ei tarkemmin luokiteltu. |
| `mdt_decision` | 2026-04-12 | 990–1069 | 1.0 | Esitiedot: moniammatillinen kokous (MDT) 12.4: suositellaan etenemistä hoitoon. |
| `treatment_decision` | 2026-04-12 | 1070–1118 | 1.0 | Hoitopäätös 2026-04-12: kuratiivinen lobektomia. |


### Regex baseline (untuned on v2 test)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-16 | 803–844 | 0.45 | Lähete saapunut keuhkoklinikalle 16.3.26. |
| `ct_done` | 2026-03-23 | 845–873 | 0.45 | Thoraxin TT tehty 23.3.2026. |
| `biopsy_done` | 2026-03-27 | 874–925 | 0.45 | Esitiedot: bronkoskopia ja biopsia tehty 27.3.2026. |
| `pathology_result` | 2026-04-08 | 926–989 | 0.45 | PAD-vastaus valmistui 8.4.2026: NSCLC, ei tarkemmin luokiteltu. |
| `mdt_decision` | 2026-04-12 | 990–1069 | 0.45 | Esitiedot: moniammatillinen kokous (MDT) 12.4: suositellaan etenemistä hoitoon. |
| `treatment_decision` | 2026-04-12 | 1070–1118 | 0.45 | Hoitopäätös 2026-04-12: kuratiivinen lobektomia. |


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-03-16 | 803–844 | 0.95 | Lähete saapunut keuhkoklinikalle 16.3.26. |
| `ct_done` | 2026-03-23 | 845–873 | 0.95 | Thoraxin TT tehty 23.3.2026. |
| `biopsy_done` | 2026-03-27 | 874–925 | 0.95 | Esitiedot: bronkoskopia ja biopsia tehty 27.3.2026. |
| `pathology_result` | 2026-04-08 | 926–989 | 0.95 | PAD-vastaus valmistui 8.4.2026: NSCLC, ei tarkemmin luokiteltu. |
| `mdt_decision` | 2026-04-12 | 990–1069 | 0.95 | Esitiedot: moniammatillinen kokous (MDT) 12.4: suositellaan etenemistä hoitoon. |
| `treatment_decision` | 2026-04-12 | 1070–1118 | 0.95 | Hoitopäätös 2026-04-12: kuratiivinen lobektomia. |


---

## 9. v2 test: written-vs-received referral (held-out phrasing)

- **note_id:** `SYN2-P0010-referral_letter-01`  
- **patient_id:** `SYN2-P0010`  
- **lang / doc_type / note_date:** fi / `referral_letter` / 2026-04-15  
- **corpus:** `tasan-extract-synthetic-v2` (split: test)  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 1 / False  
- **patient-level gold clock:** day_count=40, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
Keksityn yliop istollinen sairaala
Kirjauspäivä 15.4.2026. Potilas: Olli Oletettu SYN2-P0010 (SYN2-P0010), s. 19.5.1960.
SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.

Diktoitu merkintä keuhkoselvittelystä (synteettinen harjoi tusteksti).
Konsultaatiopyyntö laadittiin lauantaina, mutta se kirjattiin saapuneeksi vasta 14. huhtikuuta 2026.
Kuvantaminen on vasta ajanvaraus viikolla 18 keskiviikkona (2026), sitä ei ole toteutettu.
— ote vanhasta kirjauksesta 2.7.2023: syntymäaika 19.5.1960; sappirakon poisto 2.7.2023; ei liity nykyiseen keuhkoselvittelyyn. —
Aiemmin jossain tammikuun alussa oli käynyt kontrollissa; tarkkaa päivää ei ole tässä.
Lonkkaproteesi operoitu 4.4.2022.

Kirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilask ertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-04-14 | 832–932 | 1.0 | Konsultaatiopyyntö laadittiin lauantaina, mutta se kirjattiin saapuneeksi vasta 14. huhtikuuta 2026. |


### Regex baseline (untuned on v2 test)

_none_


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-04-14 | 832–932 | 0.95 | Konsultaatiopyyntö laadittiin lauantaina, mutta se kirjattiin saapuneeksi vasta 14. huhtikuuta 2026. |


---

## 10. v2 test: booked-vs-performed CT (held-out phrasing)

- **note_id:** `SYN2-P0014-ct_report-02`  
- **patient_id:** `SYN2-P0014`  
- **lang / doc_type / note_date:** fi / `ct_report` / 2026-08-19  
- **corpus:** `tasan-extract-synthetic-v2` (split: test)  
- **archetype:** complete_treated  
- **day_count / alert (from this note's gold events vs note_date):** 15 / False  
- **patient-level gold clock:** day_count=60, alert=False  
- **SYNTHETIC:** yes

### Note text (body; full file with SYNTHETIC header is in samples.json)

```
K-eksityn yliopisto1linen sairaala
Kirjauspäivä 19.8.2026. Potilas: Juhani Jäljitelmä SYN2-P0014 (SYN2-P0014), s. 28.7.1957.
SYNTEETTINEN potilaskertomus, ei oikeaa henkilöä.

Diktoitu merkintä keuhk-oselvittelystä (synteettinen harjoitu-steksti).
Lä-hete saapui toimistoon viikolla 32 tiistaina (2026) (kirjoituspäivä on eri, ks. alla).
Kuvausaika merkittiin kalenteriin viikolla 33 tiistaina (2026); itse tutkimus toteutettiin viikolla 34 maanantaina (2026).
Kuvissa erottui oikean ylälohkon 3,1 cm tuumori.
Aktiivista hoitoa ei ole aloitettu, vasta pohditaan vaihtoehtoja.
A iemmin jossain tammikuun a lussa oli käynyt kontrollissa; tarkkaa päivää ei ole tässä.

Kirjaaja: synteettinen testikäyttäjä. Tämä ei ole oikea potilaskertomus.
```

### Gold events

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-08-04 | 829–918 | 1.0 | Lä-hete saapui toimistoon viikolla 32 tiistaina (2026) (kirjoituspäivä on eri, ks. alla). |
| `ct_done` | 2026-08-17 | 919–1041 | 1.0 | Kuvausaika merkittiin kalenteriin viikolla 33 tiistaina (2026); itse tutkimus toteutettiin viikolla 34 maanantaina (2... |


### Regex baseline (untuned on v2 test)

_none_


### Model JSON (Qwen3-32B)

| type | date | start–end | confidence | evidence_span |
|---|---|---|---|---|
| `referral_received` | 2026-08-09 | 829–918 | 0.95 | Lä-hete saapui toimistoon viikolla 32 tiistaina (2026) (kirjoituspäivä on eri, ks. alla). |
| `ct_done` | 2026-08-19 | 919–1041 | 0.95 | Kuvausaika merkittiin kalenteriin viikolla 33 tiistaina (2026); itse tutkimus toteutettiin viikolla 34 maanantaina (2... |


---
