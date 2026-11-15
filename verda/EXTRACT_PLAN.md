# Tasan Extract — Verda plan

*JN Verda Lead. Written 14 Nov 2026, ~20:50 Europe/Helsinki (EET, UTC+2). Live Cloud API reads at 20:42–20:44 EET. No instance was created for this work. No paid Inference completion was made (usage still 0). GPU budget target < $25. This document is a plan, not a run log.*

Prices, availability and Inference catalogue below are from the Verda API unless marked **ESTIMATED**. Sources: `GET https://api.verda.com/v1/locations`, `/instance-types`, `/instance-availability` (list + per-type), `/instances`, `/volumes`, `/ssh-keys`, `/images`, `/inference/models`, `/inference/subscriptions`, `/inference/subscriptions/status`, `/inference/usage`, and `GET https://inference.verda.com/v1/models`. List prices also match https://verda.com/pricing (read earlier today). Supporting dumps: `verda/discovery/`.

---

## 1. Concept

Tasan Extract is a sovereign open-weight extractor that turns free-text lung-cancer pathway notes into the event dates the Tasan day-28 clock needs. The events are referral, CT, biopsy, MDT, treatment decision and treatment start. From those we derive `day_count` (days since referral, relative to the note date) and an `alert` when the clock has reached day 28 and treatment has not started.

This is the product gap the rest of Tasan cannot close from public data. The fact pack already records that no county publishes referral→diagnosis times or 6-week compliance (`nodata_referral_to_diagnosis`, `nodata_regional_target_compliance`). A wellbeing services county can only fill that clock from its own clinical notes. Those notes are health data. They must not be sent to a third-party model provider, and “EU-hosted” is not the same as “Finnish”. Verda Inference is the right *baseline* (open-weight, OpenAI-compatible, prompts not stored or used for training, models in Germany), but it is a shared API in DE. The hero is a vLLM-served open-weight instruct model on a GPU instance in a Finnish Verda datacentre (FIN-01 / FIN-02 / FIN-03), with the notes and the weights staying on that box.

Compute is what makes the weekend demo real. A 7B model can be faked on a laptop; a 32B multilingual instruct model, served with structured JSON output, evaluated on ~600 gold-labelled synthetic notes (Finnish plus Swedish and English, typoed and abbreviated) for precision/recall, notes/sec, latency and cost per 1,000 notes, and compared to both a small model and the Inference API, is a GPU job. That comparison is the claim: same prompt, same gold, three runtimes, measured numbers, instance deleted afterwards.

The corpus is entirely synthetic, with gold labels generated from templates before any paraphrase. No real patient data, tonight or in the demo. If a county later runs this for real, the same image pins to a Finnish location (and, later, a confidential-computing SKU).

---

## 2. Live availability (read-only, 14 Nov 2026 20:42–20:44 EET)

### 2.1 Locations

`GET /v1/locations` returned **only three locations, all in Finland**:

| code | name | country |
|---|---|---|
| FIN-01 | Finland 1 | FI |
| FIN-02 | Finland 2 | FI |
| FIN-03 | Finland 3 | FI |

There is **no German (or other) instance location** in this API. Inference models, separately, list `datacenters: [{country_code: "DE"}]` — EU, not Finland. Wording remains: “self-hosted on a Finnish GPU instance” vs “EU-hosted Inference (Germany)”.

### 2.2 What is in stock right now

`GET /v1/instance-availability` and the per-type endpoint `GET /v1/instance-availability/{type}?is_spot={true|false}&location_code={FIN-0x}` (boolean) agree. Types we care about that returned `true`:

| Location | Type | Hardware (from `/instance-types`) | On-demand | Spot | On-demand in stock? | Spot in stock? |
|---|---|---|---:|---:|---|---|
| **FIN-01** | **`1A100.22V`** | 1× A100 SXM4 **80 GB**, 22 vCPU, 120 GB RAM | **$2.386/h** | **$1.193/h** | **yes** | **yes** |
| **FIN-02** | **`1RTX6000ADA.10V`** | 1× RTX 6000 Ada **48 GB**, 10 vCPU, 60 GB RAM | **$1.606/h** | **$0.803/h** | **yes** | **yes** |
| FIN-03 | `8B300.240V.CC.AMD` | 8× B300 CC 268 GB (confidential computing) | $101.3/h | $50.63/h | **yes** | no |
| FIN-03 | `8B200.240V.CC.INTEL` | 8× B200 CC 180 GB (confidential computing) | $77.59/h | $38.79/h | no | **yes** |

**Not in stock** in any FIN location, spot or on-demand, at this timestamp (explicit `false` from the per-type endpoint): every **CPU** type tried (`CPU.4V.16G`, `CPU-TURIN.4V.16G`, `CPU.8V.32G`); `1V100.4V` / `2V100.10V`; `1A100.40S.22V` (40 GB); `1H100.80S.30V` and `1H100.80S.32V`; `1H200.141S.44V`; `1L40S.20V`; `1A6000.10V`; `1RTXPRO6000.30V`; `2A100.44V`; `2H100.80S.80V`; single-GPU B200/B300. A new V100 cannot be started even though a teammate already has one running (see §2.5).

Stock moves during the weekend. Re-check `GET /v1/instance-availability` immediately before any launch. Do not treat this table as a reservation.

### 2.3 Catalogue prices (all 84 types; location prices identical across FIN-01/02/03)

Relevant slices from `GET /v1/instance-types` (USD, `price_per_hour` / `spot_price`; `location_prices` did not differ by site). Billing is Pay As You Go in pre-paid 10-minute increments, unused part refunded (docs + `data/SPEND.md`). Block storage **$0.20/GiB-month**, confirmed on a 50 GB volume in this project (`monthly_price` 10, `base_hourly_cost` ≈ $0.01370/h for 50 GB).

| Type | GPU | VRAM | On-demand | Spot |
|---|---|---:|---:|---:|
| `1V100.4V` | 1× V100 | 16 GB | $0.244/h | $0.122/h |
| `1A100.40S.22V` | 1× A100 | 40 GB | $1.699/h | $0.8495/h |
| `1A6000.10V` | 1× RTX A6000 | 48 GB | $0.888/h | $0.444/h |
| `1RTX6000ADA.10V` | 1× RTX 6000 Ada | 48 GB | $1.606/h | $0.803/h |
| `1L40S.20V` | 1× L40S | 48 GB | $2.018/h | $1.009/h |
| **`1A100.22V`** | **1× A100 SXM4** | **80 GB** | **$2.386/h** | **$1.193/h** |
| `1H100.80S.30V` / `.32V` | 1× H100 SXM5 | 80 GB | $5.241/h | $2.621/h |
| `1RTXPRO6000.30V` | 1× RTX PRO 6000 | 96 GB | $2.836/h | $1.418/h |
| `CPU.4V.16G` / `CPU-TURIN.4V.16G` | — | — | $0.048/h | $0.0192/h |
| `CPU.8V.32G` | — | — | $0.096/h | $0.0384/h |
| `8B200.240V.CC.INTEL` | 8× B200 CC | 1440 GB | $77.59/h | $38.79/h |
| `8B300.240V.CC.AMD` | 8× B300 CC | 2144 GB | $101.3/h | $50.63/h |

**Do not launch the 8-GPU CC types** for this demo: $38.79–$101.3/h would exhaust the $25 cap in 15–38 minutes. They are the scale-path mention for county patient data (confidential computing in FIN-03), not tonight’s box.

### 2.4 Inference API models and prices (task-1 discovery; baseline)

Docs: https://docs.verda.com/inference/ and https://docs.verda.com/inference/models/. Endpoint `https://inference.verda.com/v1`. Per-token, Standard tier. Prompts/responses not stored (in-memory cache ≤ 2 h) and not used for training; not shared with the model provider. Failed/interrupted requests are not charged.

`GET /v1/inference/models` (Cloud API, 20:42:23 EET) lists **exactly two** models. Neither is Llama, Qwen, Mistral or Nemotron. The NVIDIA Nemotron endpoint named on the challenge page is **not in the catalogue** (same finding as `review/VERDA_PLAN.md` on 13–14 Nov). GLM 5.3 is “coming soon” on the marketing page and is **not** in the API list.

| Model | ID | Licence (API) | Where it runs | Context | Input / 1M | Cache read / 1M | Output / 1M | Features |
|---|---|---|---|---:|---:|---:|---:|---|
| Kimi K3.1 Pro (Moonshot, 2.8T-class MoE, 104B active, mxfp4) | `kimi-k3-1-pro` | Kimi K3.1 Pro License (not OSI) | **Germany (DE)** | 1,048,576 | **$2.00** | **$0.20** | **$10.00** | tools, reasoning (default `max`; low/high/max), json_mode, vision |
| DeepSeek V4.1 Flash 1017 (748B MoE, 16B active, mxfp4) | `deepseek-4-1-flash-1017` | **MIT** | **Germany (DE)** | 1,048,576 | **$0.15** | **$0.006** | **$0.60** | tools, json_mode, optional reasoning (answers directly by default), vision; tagged for extraction |

Enabled for this project (`GET /v1/inference/subscriptions`): **`kimi-k3-1-pro` only** (standard, 40 rpm, 3,000,000 tpm, enabled 14 Nov 2026 10:10 EET). `GET https://inference.verda.com/v1/models` with the inference key returns only `kimi-k3-1-pro`. DeepSeek is `status: available` and `accept_new_subscriptions: true` but **not enabled**. Inference status: `active`, minimum balance satisfied. **Usage 14 Oct–14 Nov: 0 requests, 0 tokens.** No paid smoke call has been made. Enabling DeepSeek is a `PUT /v1/inference/subscriptions/deepseek-4-1-flash-1017/standard` — not done, pending approval. Recommended baseline once enabled: DeepSeek (MIT, ~13× cheaper input than Kimi, extraction-tagged). Keep Kimi as a quality-ceiling optional, with `reasoning_effort: low` or off if the API allows, because reasoning tokens are billed as output at $10/M.

### 2.5 Instances this work did **not** create

`GET /v1/instances` at 20:42:22 EET: **1 running instance**, not ours.

- Hostname `tasan-full`, type `1V100.4V` **spot**, FIN-01, $0.122/h, image `24.04.cuda12.9-v100.docker`.
- Created 14 Nov 2026 **20:37:09 EET**. Description: “Tasan Twin smoke test - auto-deleted”. This matches the Data Analyst Pathway Twin full run (SPEND.md §3), not Extract.
- Attached 50 GB OS volume (`monthly_price` $10) and SSH key named `tasan-full-ephemeral`. Trash is empty.

**This track created 0 instances, 0 volumes and 0 keys, and did not modify or delete the teammate resource.** Re-verify before we launch Extract so we do not collide with their box.

---

## 3. Recommended serving setup

### 3.1 Hardware (what we would actually start, when approved)

**Primary: `1A100.22V` in FIN-01** (Finnish DC, 80 GB VRAM). This is the only 80 GB GPU in stock right now, and it is in stock both on-demand and spot.

- **On-demand ($2.386/h)** for the measured eval window — spot “can be discontinued at any time” (Verda docs), and we need a clean latency/throughput number.
- **Spot ($1.193/h)** is acceptable for image pull and model download, or for the whole run if we accept a retry on eviction (auto-fallback to on-demand, still inside the cap).
- OS image (from `GET /v1/images?instance_type=1A100.22V`): **`24.04.cuda13.4.docker`** (Ubuntu 24.04 + CUDA 13.4 Open + Docker). Do **not** reuse the Twin smoke image `24.04.cuda12.9-v100.docker` (V100-specific, not in the A100 list). Do not use the default Jupyter image.
- OS volume **150–200 GB**, delete permanently on teardown. Holds vLLM image + two checkpoints + a small results disk.

**Fallback, if A100 stock disappears: `1RTX6000ADA.10V` in FIN-02**, same Docker image family, 48 GB. Fine for 32B AWQ + 8B; **not** for a comfortable 70B AWQ eval. Driver note on the type: Nvidia driver ≥ 525.105.17 (the 24.04 CUDA 13.4 image should already exceed this).

**Not tonight:** H100 (better for 70B FP8, but **out of stock** and $5.241/h); 8-GPU CC (wrong size and price); a CPU instance for vLLM (out of stock, and 32B does not belong there).

### 3.2 Models, licences, Finnish / Swedish, why these

Serve with **vLLM** (OpenAI-compatible `/v1/chat/completions`, structured JSON). One model at a time on the single GPU (swap weights between evals). Bind vLLM to `127.0.0.1`. A thin `POST /extract` wrapper in front (see §6) does schema validation, date resolution and the day-28 rule — the weights never see a network other than localhost.

| Role | Model (Hugging Face) | Licence | Why | Fits |
|---|---|---|---|---|
| **Hero** | `Qwen/Qwen3-32B-AWQ` (fallback: `Qwen/Qwen3-32B` BF16, or parent-suggested `Qwen/Qwen2.5-32B-Instruct-AWQ`) | **Apache 2.0** (Qwen3-32B and Qwen2.5-32B; confirm the exact card at pull time) | Strong instruction following and JSON; Qwen3 claims **100+ / 119 languages and dialects**, explicitly including the **Uralic** family (Finnish is Uralic). Qwen2.5 officially names 29 languages and does **not** list Finnish in the examples. Disable Qwen3 “thinking” mode for this task (`enable_thinking=false` / `/no_think`) so we get fast, deterministic JSON, not chain-of-thought billed as latency. | AWQ ~18–20 GB weights **ESTIMATED** — comfortable on A100 80 GB and on Ada 48 GB with `max-model-len 8192`. BF16 32B (~64 GB) is A100-only and tight once KV cache and batching are added. |
| **Small comparison** | `Qwen/Qwen3-8B` (or `Qwen/Qwen2.5-7B-Instruct`) | **Apache 2.0** | Same prompt and gold, same box, sequential serve. Shows the quality/speed/cost frontier. 8B/7B is what a county could leave running on a cheaper 48 GB GPU later. | Easy on either SKU (BF16 ~14–16 GB). |
| Optional 70B (only if 32B quality is weak and we are still on the A100) | Llama-3.3-70B-Instruct AWQ or FP8 | **Llama 3.3 Community License** (accept terms; not Apache; use restrictions apply) | Parent-suggested size class. Official Llama 3.1/3.3 language list is 8 languages and **does not include Finnish or Swedish**, so it is a weaker language fit. | AWQ ~35–40 GB **ESTIMATED**: OK on 80 GB with short context; **not** recommended on the 48 GB fallback. FP8 is happier on H100, which is out of stock. |
| Not default | `Qwen/Qwen2.5-72B-Instruct-AWQ` | **Qwen licence** (72B is *not* Apache 2.0; 3B and 72B are the exceptions) | Parent mentioned it; skip unless we have a reason to take a non-Apache 72B. | Tight on 80 GB. |
| Finnish-centric research option (not the hero) | LumiOpen Viking-33B (Apache 2.0; trained on FI, EN, SV, DA, NO, IS + code) or Poro-34B (Apache 2.0; FI+EN only, incomplete research checkpoint, no Swedish) | Apache 2.0 | Best *language* coverage on paper, especially Viking for FI+SV. These are primarily base models; JSON instruction following is likely weaker without an instruct fine-tune. Evaluate only if an instruct checkpoint is clearly available and time remains. | 33–34B AWQ would fit either SKU. |
| **Inference API baseline** (DE, not Finnish) | `deepseek-4-1-flash-1017` (enable first); optional `kimi-k3-1-pro` | MIT / Kimi licence | Same gold, same schema, no GPU instance. Honest “shared EU API vs Finnish self-host” comparison. | n/a |

**Finnish quality, honestly:** we do **not** have a published clinical-Finnish extraction score for any of these models. Qwen3’s Uralic coverage is a documented claim, not a measured result. The 600-note eval *is* the Finnish/Swedish quality study. We will report precision/recall on messy FI notes (relative dates, abbreviations) rather than claiming the model “speaks clinical Finnish” in advance.

**vLLM flags (plan, not yet run):** `vllm serve $MODEL --quantization awq` (when AWQ) `--max-model-len 8192 --gpu-memory-utilization 0.90 --enforce-eager` only if needed, structured output / JSON schema for the event list. Temperature 0. Notes are short; 8k context is enough for prompt + note + JSON. Batch the eval (`n` concurrent in-flight requests) to get a real notes/sec number — that is the “compute let us do this” figure.

---

## 4. Synthetic corpus plan (~600 notes, gold-first)

**No real patient data. No real names, identifiers, or copied EHR text.** Every note is generated.

**Gold is written first**, then the surface form is produced from it. The model is never the source of truth for dates or event types.

1. **Template layer (~40 slot-templates).** Each template has a pathway skeleton and typed slots: event type, ISO date, optional time, hospital/unit *fictional* names, and a note `as_of` date (kirjauspäivä). Event types exactly match the API: `referral`, `ct`, `biopsy`, `mdt`, `treatment_decision`, `treatment_start`. Some pathways are complete; some stop before treatment (these must alert once `day_count >= 28`); some are missing a referral; some have CT but no biopsy, etc.
2. **Surface realisation, two passes.**
   - Deterministic render: slots filled into Finnish / Swedish / English sentence patterns, including abbreviations and relative dates.
   - Constrained paraphrase for messiness: rewrite wording only. A validator **rejects** any paraphrase that drops, adds or changes an event type or a resolvable date. If we use an LLM for paraphrase later, it is a separate, approved, cheap Inference call on already-synthetic text; it is not required to build v1 (templates + a typo/relative-date/abbreviation morpher can get us to 600 without any paid call).
3. **Noise morpher (always on, applied to gold-faithful text):**
   - Typos and missing diacritics (`potilas`, `lähete`→`lahete`, character swaps).
   - Relative dates that must resolve against `as_of`: *viime tiistaina*, *toissapäivänä*, *eilen*, *tällä viikolla*, *3 vk sitten*, *ma 3.11.*, *vko 41*.
   - Abbreviations and mixed-language shorthand common in Finnish lung pathways: **TT** / keuhko-TT / PET-TT (CT), **bronkoskopia** / EBUS, **PAD**, **MDT** / *moniammatillinen kokous* / hoitokokous, lähete / ESH-lähete, hoitopäätös / linjaus, lobektomia / SBRT / sädehoito / sytostaatti. Swedish counterparts: remiss, DT, bronkoskopi, MDK / multidisciplinär konferens, behandlingsstart. Occasional English fragments inside a Finnish note.
4. **Adversarial slice (~10–15%).** Conflicting dates, a date typo that looks like a second event, mention of another cancer, “ei MDT:tä vielä”, no referral anywhere, treatment start with no earlier dates, future tense vs completed events.
5. **Language mix (target 600):** about **420 FI / 90 SV / 90 EN** (70/15/15). Within FI, a share of typo-heavy and relative-date-heavy notes. Split: ~80 prompt-dev, **520 held-out eval**. We do not train tonight; the dev split is only for prompt/schema iteration so the reported scores stay honest.
6. **Gold record (per note):** `id`, `lang`, `as_of`, `events: [{type, date, date_text, evidence_span}]`, `day_count`, `alert`, `tags` (e.g. `relative_date`, `typos`, `missing_referral`). `day_count` is `as_of − referral.date` in days when a referral date exists, else `null`. `alert` is `true` iff `day_count != null` and `day_count >= 28` and there is no `treatment_start` event. This rule is computed from gold, not written by hand, so it cannot drift.

**Eval (run on the GPU box and on the Inference baseline, same gold):**

- Event extraction: precision / recall / F1 **per event type**. A predicted event is a true positive only if the type matches and the ISO date matches gold. Secondary: date within ±1 day (relative-date tolerance) and evidence-span token overlap.
- Clock: `day_count` MAE when gold has a referral; alert precision/recall.
- Systems: notes/sec (batched), p50/p95 latency, tokens if known, **cost per 1,000 notes** (instance-hours allocated across the eval plus any Inference tokens). Label any incomplete run.
- Three systems on the same 520: Qwen3-32B-AWQ (self-host FIN), Qwen3-8B (self-host FIN), DeepSeek V4.1 Flash (Inference, DE) once enabled. Optional Kimi / 70B only if budget remains.

---

## 5. Instance-hour plan and cost (cap < $25)

All dollar figures in this section use **API list prices** from §2. Wall-clock durations are **ESTIMATED** until a run exists. Auto-delete the instance, its volume and the ephemeral SSH key at a hard deadline; verify with `GET /instances`, `/volumes`, `/volumes/trash`, `/ssh-keys`.

### 5.1 Planned shape (not launched)

| Step | What | ESTIMATED wall time |
|---|---|---|
| 1 | Boot `1A100.22V` FIN-01, SSH, docker pull `vllm/vllm-openai` | 10–15 min |
| 2 | Download Qwen3-32B-AWQ + Qwen3-8B (~25–30 GB) | 15–30 min (HF rate **ESTIMATED**) |
| 3 | Serve 32B, warmup, 520-note batched eval + a 16-note latency probe | 10–20 min |
| 4 | Swap to 8B, same eval | 5–10 min |
| 5 | Copy results off, delete instance + volume + key, API verify | 10 min |
|  | **Expected instance life** | **~1.5 hours** |

Inference baseline (DeepSeek) can run from this box or from the laptop against `inference.verda.com`; it does not need the GPU. Skip until DeepSeek is enabled and a small token budget is approved. **No Inference completion in this planning step.**

### 5.2 Expected cost

Storage: 200 GB × $0.20/GiB-month ÷ 730 h ≈ **$0.0548/h**.

| Option | Instance | Storage (1.5 h) | **Expected total** |
|---|---:|---:|---:|
| A100 spot, 1.5 h | 1.5 × $1.193 = $1.79 | $0.08 | **≈ $1.87** |
| A100 on-demand, 1.5 h (preferred for the measured run) | 1.5 × $2.386 = $3.58 | $0.08 | **≈ $3.66** |
| Fallback Ada on-demand, 1.5 h | 1.5 × $1.606 = $2.41 | $0.08 | **≈ $2.49** |

10-minute billing: 1.5 h is 9 increments if rounded up in slices; unused fractions of a 10-min increment are refunded per the docs, so the table above is a close expected value, not a meter reading.

**Inference baseline, ESTIMATED tokens** (not yet run): 520 notes × ~800 input + ~250 output, plus a repeated system prefix that should cache.

- DeepSeek: 520×800×$0.15/1M + 520×250×$0.60/1M ≈ **$0.14** (cache hits would be lower).
- Kimi, if used: 520×800×$2/1M + 520×250×$10/1M ≈ **$2.14**, more if reasoning stays on.

Corpus paraphrase, if we later use DeepSeek for rewrites of 600 short notes, is similarly in the **cents** — estimate in SPEND.md *before* that call.

### 5.3 Worst case, still under $25

Assume: A100 stock flaps, one spot eviction, slow downloads, a second 32B eval, an optional 70B attempt on the A100, and we sit on **on-demand `1A100.22V` for 8 hours** (hard auto-delete).

- Instance: 8 × $2.386 = **$19.09**
- 200 GB storage × 8 h ≈ **$0.44**
- Inference (DeepSeek + a cautious Kimi probe) **ESTIMATED < $3**
- **Worst case ≈ $22.5, under $25.**

Tighter operational cap for the launch approval: **$10** expected-max (4 h on-demand A100 = $9.54 + storage + a DeepSeek baseline). Hard stop still $25. **Never** start an 8-GPU CC type. If at launch time neither `1A100.22V` nor `1RTX6000ADA.10V` is in stock, **do not improvise a bigger SKU** — re-read availability and come back for approval.

---

## 6. API contract draft

Local wrapper in front of vLLM (and, with a runtime flag, in front of Inference). Key stays in env on the server, never in the app. No real patient text in logs; log only note id, timings and token counts.

```
POST /extract
Content-Type: application/json

{
  "text": "string, required, the note",
  "lang": "fi" | "sv" | "en" | null,     // optional hint; model may still answer if omitted
  "as_of": "YYYY-MM-DD"                    // optional; default = today in Europe/Helsinki
}

200:
{
  "events": [
    {
      "type": "referral" | "ct" | "biopsy" | "mdt" | "treatment_decision" | "treatment_start",
      "date": "YYYY-MM-DD" | null,         // resolved ISO; null if mentioned but not resolvable
      "date_text": "string | null",        // surface form, e.g. "viime tiistaina"
      "evidence_span": "string",           // verbatim substring of `text`
      "confidence": 0.0
    }
  ],
  "day_count": 31,                         // integer days (as_of − referral.date), or null
  "alert": true,                           // day_count != null && day_count >= 28 && no treatment_start
  "model": "Qwen/Qwen3-32B-AWQ",
  "refused": false,
  "warnings": []                           // e.g. "unresolved_relative_date", "no_referral"
}

4xx/5xx:
{ "error": "invalid_json" | "missing_text" | "upstream_error" | "...", "detail": "..." }
```

Rules the wrapper, not the model, owns:

- Unknown `type` values are dropped.
- `evidence_span` must be a substring of `text` or it is dropped and `warnings` records it.
- `day_count` and `alert` are computed from the accepted events and `as_of`; the model is not trusted to do the arithmetic.
- Relative dates are resolved against `as_of` using the model’s `date` when present; if `date` is null and `date_text` is relative, the wrapper may leave `date` null rather than guess.
- Empty `text` → 400. If the model returns no events, `events: []`, `day_count: null`, `alert: false`, `refused: false` (there is nothing to refuse; this is “no events found”). `refused: true` is reserved for policy blocks (e.g. a caller asking the model to invent a missing date as if it were a fact).

A `GET /health` returns `{ "ok": true, "model": "...", "backend": "vllm"|"inference" }`. Runnable locally with a fixture backend so the Builder can wire `POST /extract` before any GPU exists. **Do not deploy a billed instance until the budget in §5 is approved.**

---

## 7. What this document is not

- Not a launch. No Extract instance has been created.
- Not the Ask Tasan proxy, `VERDA.md`, or a Discord post (deprioritised).
- Not a paid Inference smoke call (usage is still 0). DeepSeek is not yet enabled.
- Numbers labelled **ESTIMATED** (wall-clock, tokens, VRAM headroom, notes/sec) will be replaced by measured values in the run log and in `data/SPEND.md` after a run.

**Go / no-go to launch:** user approves a cap (recommend $10 operational, $25 hard), we re-read availability, we confirm the teammate `tasan-full` box will not be affected, and we enable DeepSeek only if the Inference baseline is in scope for that same cap.
