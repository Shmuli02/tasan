#!/usr/bin/env python3
"""LoRA SFT of Qwen3-8B on SYNTHETIC Tasan Extract train rows. No v2 test data.

Uses PEFT + transformers.Trainer only (no TRL), so the trainer API cannot
break the session. All notes are SYNTHETIC.
"""
from __future__ import annotations

import json
import os
import traceback
from pathlib import Path

import torch
from datasets import Dataset
from peft import LoraConfig, TaskType, get_peft_model
from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    DataCollatorForLanguageModeling,
    Trainer,
    TrainingArguments,
)

MODEL = os.environ.get("TASAN_TRAIN_MODEL", "Qwen/Qwen3-8B")
DATA = Path(os.environ.get("TASAN_TRAIN_JSONL", "/work/data/train_sft_all.jsonl"))
OUT = Path(os.environ.get("TASAN_LORA_OUT", "/work/out/lora_qwen3_8b"))


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    rows = [json.loads(l) for l in DATA.read_text(encoding="utf-8").splitlines() if l.strip()]
    print(f"loading {len(rows)} SYNTHETIC sft rows from {DATA}", flush=True)
    print(f"cuda={torch.cuda.is_available()} ndev={torch.cuda.device_count()} "
          f"name={torch.cuda.get_device_name(0) if torch.cuda.is_available() else 'cpu'}", flush=True)

    tok = AutoTokenizer.from_pretrained(MODEL, trust_remote_code=True)
    if tok.pad_token is None:
        tok.pad_token = tok.eos_token
    tok.padding_side = "right"

    def to_text(ex):
        kwargs = {"tokenize": False, "add_generation_prompt": False}
        try:
            text = tok.apply_chat_template(ex["messages"], enable_thinking=False, **kwargs)
        except TypeError:
            text = tok.apply_chat_template(ex["messages"], **kwargs)
        return {"text": text}

    ds = Dataset.from_list(rows).map(to_text, remove_columns=list(rows[0].keys()))

    def tokenize(batch):
        return tok(batch["text"], truncation=True, max_length=4096, padding=False)

    ds = ds.map(tokenize, batched=True, remove_columns=["text"])

    model = AutoModelForCausalLM.from_pretrained(
        MODEL, torch_dtype=torch.bfloat16, device_map="auto", trust_remote_code=True,
    )
    model.config.use_cache = False
    try:
        model.gradient_checkpointing_enable()
        if hasattr(model, "enable_input_require_grads"):
            model.enable_input_require_grads()
    except Exception as e:
        print("gradient checkpointing skipped:", e, flush=True)

    model = get_peft_model(model, LoraConfig(
        task_type=TaskType.CAUSAL_LM, r=16, lora_alpha=32, lora_dropout=0.05, bias="none",
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
    ))
    model.print_trainable_parameters()

    args = TrainingArguments(
        output_dir=str(OUT / "checkpoints"),
        num_train_epochs=2,
        per_device_train_batch_size=1,
        gradient_accumulation_steps=8,
        learning_rate=1e-4,
        lr_scheduler_type="cosine",
        warmup_ratio=0.03,
        logging_steps=5,
        save_strategy="no",
        bf16=True,
        report_to=[],
        max_grad_norm=1.0,
        remove_unused_columns=False,
        dataloader_num_workers=0,
        gradient_checkpointing=True,
    )
    collator = DataCollatorForLanguageModeling(tok, mlm=False)
    try:
        trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collator, processing_class=tok)
    except TypeError:
        trainer = Trainer(model=model, args=args, train_dataset=ds, data_collator=collator, tokenizer=tok)
    trainer.train()
    trainer.model.save_pretrained(str(OUT))
    tok.save_pretrained(str(OUT))
    (OUT / "TRAIN_NOTE.txt").write_text(
        "SYNTHETIC LoRA adapter for Tasan Extract. Trained only on SYNTR-P* templates "
        "and a v1 easy slice. No v2 dev/test documents or v2 template families.\n"
    )
    print("saved LoRA to", OUT, flush=True)


if __name__ == "__main__":
    try:
        main()
    except Exception:
        traceback.print_exc()
        raise
