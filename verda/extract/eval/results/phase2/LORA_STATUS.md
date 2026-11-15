# LoRA 8B — started, not completed

Times are Europe/Helsinki (EET, UTC+2) on 14 Nov 2026. All training rows are **SYNTHETIC**. No v2 dev/test documents were in the train set (see `corpus/data_train/LEAKAGE.md`).

LoRA fine-tune of Qwen3-8B was started on instance `715c7100…` (`tasan-extract-p2`, 1A100.22V **spot**, FIN-01) at 22:57:26 EET. It got as far as:

- 481 SYNTHETIC SFT rows loaded (`train_sft.jsonl` + `train_sft_v1.jsonl`)
- Qwen3-8B weights loaded in bf16
- PEFT LoRA applied: **43,646,976** trainable params / 8,234,382,336 all params (**0.5301%**), r=16, alpha=32, targets q/k/v/o/gate/up/down

It then crashed before the first optimizer step:

```
TypeError: TrainingArguments.__init__() got an unexpected keyword argument 'warmup_ratio'
```

The vLLM image had `transformers` 5.20.2, which no longer accepts `warmup_ratio` on `TrainingArguments`. No adapter was written, and there is no 8B-base or 8B-LoRA quality score on the v2 test from this run.

A first attempt on `d81e14db…` (A100 on-demand, 22:43–22:50 EET) also failed at the train step, without usable logs (the fail path did not yet pack them).

Per the 23:09 wrap-up order, LoRA was **not retried** (more than ~30 minutes from a scored result). The follow-up GPU session is sweep-only.
