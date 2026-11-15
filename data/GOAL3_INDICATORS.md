# Goal 3 indicators – National Cancer Strategy 2026–2035 (verbatim) and public-data mapping

Access date: 2026-11-14. Page numbers = printed page numbers (they equal the PDF page index in both files).

- Strategy (S): *Kansallinen syöpästrategia 2026–2035* – https://files.hackjunction.app/resources/Kansallinen_syopastrategia_2026_2035_FINAL.pdf (raw copy: `raw/Kansallinen_syopastrategia_2026_2035_FINAL.pdf`, text: `.txt`)
- Roadmap (R): *Toimeenpanon tiekartta vuosille 2026–2031* – https://files.hackjunction.app/resources/Kansallinen_syopastrategia_toimeenpanon_tiekartta_2026_2031.pdf

Goal 3 = **"Varmistetaan yhdenvertainen ja vaikuttava syövänhoito"** (Ensure equal and effective cancer care), S p. 5 and p. 32. Roadmap Goal 3 section starts R p. 54.

The PDFs are byte-identical (same md5) to `/workspace/junction-new/pitch/sources/`.

**Goal 3 has exactly THREE headline indicators (S p. 5, Kuva 1): G3-a, G3-b, G3-c below.** Section B lists the strategy's *sub-goal* measures (3.1–3.5). Screening 80 % and stage I–II 70 % are **Goal 2** (section C).

## A. Headline Goal 3 targets (strategy figure "Kuva 1", S p. 5)

| # | Verbatim (FI) | Page | Public regional data found? | Our file / note |
|---|---|---|---|---|
| G3-a | "Huonoennusteisten syöpien 5 vuoden elossaololuvut saavuttavat pohjoismaisen tason**" — footnote: "Viiden vuoden suhteellinen elossaolo kasvaa Nordcan-tilastossa esitetystä vuoden 2023 tasosta yli 14 prosenttiyksikköä keuhko­syövässä, 6 prosenttiyksikköä haimasyövässä ja 14 prosenttiyksikköä maksasyövässä. Pohjoismaisella tasolla viitataan Ruotsin ja Norjan keskiarvoon." | S p. 5 | **Partly.** No public lung/pancreas/liver 5-y survival by wellbeing county found (only national in NORDCAN; county-level only in the Cancer Registry Shiny app, not scraped). Proxy by county: lung-cancer **curative-treatment share** 2019–2023 (Cancer Registry/FICAN lung report, Taulukko 11). Sotkanet has county 5-y relative survival only for breast (3625), cervical (3626), bowel (3627) – not poor-prognosis cancers. | `csv/lung_report2026_treatment_by_wsc.csv`; `csv/sotkanet_3627_survival5y_bowel.csv` |
| G3-b | "Syöpäkuolleisuus pienenee 10 % (nykyisin 13 300 henkilöä vuodessa)" | S p. 5 | **Partly.** Cancer deaths by county: StatFin 13u5 (counts + CRUDE rate only, not age-standardised → regional comparison confounded by age structure). National 2024: 13 316 cancer deaths (C00–C97), consistent with the strategy's 13 300. | `csv/statfin_13u5_cancer_deaths_by_wsc.csv` |
| G3-c | "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa***" — footnote "THL (Ohjaus 21/2016). Hoitoonpääsyn seuranta syövän hoidossa." | S p. 5 (also S p. 33; R p. 57) | **Targets sourced:** THL Ohjaus 21/2016: 6 weeks from referral arrival to first treatment, plus cancer-specific limits (see `TREATMENT_TARGETS.md`). **Achievement by region: no public statistic.** Proxy: lung cancer diagnosis→first-treatment medians by collaborative area (`csv/lung_report2024_days_dx_to_first_treatment_by_yta.csv`). Closest: THL non-urgent queue for specialty 65 *Syöpätaudit* (tiny n, excludes urgent cancer care) and generic referral-processing indicators (Sotkanet 13, 5033). | `csv/thl_eshjono_oncology_waits_by_wsc.csv`; `csv/sotkanet_13_*.csv`, `csv/sotkanet_5033_*.csv` |
| Cross-cutting | "Yhdenvertaisuus • Alueelliset ja sosioekonomiset erot syövän ilmaantuvuudessa, hoidossa ja syöpä­kuolleisuudessa ovat käytettävissä palvelutoiminnassa ja niillä ohjataan toimintaa" | S p. 5 | This whole dataset is an attempt at this; most treatment-stage data are missing. | – |

## B. Sub-goal measures ("Tavoitteen toteutumista mitataan seuraavasti")

### 3.1 Kansalliset hoitosuositukset ja hoitoketjut ohjaavat yhdenvertaista, viiveetöntä ja vaikuttavaa hoitoa (S p. 33)
| Verbatim | Page | Public data? |
|---|---|---|
| "Ajantasaisten kansallisten hoitosuositusten ja hoitoketjujen saatavuudessa ollaan pohjois­maisella tasolla (hoitosuositusten osuus suhteessa pohjoismaisiin verrokkeihin, %)." | S p. 33; R p. 56 | No public data. |
| "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa." | S p. 33; R p. 57 ("Mittari: Potilaat pääsevät hoitoon tavoiteaikojen puitteissa.") | **No cancer-specific public data** (see G3-c). R p. 57 schedule: "2026–2028: Kansalliset hoitoketjukuvaukset tehty viidestä syövästä ja syöpäkohtaiset hoitoonpääsyajat on määritetty." → cancer-specific target times do not yet exist. |
| "Kansalliset ja yhtenäiset tavoitteet ja keskeisimmät vaikuttavuuden seurantamittarit määri­tetty sovittuihin syöpiin." | S p. 33; R p. 59 | No (process indicator). |

### 3.2 Kansallinen syövänhoidon laaturekisteri, systemaattinen tulosten tarkastelu ja vertaisarviointi tukevat vaikuttavan hoidon kehittämistä (S p. 36)
| Verbatim | Page | Public data? |
|---|---|---|
| "Syöpäkohtaisten tietojen kirjaaminen laaturekisteriin, vertaiskehittämistoiminta käytössä (syöpätyyppien lukumäärä, joista tieto käytettävissä laaturekistereissä)." | S p. 36; R p. 61 | Qualitative: lung-cancer report 2019–2023 published 23.4.2026 (FICAN news). |
| "Laaturekisterin tietopohja (ml. levinneisyystieto) mahdollistaa laadun ja vaikuttavuuden luotettavan arvioinnin ja vertailun (tietopohjan kattavuus 90 %)." | S p. 36; R p. 60 | **Yes (lung, national + chart by county).** Stage at diagnosis missing ("Ei tietoa") for 7 097 / 14 873 = **47.7 %** of lung cancers 2019–2023 → coverage ≈52 % vs 90 % target. County split only as a bar chart (Kuva 13) – values not tabulated. `csv/lung_report2026_stage_info_coverage_national.csv`, `raw/lung_figs/Kuva_13.png` |
| "Saatavilla on luotettavaa tietoa syövän diagnostiikka- ja hoitokäytäntöjen alueellisista eroista, minkä avulla voidaan kaventaa eroja hoitotuloksissa." | S p. 36; R p. 61–62 | Partly (lung report Taulukko 10–11). |
| "Kliinisten syöpäilmoitusten määrä (tavoitteena 90 % tapauksista automatisoidusti vuoteen 2030 mennessä)." | S p. 36 | Cancer Registry "Kliinisten ilmoitusten tilasto" app (Shiny, by county) exists – **not extracted** (interactive only). |

### 3.3 Kuntoutus, psykososiaalinen tuki, terveyssosiaalityö ja palliatiivinen hoito … (S p. 38)
Verbatim measures (S p. 38; R p. 64–67): "Syöpäpotilaiden osuus, joiden oire-, elämänlaatu- ja toimintakykytieto on saatavilla (%)." · "Yksiköiden osuus, joissa saatavilla psykososiaalisia, sosiaalisia, henkisiä/hengellisiä ja kuntoutuspalveluita (%)." · "Syöpäpotilaiden osuus, joille laadittu yksilöllinen suunnitelma kuntoutumisen tueksi (%)." · "Levinnyttä syöpää sairastavien potilaiden osuus, joille laadittu elämän loppuvaiheen enna­koiva hoitosuunnitelma (%)." · "Levinnyttä syöpää sairastavien potilaiden osuus, joilla palliatiivinen hoito aloitettu jo sairauden hoidon rinnalla (%)." · "Palliatiivisten hoitolinjauksien määrät syöpään kuolleista potilaista (%) sekä palliatiivisten hoitolinjauksien ajankohta suhteessa kuolemaan (vrk)." · "Syöpäpotilaiden osuus, jotka saivat syöpään kohdistuvaa hoitoa viimeisen elinkuukauden aikana (%)."
→ **No public regional data** for any of these. Closest proxy: lung report share with symptomatic/palliative treatment by county (Taulukko 11, `treatment_group_fi = Oireenmukainen`).

### 3.4 Toimintakykytieto ohjaa ikääntyneiden syöpäpotilaiden diagnostiikkaa ja hoitoa (S p. 39)
Verbatim (S p. 39; R p. 69–70): "Niiden hyvinvointialueiden osuus, jossa kaikille soveltuville ikääntyneille syöpäpotilaille tehdään geriatris-onkologinen arviointi (%)." · "Niiden hyvinvointialueiden osuus, joissa perusterveydenhuollolla on mahdollisuus konsultoida geriatrisen onkologian tiimiä jo syövän diagnostiikkavaiheessa (%)." · "Niiden syöpää hoitavien yksiköiden määrä Suomessa, joissa toteutetaan iäkkäiden potilaiden geriatrista seulontaa ja arviointia (%)." · "G8-seulan hyödyntäminen ja/tai geriatrin läsnäolo moniammatillisissa hoitotiimeissä, G8-seulan käytön seuranta syövänhoidon eri aloilla."
→ **No public data.**

### 3.5 Riittävä ja osaava henkilöstö … (S p. 42)
Verbatim (S p. 42; R p. 72–77): "Ammattilaisten alueellinen jakautuminen, sairauspoissaolot ja työtyytyväisyyskyselyt." · "Valmistuneiden ja erikoistumiskoulutuksen suorittaneiden määrä vuosittain." · "Geriatrisen onkologian sisältyminen geriatrian erikoislääkärikoulutukseen." · "Perustettu palliatiivisen lääketieteen erikoislääkärikoulutus." · "Digitaalisten hoitopolkujen käyttöaste syöpää hoitavissa yksiköissä." (R p. 74 adds: "…ja tekoälysovellusten käyttöaste…")
→ **No public data collected here** (oncologist workforce by county not found in Sotkanet).

## C. Closely related Goal 2 targets used in FINDINGS (for context – NOT Goal 3)
- "Kaikissa syöpäseulontaohjelmissa saavutetaan 80 %:n osallistumisaste jokaisella hyvinvointialueella" (S p. 5); R p. 48: "Mittari: Seulontoihin osallistumisaste (tavoitteena vähintään 80 % osallistumisaste eri ohjelmissa kaikilla hyvinvointialueilla ja Helsingin kaupungissa)." → **Public data: yes** (Sotkanet 3620, 3621, 6103).
- "Vähintään 70 % syövistä diagnosoidaan levinneisyysluokissa I-II" (S p. 5; R p. 34, 53) → **No public county data** on stage distribution (only stage-coverage chart for lung).
- R p. 27/33: "Mittari: Seulontoihin osallistumisasteen parantuminen siten, että äidinkielenään muita kieliä kuin suomea ja ruotsia puhuvan väestön osallistumisaste saavuttaa suo­men- ja ruotsinkielisen väestön tason." → no public breakdown by language found.

## D. Recommended Goal 3 indicator(s) for the demo
1. **G3-c "Potilaat pääsevät hoitoon tavoiteaikojen puitteissa"** – show honestly that it is *unmeasurable publicly today*; the demo can define the missing metric (referral→diagnosis→treatment days by county) as the "early-warning" input.
2. **3.2 stage-data coverage (target 90 %)** – lung: 52 % coverage nationally (47.7 % missing), large county variation in Kuva 13.
3. **G3-a proxy** – lung curative-treatment share by county 18.5 %–35.6 % (2019–2023).
