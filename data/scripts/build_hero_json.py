import json
R24='https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf'; R26='https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html'
hero={
 "project":"Tasan","generated":"2026-11-14","goal":"National Cancer Strategy 2026-2035, Goal 3 (S p.5): (1) 5-yr survival of poor-prognosis cancers to Nordic level; (2) cancer mortality -10%; (3) patients reach treatment within target times (THL Ohjaus 21/2016)",
 "target_reference":{"value":6,"unit":"weeks","label":"THL maximum time from referral arrival to first cancer treatment (all cancers; no lung-specific target exists)","source_url":"https://www.julkari.fi/server/api/core/bitstreams/de33d584-bdce-40a1-b100-df48c4906a49/content","source_table":"THL Ohjaus 21/2016 §4.1, PDF p.14","caveat":"Clock starts at referral arrival. No public regional statistic reports compliance with this target. The PDF is watermarked 'Vanhentunut' (outdated), but the 2026-2035 strategy still cites it."},
 "headlines":[
  {"id":"lung_curative_share","goal_link":"Goal 3 indicator 1 (proxy, not survival)","value":[18.5,35.6],"unit":"%","national":27.0,
   "label":"Lung cancer patients with a curative-treatment record within 12 months: Lapland 18.5% vs Vantaa-Kerava 35.6%",
   "regions":[{"name":"Lapland wellbeing services county","code":"21","value":18.5,"n":131,"N":710,"ci95":[15.8,21.5]},{"name":"Vantaa and Kerava wellbeing services county","code":"04","value":35.6,"n":212,"N":595,"ci95":[31.9,39.6]},{"name":"Finland","value":27.0,"n":4009,"N":14873}],
   "period":"diagnosed 2019-2023, 12-month follow-up","ci_method":"Wilson 95% CI computed by Tasan from printed n/N (not printed in report)",
   "age_standardised_check":{"note":"CHART-DIGITISED from report Kuva 16 (+/-1 pp), not a published number","Lapland":{"men":[16.2,12.7,20.4],"women":[23.1,17.9,29.0]},"Vantaa-Kerava":{"men":[29.8,24.2,36.1],"women":[39.7,33.1,47.0]}},
   "source_url":R26,"source_table":"Keuhkosyöpä Suomessa 2019-2023 (Syöpärekisteri/FICAN, publ. 23.4.2026), Taulukko 11; age-standardised check: Kuva 16",
   "caveat":"Crude share of all lung cancers (C33-C34) diagnosed 2019-2023 among residents of each wellbeing county who had surgery or curative radiotherapy recorded in national registers within 12 months of diagnosis. Not survival and not adjusted for stage (missing for 48% nationally), comorbidity or fitness. Depends on regional treatment recording. The report's age-standardised chart shows the same gap for men and women, so age structure alone does not explain it."},
  {"id":"lung_dx_to_surgery_days","goal_link":"Goal 3 indicator 3 (proxy: starts at diagnosis, not referral)","value":[13.5,46.0],"unit":"days (median)","national":37.0,
   "label":"Median days from lung cancer diagnosis to surgery: North Finland 13.5 vs South Finland 46.0",
   "regions":[{"name":"North Finland collaborative area (Pohjois-Suomi YTA)","code":"YTA-POHJOIS","value":13.5,"iqr":[0,44]},{"name":"South Finland collaborative area (Etelä-Suomi YTA)","code":"YTA-ETELA","value":46.0,"iqr":[33,63]},{"name":"Finland","value":37.0,"iqr":[0,56]}],
   "n":"not printed per area; nationally about 1 in 10 patients (N=1 627) had any surgery within 6 months (report text, PDF p.17)","period":"diagnosed 1/2018-6/2022",
   "source_url":R24,"source_table":"Keuhkosyöpä Suomessa (Syöpärekisteri, 12/2024), Taulukko 4.1, PDF p.28 (printed p.27); national median from text p.27",
   "caveat":"Lung cancers diagnosed Jan 2018-Jun 2022, by collaborative area of residence (5 areas, not wellbeing counties). Median days from Cancer Registry diagnosis date to surgery, only among patients whose first treatment within 6 months was surgery (nationally about 1 in 10 patients had surgery). Not the official 6-week referral-to-treatment clock. In the North at least a quarter of these patients have surgery on the diagnosis date (lower quartile 0 days), so the low median partly reflects how diagnosis is dated. Radiotherapy and drug-therapy medians do not show this North-South pattern."},
  {"id":"lung_treated_within_2_months","goal_link":"Goal 3 indicator 3 (proxy covering all patients)","value":[27.7,38.7],"unit":"%",
   "label":"Share of all lung cancer patients whose first active treatment started within 2 months of diagnosis: West Finland 27.7% vs Inland Finland 38.7%",
   "regions":[{"name":"West Finland collaborative area (Länsi-Suomi YTA)","code":"YTA-LANSI","value":27.7,"ci95_approx":[25.9,29.6],"N":2284},{"name":"Inland Finland collaborative area (Sisä-Suomi YTA)","code":"YTA-SISA","value":38.7,"ci95_approx":[36.6,40.8],"N":2033}],
   "other_areas":{"Itä-Suomi":38.0,"Etelä-Suomi":32.9,"Pohjois-Suomi":30.5},"period":"diagnosed 1/2018-6/2022",
   "ci_method":"approximate Wilson 95% CI computed by Tasan; denominator = area patient total from Taulukko 3.3",
   "source_url":R24,"source_table":"Keuhkosyöpä Suomessa (2024), Taulukko 4.5 PDF p.34 (derived: surgery + non-palliative radiotherapy + drug therapy first-event columns at month 2) and Taulukko 3.3 PDF p.18",
   "caveat":"DERIVED by Tasan. Covers all lung cancers diagnosed Jan 2018-Jun 2022 among residents of each collaborative area. Measure: the cumulative share whose first recorded event within 2 months of the registry diagnosis date was surgery, non-palliative radiotherapy or drug therapy. Starts at diagnosis, not referral. West Finland includes Varsinais-Suomi, where drug therapy is barely recorded in registers (about 1% age-standardised vs 25% nationally), so part of the gap is recording, not care."},
  {"id":"lung_1yr_survival","goal_link":"Goal 3 indicator 1 (context: 1-year, not 5-year)","value":[40.1,46.8],"unit":"%","national":42.9,
   "label":"Age-standardised 1-year relative survival from lung cancer: North Finland 40.1% vs Inland Finland 46.8%",
   "regions":[{"name":"North Finland collaborative area (Pohjois-Suomi YTA)","code":"YTA-POHJOIS","value":40.1,"ci95":[37.5,43.0]},{"name":"Inland Finland collaborative area (Sisä-Suomi YTA)","code":"YTA-SISA","value":46.8,"ci95":[44.1,49.6]},{"name":"Finland","value":42.9,"ci95":[41.8,43.9]}],
   "n":"not printed","period":"follow-up years 2020-2022","ci_method":"95% CI as printed in report",
   "source_url":R24,"source_table":"Keuhkosyöpä Suomessa (2024), Taulukko 5.1, PDF p.36",
   "caveat":"Age-standardised 1-year relative survival of lung cancer patients followed in 2020-2022, by collaborative area of residence, both sexes. One-year survival only: the strategy's indicator is 5-year survival against the Sweden-Norway average, and no public regional 5-year lung survival exists. Not adjusted for stage."},
  {"id":"lung_stage_missing","goal_link":"Data gap (sub-goal 3.2: 90% data coverage, S p.36)","value":47.7,"unit":"%","n":7097,"N":14873,
   "label":"Stage at diagnosis is missing for 47.7% of lung cancers",
   "regions":[{"name":"Finland","value":47.7,"n":7097,"N":14873}],"period":"diagnosed 2019-2023",
   "source_url":R26,"source_table":"Keuhkosyöpä Suomessa 2019-2023, Taulukko 4",
   "caveat":"All lung cancers diagnosed in Finland 2019-2023 (N=14 873): share with no stage information (no TNM, stage, verbal description or registry extent code). By county it ranges from about 22% to about 68% (Tasan's digitisation of report Kuva 13, +/-1 pp). Because stage is missing, no regional comparison can be stage-adjusted."}
 ],
 "excluded":{"sotkanet_6411":"Not used. Sotkanet 6411 is the share of non-urgent primary-care physician visits with a wait over 7 days (all causes, not cancer). Avohilmo data gaps in Vantaa, Kerava and Helsinki make county values unreliable (Vantaa-Kerava 85.4% in 2025 is an artefact risk).","colorectal_screening":"Goal 2 context only (strategy p.5), not a Goal 3 indicator."}
}
json.dump(hero,open(__import__('os').path.join(__import__('os').path.dirname(__file__),'..','hero.json'),'w'),ensure_ascii=False,indent=1)
