# Train / eval leakage controls

This train corpus (`tasan-extract-synthetic-train`, IDs `SYNTR-P*`, seed 20261190) is **SYNTHETIC** and is built to stay off the v2 evaluation families.

- It does **not** read `corpus/data_v2/` or reuse `SYN2-P*` patients.
- Sentence banks in `generate_train.py` are new (e.g. *Saapumispäivä merkitty…*, *Keuhkojen viipalekuvaus tehtiin…*, *Hoitoryhmä kokoontui…*). A banned-substring check rejects v2 anchors such as *Konsultaatiopyyntö kirjattiin saapuneeksi*, *Kerroskuvaus toteutettiin*, *Tiimikokous pidettiin*, *viikolla N … (year)*.
- Date styles are dotted / ISO / spelled / short weekday+date — not v2's `viikolla N maanantaina (2026)` form.
- A v1 easy subset may be added (optionally GPU-paraphrased) as extra train rows. v1 templates are already disjoint from v2. v2 **dev and test are never used for training**.
