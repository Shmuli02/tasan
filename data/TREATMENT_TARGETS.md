# Official cancer treatment target times (Goal 3 indicator "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa")

Access date 2026-11-14. All quotes verbatim from the fetched PDF (raw copy `raw/thl_ohjaus_21_2016.pdf`, text `raw/thl_ohjaus_21_2016.txt`).

**Source:** THL Ohjaus 21/2016, *Hoitoonpääsyn seuranta syövän hoidossa – Määrittelyt ja ohjeistus – Voimassa 1.1.2017 lähtien* (Sillanpää, Pylkkänen, Häkkinen, eds.).
- Item page: https://www.julkari.fi/items/0424a55a-f159-406f-8883-5dfdad4d6772 (permanent: http://urn.fi/URN:ISBN:978-952-302-782-4)
- PDF that worked (via Julkari REST API; the older bitstream link `.../f99e6277-.../content` returns 404): https://www.julkari.fi/server/api/core/bitstreams/de33d584-bdce-40a1-b100-df48c4906a49/content — file name "Hoitoonpääsyn seuranta syövän hoidossa_päivitys170225_**Vanhentunut**.pdf", 46 pages.
- The strategy names exactly this document as the reference for Goal 3 indicator 3: S p. 5 footnote "*** THL (Ohjaus 21/2016). Hoitoonpääsyn seuranta syövän hoidossa."

⚠️ **Caveat.** Every page of the PDF carries a "Vanhentunut" (= outdated) watermark. Julkari says the 2025 update replaced only section 4.5.4 (radiotherapy coding, now Liite 1) and added Liite 2 (MDT meetings). We found **no newer published version of the target times**. The roadmap (R p. 57) plans: "2026–2028: Kansalliset hoitoketjukuvaukset tehty viidestä syövästä ja syöpäkohtaiset hoitoonpääsyajat on määritetty." So cancer-specific target times are still being defined. The 2016 figures below are the latest official numbers we could find.

## 1. Generic maximum times (all cancers). Section 4.1, PDF p. 14 (printed pp. 12–13)
> "Syöpäepäilyssä maksimiaika lähetteen saapumisesta ensimmäiseen hoitoon (leikkaus, lääke- tai sädehoito) on 6 viikkoa. Tätä nopeammin on hoidettava erittäin kiireellistä hoitoa edellyttävät syövät, joissa hoidon tulee alkaa muutamassa päivässä tai korkeintaan 2−3 viikossa diagnoosista. Syöpäepäilyssä radiologin lausunto kuvantamistutkimuksesta tulee olla käytettävissä viikon kuluessa tutkimuspyynnön tekemisestä. Syöpäepäilyssä kudosnäyte (kirurginen biopsia tai neulanäyte) tulee ottaa viikon kuluessa tutkimuspyynnön saapumisesta kirurgiseen yksikköön tai kuvantamisyksikköön. Patologin lausunnon tulee olla käytettävissä viikon kuluessa kudosnäytteen otosta, jos syöpädiagnoosi ei edellytä erikoisvärjäyksiä. Leikkauksen jälkeiset liitännäishoidot (säde- tai lääkehoidot) tulee aloittaa viimeistään 4 viikon kuluessa leikkauksesta, ellei potilaasta johtuva syy (esim. toipuminen leikkaustoimenpiteestä) edellytä pitempää aikaa."

> "…edellä kuvatut aikarajat pätevät pääsääntöisesti myös uusiutuneen syövän diagnostiikassa ja hoidossa."

The same section says these limits come from the STM cancer-care working group (STM Selvityksiä 6/2010). The THL 2017 final report notes that the 2010 limits were proposed only as guidance ("ohjeellisina") (see §3).

| Pathway step | Max. time | Clock starts |
|---|---|---|
| Suspected cancer → first treatment (surgery, drug or radiotherapy) | **6 weeks (42 days)** | arrival of the referral |
| Very urgent cancers → treatment | **a few days, at most 2–3 weeks** | diagnosis |
| Radiologist's imaging report | **1 week** | imaging request |
| Tissue sample (biopsy/needle) taken | **1 week** | request arrives at surgical/imaging unit |
| Pathologist's report (no special stains) | **1 week** | sampling |
| Adjuvant radio-/drug therapy after surgery | **≤ 4 weeks** | surgery |

## 2. Cancer-specific recommended maximum times (from placement on the treatment queue). Section 4.3.2, Kuviot 2–5, PDF pp. 19–20 (printed pp. 17–18)
> "Syövän hoidon hoitoonpääsyn seurannassa esitetään suositellut enimmäisajat seuraavien syöpien hoidon osalta: invasiivinen rintasyöpä ja intraduktaalinen rintasyöpä (C50- ja D05.1-alkuiset diagnoosit) (Kuvio 2) · eturauhassyöpä (C61-alkuiset diagnoosit) (Kuvio 3) · paksu- ja peräsuolisyöpä (C18-20-alkuiset diagnoosit) (Kuviot 4 ja 5). Suositellut enimmäisajat esitetään vaihtoehtoisille hoitopoluille hoitojononoon asettamispäivämäärästä erityyppisiin hoitoihin. Suositellut enimmäissajat perustuvat ohjausryhmän asiantuntija-arvioihin…"

**Verification (done 2026-11-14).**
1. The numbers ("4 vkoa", "6 vkoa", "3 vkoa", "3 kk", "5 vrk", "8 vkoa") are **text glyphs inside the PDF figures**, not our OCR: they come out of `pdftotext` (raw/thl_ohjaus_21_2016.txt lines 978–1075).
2. We rendered PDF pp. 19–20 (`raw/thl_figs/p-19.png`, `p-20.png`, 110 dpi) and checked each label sits on the arrow we assign it to. Every label below matched its arrow.
3. The clock start is explicit in the section text ("hoitojononoon asettamispäivämäärästä erityyppisiin hoitoihin"), i.e. **from placement on the treatment queue**, not from referral and not from diagnosis.
4. **Second independent source: none found.**
   - A second Julkari bitstream of the same guide (`f99e6277-…`) shows the same labels in search extracts, but it is the same document, so it is not independent (download returns HTML/404).
   - THL Työpaperi 3/2017 (`raw/thl_hoitoonpaasy_loppuraportti_2017.txt` ~l. 774–797) reports shares treated "kolmessa viikossa hoitojonoon asettamispäivästä" for breast, prostate and bowel. It does **not** restate the targets.
   - FICAN Länsi-Suomi patient page says only "4–6 viikon kuluttua lähetteen kirjoittamisesta" (https://fican.fi/lantinen-syopakeskus/syovan-hoito/tietoa-potilaalle/hoitoonpaasyajat/), which is generic and is a regional centre's patient text.
   - So these items are verified against the primary document only.

| Cancer (ICD-10) | Queue placement → first treatment | First → next treatment | Status |
|---|---|---|---|
| Breast C50, D05.1 (Kuvio 2) | → surgery **4 wk**; → neoadjuvant drug therapy **4 wk** | surgery → adjuvant radio/drug **6 wk**; drug therapy → surgery **4 wk**; that surgery → radio/drug **6 wk** | **VERIFIED (primary source, diagram + section text); no independent 2nd source** |
| Prostate C61 (Kuvio 3) | → active surveillance / surgery / radiotherapy **6 wk**; → drug therapy (WB–WC codes; disseminated WD) **4 wk** | surgery → radiotherapy **3 months**; drug therapy → radiotherapy **3 months** | **VERIFIED (primary source); no 2nd source**. The 6-wk arrow fans out to three boxes and the 4-wk arrow to two; the reading is unambiguous in the render. |
| Colon C18–19 (Kuvio 4) | → surgery or drug therapy **3 wk** | surgery → adjuvant drug therapy **6 wk** | **VERIFIED (primary source); no 2nd source** |
| Rectum C20 (Kuvio 5) | → surgery / drug / short RT 5×5 Gy / long RT 45–54 Gy **3 wk** | short RT → surgery **5 days**; long RT → surgery **8 wk**; surgery → adjuvant drug **6 wk** (both paths) | **VERIFIED (primary source); no 2nd source** |
| **Lung C33–C34** | **No lung-specific target.** §4.3.2 lists only C50/D05.1, C61 and C18–20. | – | **VERIFIED ABSENT.** Lung falls under the generic §4.1 limit: **6 weeks from referral arrival to first treatment**, or 2–3 weeks from diagnosis for very urgent cancers. The roadmap (R p. 57) defines cancer-specific times only in 2026–2028. |
| Generic 6 wk / 1 wk / 4 wk (§4.1) | – | – | **VERIFIED VERBATIM** (quoted above, PDF p. 14). Partial independent corroboration: FICAN Länsi-Suomi "4–6 viikon kuluttua lähetteen kirjoittamisesta". |

The whole PDF is watermarked **Vanhentunut** (outdated). On a lung slide, use only the generic 6-week §4.1 limit.

## 3. Is achievement of these targets publicly reported by region?
**No regional public statistic exists.** This is the core data gap for Goal 3 indicator 3.
- THL Työpaperi 3/2017 (project final report), https://www.julkari.fi/items/c296653c-356e-4742-a029-ddab51cd0aab (PDF https://www.julkari.fi/server/api/core/bitstreams/c0c8c67d-3b8b-4016-ad52-b40682713441/content, raw copy `raw/thl_hoitoonpaasy_loppuraportti_2017.pdf`), p. "Lukijalle": "Näiden aikarajojen käyttöönottoa ehdotettiin ohjeellisina. Viiveiden seuraamisen vastuutahoksi esitettiin sairaanhoitopiirejä." … "Kansallinen seuranta syöpään sairastuneiden hoitoonpääsystä on puuttunut."
- FICAN statement of 28.2.2025 asks for the same measures: "Syöpäsairauksien kohdalla hoitoonpääsyajan seurantaa tulee tehdä systemaattisesti ja hoitoonpääsyajat julkaista avoimesti. Mittareina voivat olla hoitoonpääsyaika syöpäepäilystä (lähetteestä) diagnoosiin ja diagnoosista hoitoon…" https://fican.fi/wp-content/uploads/2026/08/FICANin-lausunto-luonnoksesta-hyvinvointialueiden-tehtavia-koskeviksi-valtakunnallisiksi-tavoitteiksi-vuosille-2025-2029-28.02.2025.pdf (quoted from a search-result extract; the PDF was not downloaded).
- We searched Sotkanet (3 797 indicators, `raw/sotkanet_indicators.json`) and found **no** cancer-specific waiting-time indicator.

### Closest available public numbers (proxies, each with caveats)
1. **Lung cancer, days from diagnosis to first treatment, by collaborative area (YTA), diagnosed 1/2018–6/2022.** Syöpärekisteri, *Keuhkosyöpä Suomessa* (2024), Taulukko 4.1, printed p. 27. https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf → `csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv`
   - Surgery median: Pohjois-Suomi **13.5 d** (IQR 0–44) vs Etelä-Suomi **46.0 d** (IQR 33–63), a 3.4× difference.
   - Radiotherapy (non-palliative) median: Itä-Suomi 25.0 d vs Länsi-Suomi 45.0 d (Q3 74.5).
   - Drug therapy median: 34.5 d (Länsi) to 43.0 d (Sisä).
   - Interpretation: these intervals start at the **Cancer Registry diagnosis date**, while the THL 6-week limit starts at **referral arrival**. The medians cover only patients whose first treatment within 6 months was that modality. **Surgery Q1 = 0 days** in Pohjois, Itä and Sisä means at least a quarter of surgical patients have surgery on the diagnosis date, so low surgical medians partly reflect how diagnosis is dated. The report gives no reason for this. Our guess is that the diagnosis is dated from the resection specimen. We give no 6-week compliance inference. See LUNG.md.
2. **THL non-urgent queue, specialty 65 Syöpätaudit (oncology), by county** (sampo.thl.fi eshjono): `csv/thl_eshjono_oncology_waits_by_wsc.csv`. Nationally 486 patients were waiting on 30.9.2026, 3.5 % of them > 90 days. **Not a cancer time-to-treatment measure.** It covers only *non-urgent* oncology queues, while most cancer treatment is urgent. Counts per county are tiny (1–283), so the percentages are unstable. It is unverified monthly data.
3. **HUS publishes a median wait for its oncology specialty**: "Syöpätautien" median **7 days** (30.9.2026). https://www.hus.fi/potilaalle/opas-potilaalle/oikeutesi-potilaana/hoitoonpaasy-erikoissairaanhoidossa (from a search-result extract). Generic specialty queue only, one provider.

## 4. Regional survival data available (Goal 3 indicator 1 context)
- Sotkanet 5-year relative survival by wellbeing county, Cancer Registry: breast (3625), cervical (3626), **bowel (3627)**. Nothing for the strategy's poor-prognosis cancers (lung, pancreas, liver). → `csv/sotkanet_362[5-7]_*.csv`
  - Bowel 2024 (patients diagnosed 2015–2024): Päijät-Häme **63 %**, Satakunta / North Savo / Kainuu 64 % vs Central Uusimaa **74 %**, Vantaa-Kerava / Lapland 73 %. National 68 %.
- Lung: age-standardised **1-year relative survival by YTA and sex with 95 % CI** is tabulated in the 2024 report, Taulukko 5.1 (follow-up 2020–2022) → `csv/lung_report2024_survival_1y_by_yta.csv`. By-county survival exists only as curves (2026 report Kuva 20; not digitised). No public **5-year** lung survival by region.
- Hospital-district survival variation: Seppä K, Malila N, Pitkäniemi J. *Acta Oncologica* 2020;59(11):1316–1321, cited in the roadmap (R p. 12, footnote 4). Not fetched.
