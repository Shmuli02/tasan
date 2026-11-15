"""Post-process hero.json: lead headline = age-standardised (chart-estimate) curative share by sex;
crude Taulukko 11 figures kept as secondary. Requested by coordinator/judge 2026-11-14."""
import json, pathlib
p = pathlib.Path(__file__).resolve().parent.parent / "hero.json"
h = json.loads(p.read_text())
crude = next(x for x in h["headlines"] if x["id"] == "lung_curative_share")
if "crude_secondary" not in crude:
    lead = {
      "id": "lung_curative_share",
      "goal_link": "Goal 3 indicator 1 (proxy, not survival)",
      "measure_label": "chart estimate, age-adjusted, not stage-adjusted, not survival",
      "unit": "%",
      "label": "Age-adjusted share of lung cancer patients with curative treatment within 12 months. Men: Lapland ~16.2% vs Vantaa-Kerava ~29.8%. Women: ~23.1% vs ~39.7%",
      "value": {"men": [16.2, 29.8], "women": [23.1, 39.7]},
      "regions": [
        {"name": "Lapland wellbeing services county", "code": "21",
         "men": {"value": 16.2, "ci95": [12.7, 20.4]}, "women": {"value": 23.1, "ci95": [17.9, 29.0]}},
        {"name": "Vantaa and Kerava wellbeing services county", "code": "04",
         "men": {"value": 29.8, "ci95": [24.2, 36.1]}, "women": {"value": 39.7, "ci95": [33.1, 47.0]}}
      ],
      "period": "diagnosed 2019-2023, 12-month follow-up",
      "ci_method": "Values and 95% CIs read off the report's chart (Kuva 16), +/-1 pp; not published as numbers",
      "source_url": crude["source_url"],
      "source_table": "Keuhkosyöpä Suomessa 2019-2023 (Syöpärekisteri/FICAN, publ. 23.4.2026), Kuva 16 (age-standardised, by sex); crude: Taulukko 11",
      "caveat": "Chart estimate, age-adjusted, not stage-adjusted, not survival. Values read by Tasan from the report's age-standardised chart (Kuva 16, +/-1 percentage point), not published numbers. Lung cancers (C33-C34) diagnosed 2019-2023 among residents of each wellbeing county; share with surgery or curative radiotherapy recorded in national registers within 12 months of diagnosis. Not adjusted for stage (missing for 48% nationally), comorbidity or fitness, and depends on regional treatment recording. Confidence intervals do not overlap for either sex.",
      "crude_secondary": {k: crude[k] for k in ["value","national","label","regions","period","ci_method","source_table","caveat"]}
    }
    lead["crude_secondary"]["source_table"] = "Keuhkosyöpä Suomessa 2019-2023, Taulukko 11"
    h["headlines"][h["headlines"].index(crude)] = lead
    p.write_text(json.dumps(h, ensure_ascii=False, indent=1))
print("hero.json lead headline: age-standardised by sex")
