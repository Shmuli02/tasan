# DISCORD DRAFT — NOT POSTED

**DRAFT ONLY. Do not paste this into the Verda Discord channel, or anywhere else, until a teammate reviews it and confirms the public link.** This file is the summary the track asks us to share; it has not been posted.

Suggested channel: the Verda Compute Track Discord channel named in the side-challenge brief (“Share a link to a summary → Post it in our Discord channel”).

---

**Public link (placeholder — confirm before posting):**

https://petaled-trowel-90.beacon.host/

(Confirmed live 2026-11-15 08:01 Europe/Helsinki, freeze build `index-CvE5rxJ9.js`.)

---

## Post text (~200 words)

Tasan is a lung-cancer pathway clock for Finland’s wellbeing services counties. We ran it on Verda in Finnish data centres — every GPU region in the catalogue is in Finland.

The hero is **Tasan Extract**: Qwen3-32B-AWQ on an A100 in FIN-01, turning synthetic Finnish, Swedish and English notes into pathway dates and a day-28 alert. On a hard held-out set: exact-date F1 0.74 and alert accuracy 0.96 (regex F1 0.00). Measured cost is $0.89–$0.99 per 1,000 notes, or about **$15 a year** for all new lung cases in Finland (2,994 patients × ~5 notes; notes-per-patient is a costing assumption). No real patient data. LoRA and a concurrency sweep were not completed (a 7.5-min spot A100 crashed before the first training step). Measuring stopped at 23:12. Final Extract spend ≈ $4.24.

**Pathway Twin** (132 jobs + 5 calibrations) ran on a V100 spot box in FIN-01; outputs matched our local run. A serverless follow-up was blocked by TLS to tasks.verda.com and was deleted.

**Ask Tasan**, the in-app analyst, uses the Verda Inference API (kimi-k3-1-pro, EU/Germany) behind a key-holding proxy.

Process and spend: `verda/VERDA.md`. Instances were deleted (0 instances / 0 volumes at 23:13).
