"""Add people_number to hero.json. Arithmetic: for each wellbeing county whose crude curative share
(Taulukko 11, dx 2019-2023) is below the national share 4009/14873 = 26.95%, gap = 0.2695*N - n; sum / 5 diagnosis years."""
import csv, json, pathlib
d = pathlib.Path(__file__).resolve().parent.parent
rows = [r for r in csv.DictReader(open(d/'csv/lung_report2026_treatment_by_wsc.csv'))
        if r['treatment_group_fi']=='Parantava' and r['sex']=='total' and r['region_code']!='358']
p = 4009/14873
below = []
for r in rows:
    n, N = int(r['numerator']), int(r['denominator'])
    if n/N < p:
        below.append({"region": r['region'], "code": r['region_code'], "n": n, "N": N,
                      "share_pct": round(100*n/N,1), "gap_5y": round(p*N-n,1), "gap_per_year": round((p*N-n)/5,1)})
tot = sum(b['gap_5y'] for b in below)
lap = next(b for b in below if b['region'].startswith('Lapland'))
h = json.loads((d/'hero.json').read_text())
h["people_number"] = {
  "value_per_year": round(tot/5), "value_5y": round(tot), "lapland_per_year": round(lap['gap_per_year']),
  "unit": "lung cancer patients per year",
  "statement_en": f"If every wellbeing county below the national average had reached the national curative-treatment share (27.0%), about {round(tot/5)} more lung cancer patients a year would have had a curative-treatment record, about {round(lap['gap_per_year'])} of them in Lapland.",
  "statement_fi": f"Jos jokainen kansallisen keskiarvon alle jäävä hyvinvointialue olisi yltänyt parantavan hoidon valtakunnalliseen osuuteen (27,0 %), noin {round(tot/5)} keuhkosyöpäpotilasta enemmän vuodessa olisi saanut parantavan hoidon merkinnän, heistä noin {round(lap['gap_per_year'])} Lapissa.",
  "method": f"For each of the {len(below)} wellbeing counties with a crude curative share below the national 4009/14873 = 26.95%: gap = 0.2695 x patients - patients with curative treatment. Summed gap {tot:.1f} over 5 diagnosis years (2019-2023) divided by 5 = {tot/5:.1f}/yr (Lapland {lap['gap_5y']}/5 = {lap['gap_per_year']}/yr). Computed by Tasan; not a published figure.",
  "counties": below,
  "period": "diagnosed 2019-2023, 12-month follow-up; per-year = 5-year total / 5",
  "source_url": "https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html",
  "source_table": "Keuhkosyöpä Suomessa 2019-2023 (Syöpärekisteri/FICAN, publ. 23.4.2026), Taulukko 11 (counts by wellbeing county)",
  "caveat": "Illustrative arithmetic by Tasan, not a published estimate and not a causal claim. Uses crude shares (not age- or stage-adjusted; stage is missing for 48% of lung cancers), so some of the gap may reflect older or less fit patients, later stage, or differences in how treatment is recorded. Benchmark is the national average, not a clinical optimum. 'Curative treatment' = surgery or curative radiotherapy recorded in national registers within 12 months. Does not say how many lives would be saved.",
  "safe_wording_en": f"About {round(tot/5)} more lung cancer patients a year would get curative treatment if every below-average county reached the national rate, based on Cancer Registry counts for 2019-2023 (illustrative, not adjusted for stage).",
  "do_not_say": ["lives saved", "deaths prevented", "patients denied treatment", "exact number (always 'about')"]
}
(d/'hero.json').write_text(json.dumps(h, ensure_ascii=False, indent=1))
print(round(tot/5,1), lap['gap_per_year'], len(below))
