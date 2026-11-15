#!/usr/bin/env bash
# Reproduce everything (run from data/): needs python3 + pandas + lxml; network access to sotkanet.fi, pxdata.stat.fi, sampo.thl.fi, syoparekisteri.fi, files.hackjunction.app
set -euo pipefail
cd "$(dirname "$0")/.."
mkdir -p raw csv
curl -sfL -A "curl/8 junction" -o raw/sotkanet_indicators.json "https://sotkanet.fi/rest/1.1/indicators?lang=en"
curl -sfL -A "curl/8 junction" -o raw/sotkanet_regions.json "https://sotkanet.fi/rest/1.1/regions"
for u in Kansallinen_syopastrategia_2026_2035_FINAL.pdf Kansallinen_syopastrategia_toimeenpanon_tiekartta_2026_2031.pdf; do
  curl -sfL -o raw/$u "https://files.hackjunction.app/resources/$u"; pdftotext -layout raw/$u raw/${u%.pdf}.txt; done
curl -sfL -A "Mozilla/5.0" -o raw/keuhkosyoparaportti_2026.html https://syoparekisteri.fi/assets/themes/ssy3/factsheets/keuhkosyoparaportti.html
curl -sfL -A "Mozilla/5.0" -o raw/Keuhkosyopa_Suomessa.pdf https://syoparekisteri.fi/assets/files/2024/12/Keuhkosyopa_Suomessa.pdf
curl -sfL -A "Mozilla/5.0" -o raw/thl_ohjaus_21_2016.pdf https://www.julkari.fi/server/api/core/bitstreams/de33d584-bdce-40a1-b100-df48c4906a49/content && pdftotext -layout raw/thl_ohjaus_21_2016.pdf raw/thl_ohjaus_21_2016.txt
curl -sfL -o raw/thl_eshjono_dims.json https://sampo.thl.fi/pivot/prod/fi/eshjono/jonotilanne/fact_eshjono_jonotilanne.dimensions.json
python3 scripts/fetch_sotkanet.py
python3 scripts/build_sotkanet_csv.py
python3 scripts/spreads.py
python3 scripts/fetch_statfin_cancer_deaths.py
python3 scripts/build_lung_report_csv.py
python3 scripts/fetch_thl_eshjono_oncology.py
python3 scripts/derived_metrics.py
python3 scripts/lung2024_table41.py  # superseded by build_lung2024_tables.py (kept for provenance)
# OCR cross-check needs: pdftoppm -r 200 renders in raw/lung2024_pages + pip rapidocr_onnxruntime; python3 scripts/ocr_pages.py raw/lung2024_pages/p-*.png
python3 scripts/build_lung2024_tables.py
python3 scripts/derived_lung_first_treatment_by_month.py
python3 scripts/kuva13_stage_missing_estimate.py
python3 scripts/digitise_lung2026_agestd_curative.py   # needs raw/lung_figs/img2026_176.png, _177.png (base64 figures extracted from the 2026 HTML)
python3 scripts/digitise_lung2026_agestd_national.py   # national reference lines from Kuva 15/16 (same extracted figures)
python3 scripts/build_data_gaps.py
python3 scripts/build_hero_json.py
python3 scripts/hero_lead_agestd.py
python3 scripts/hero_people_number.py
python3 scripts/build_combined_json.py
python3 scripts/build_facts.py
python3 scripts/check_facts.py
python3 scripts/build_app_data.py    # chart-ready JSON for the app -> app/*.json (read-only use of csv/, hero.json, facts.json)
python3 scripts/check_app_data.py
