"""Portable assistant-only SFT loop using optional PyTorch/Transformers."""

from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any

from juniper_router.data.validate import load_jsonl
from juniper_router.rendering.chatml import render_chatml

from .config import SFTConfig


def run_sft(config: SFTConfig, *, resume: Path | None = None) -> dict[str, Any]:
    """Run a real bounded causal-LM update; fail loudly when model deps are absent."""

    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise RuntimeError(
            "SFT requires the optional model environment; install requirements-model.in"
        ) from exc
    random.seed(config.seed)
    torch.manual_seed(config.seed)
    tokenizer = AutoTokenizer.from_pretrained(config.model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(config.model_path, local_files_only=True)
    model.train()
    optimizer = torch.optim.AdamW(model.parameters(), lr=config.learning_rate)
    records = load_jsonl(config.train_path)
    if not records:
        raise ValueError("training data is empty")
    config.output_dir.mkdir(parents=True, exist_ok=True)
    start_step = 0
    if resume is not None:
        checkpoint = torch.load(resume, map_location="cpu", weights_only=False)
        if checkpoint.get("schema_version") != "juniper-router-checkpoint-v1":
            raise ValueError("unsupported checkpoint schema")
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        start_step = int(checkpoint["step"])
        if "python_rng_state" in checkpoint:
            random.setstate(checkpoint["python_rng_state"])
        if "torch_rng_state" in checkpoint:
            torch.set_rng_state(checkpoint["torch_rng_state"])
    log_path = config.output_dir / "train.jsonl"
    started = time.monotonic()
    for step in range(start_step, config.max_steps):
        optimizer.zero_grad(set_to_none=True)
        record_ids = []
        loss_total = 0.0
        microbatches = config.batch_size * config.gradient_accumulation_steps
        for micro_step in range(microbatches):
            record = records[(step * microbatches + micro_step) % len(records)]
            record_ids.append(record["example_id"])
            messages = record["messages"] + [
                {
                    "role": "assistant",
                    "content": json.dumps(
                        record["expected_decision"], sort_keys=True, separators=(",", ":")
                    ),
                }
            ]
            text = render_chatml(messages)
            encoded = tokenizer(
                text, return_tensors="pt", truncation=True, max_length=config.sequence_length
            )
            input_ids = encoded["input_ids"]
            attention_mask = encoded.get("attention_mask")
            labels = input_ids.clone()
            marker = "<|im_start|>assistant\n"
            assistant_start = text.rfind(marker) + len(marker)
            if assistant_start <= len(marker):
                raise ValueError("assistant marker missing from rendered training text")
            prefix_ids = tokenizer(
                text[:assistant_start],
                return_tensors="pt",
                truncation=True,
                max_length=config.sequence_length,
            )["input_ids"]
            labels[:, : min(prefix_ids.shape[1], labels.shape[1])] = -100
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            if not torch.isfinite(loss):
                raise FloatingPointError(f"non-finite loss at step {step + 1}")
            loss_total += float(loss.detach())
            (loss / microbatches).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        event = {
            "step": step + 1,
            "loss": loss_total / microbatches,
            "elapsed_seconds": time.monotonic() - started,
            "record_ids": record_ids,
        }
        with log_path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(json.dumps(event, sort_keys=True) + "\n")
        if (step + 1) % config.save_every == 0 or step + 1 == config.max_steps:
            _save_checkpoint(
                config.output_dir / f"checkpoint-{step + 1}.pt", model, optimizer, step + 1, config
            )
    model.save_pretrained(config.output_dir / "model", safe_serialization=True)
    tokenizer.save_pretrained(config.output_dir / "model")
    return {
        "status": "tested",
        "steps": config.max_steps - start_step,
        "elapsed_seconds": time.monotonic() - started,
        "output_dir": str(config.output_dir),
    }


def _save_checkpoint(path: Path, model: Any, optimizer: Any, step: int, config: SFTConfig) -> None:
    import torch

    temp = path.with_suffix(path.suffix + ".tmp")
    payload = {
        "schema_version": "juniper-router-checkpoint-v1",
        "step": step,
        "model": model.state_dict(),
        "optimizer": optimizer.state_dict(),
        "python_rng_state": random.getstate(),
        "torch_rng_state": torch.get_rng_state(),
        "config": {
            "model_path": config.model_path,
            "train_path": str(config.train_path),
            "seed": config.seed,
            "batch_size": config.batch_size,
            "gradient_accumulation_steps": config.gradient_accumulation_steps,
        },
    }
    torch.save(payload, temp)
    temp.replace(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(
        digest + "  " + path.name + "\n", encoding="utf-8"
    )
