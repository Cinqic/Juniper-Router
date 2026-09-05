"""Portable assistant-only SFT loop using optional PyTorch/Transformers."""

from __future__ import annotations

import hashlib
import json
import random
import time
from pathlib import Path
from typing import Any

from juniper_router.contracts import Decision
from juniper_router.data.validate import load_jsonl
from juniper_router.rendering.chatml import render_router_prompt

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
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    model = AutoModelForCausalLM.from_pretrained(config.model_path, local_files_only=True)
    trainable_parameters = sum(parameter.numel() for parameter in model.parameters())
    if config.method == "lora":
        from peft import LoraConfig, TaskType, get_peft_model

        model = get_peft_model(
            model,
            LoraConfig(
                r=config.lora_r,
                lora_alpha=config.lora_alpha,
                lora_dropout=config.lora_dropout,
                target_modules=["q_proj", "k_proj", "v_proj", "o_proj"],
                task_type=TaskType.CAUSAL_LM,
            ),
        )
        trainable_parameters = sum(
            parameter.numel() for parameter in model.parameters() if parameter.requires_grad
        )
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
        if checkpoint.get("config", {}).get("train_path") != str(config.train_path):
            raise ValueError("checkpoint training data does not match requested resume")
        checkpoint_serialization = checkpoint.get("config", {}).get(
            "target_serialization", "sorted-keys-v1"
        )
        if checkpoint_serialization != config.target_serialization:
            raise ValueError("checkpoint target serialization does not match requested resume")
        model.load_state_dict(checkpoint["model"])
        optimizer.load_state_dict(checkpoint["optimizer"])
        start_step = int(checkpoint["step"])
        if "python_rng_state" in checkpoint:
            random.setstate(checkpoint["python_rng_state"])
        if "torch_rng_state" in checkpoint:
            torch.set_rng_state(checkpoint["torch_rng_state"])
    log_path = config.output_dir / "train.jsonl"
    started = time.monotonic()
    tokens_seen = 0
    for step in range(start_step, config.max_steps):
        optimizer.zero_grad(set_to_none=True)
        record_ids = []
        loss_total = 0.0
        accumulation = config.gradient_accumulation_steps
        for micro_step in range(accumulation):
            start = (step * accumulation + micro_step) * config.batch_size
            batch = [
                records[(start + offset) % len(records)] for offset in range(config.batch_size)
            ]
            record_ids.extend(record["example_id"] for record in batch)
            prompts = [
                render_router_prompt(
                    record["messages"][0]["content"],
                    registry=record["registry"],
                    policy=record["policy"],
                    trusted_result=record["policy"].get("trusted_result"),
                    compact=config.prompt_mode == "compact",
                )
                for record in batch
            ]
            texts = [
                prompt
                + _serialize_target(record["expected_decision"], config.target_serialization)
                + "<|im_end|>\n"
                for prompt, record in zip(prompts, batch)
            ]
            encoded = tokenizer(
                texts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=config.sequence_length,
                add_special_tokens=False,
            )
            input_ids = encoded["input_ids"]
            attention_mask = encoded.get("attention_mask")
            labels = input_ids.clone()
            prefix_encoded = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                truncation=True,
                max_length=config.sequence_length,
                add_special_tokens=False,
            )
            prefix_lengths = prefix_encoded["attention_mask"].sum(dim=1).tolist()
            for row_index, prefix_length in enumerate(prefix_lengths):
                if prefix_length >= int(attention_mask[row_index].sum()):
                    raise ValueError(
                        f"sequence_length={config.sequence_length} truncates assistant target for "
                        f"{batch[row_index]['example_id']}"
                    )
                labels[row_index, : int(prefix_length)] = -100
            labels[attention_mask == 0] = -100
            tokens_seen += int(attention_mask.sum())
            outputs = model(input_ids=input_ids, attention_mask=attention_mask, labels=labels)
            loss = outputs.loss
            if not torch.isfinite(loss):
                raise FloatingPointError(f"non-finite loss at step {step + 1}")
            loss_total += float(loss.detach())
            (loss / accumulation).backward()
        torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
        optimizer.step()
        event = {
            "step": step + 1,
            "loss": loss_total / accumulation,
            "elapsed_seconds": time.monotonic() - started,
            "record_ids": record_ids,
            "tokens_seen": tokens_seen,
        }
        if config.eval_path is not None and (step + 1) % config.eval_every == 0:
            event["validation_loss"] = _validation_loss(
                model,
                tokenizer,
                load_jsonl(config.eval_path)[: config.eval_limit],
                config.sequence_length,
                config.prompt_mode,
                config.target_serialization,
            )
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
        "tokens_seen": tokens_seen,
        "method": config.method,
        "prompt_mode": config.prompt_mode,
        "target_serialization": config.target_serialization,
        "trainable_parameters": trainable_parameters,
    }


def _validation_loss(
    model: Any,
    tokenizer: Any,
    records: list[dict[str, Any]],
    sequence_length: int,
    prompt_mode: str,
    target_serialization: str,
) -> float:
    import torch

    if not records:
        return 0.0
    was_training = model.training
    model.eval()
    total = 0.0
    count = 0
    with torch.no_grad():
        for record in records:
            prompt = render_router_prompt(
                record["messages"][0]["content"],
                registry=record["registry"],
                policy=record["policy"],
                trusted_result=record["policy"].get("trusted_result"),
                compact=prompt_mode == "compact",
            )
            target = _serialize_target(record["expected_decision"], target_serialization)
            encoded = tokenizer(
                prompt + target + "<|im_end|>\n",
                return_tensors="pt",
                truncation=True,
                max_length=sequence_length,
                add_special_tokens=False,
            )
            prefix = tokenizer(
                prompt, return_tensors="pt", truncation=True, max_length=sequence_length,
                add_special_tokens=False,
            )["input_ids"]
            if prefix.shape[1] >= encoded["input_ids"].shape[1]:
                continue
            labels = encoded["input_ids"].clone()
            labels[:, : prefix.shape[1]] = -100
            outputs = model(
                input_ids=encoded["input_ids"],
                attention_mask=encoded.get("attention_mask"),
                labels=labels,
            )
            if torch.isfinite(outputs.loss):
                total += float(outputs.loss)
                count += 1
    if was_training:
        model.train()
    return total / count if count else 0.0


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
            "method": config.method,
            "prompt_mode": config.prompt_mode,
            "target_serialization": config.target_serialization,
            "sequence_length": config.sequence_length,
            "learning_rate": config.learning_rate,
            "seed": config.seed,
            "batch_size": config.batch_size,
            "gradient_accumulation_steps": config.gradient_accumulation_steps,
            "lora_r": config.lora_r,
            "lora_alpha": config.lora_alpha,
            "lora_dropout": config.lora_dropout,
        },
    }
    torch.save(payload, temp)
    temp.replace(path)
    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    path.with_suffix(path.suffix + ".sha256").write_text(
        digest + "  " + path.name + "\n", encoding="utf-8"
    )


def _serialize_target(decision: dict[str, Any], serialization: str) -> str:
    parsed = Decision.from_dict(decision).to_dict()
    if serialization == "sorted-keys-v1":
        return json.dumps(parsed, sort_keys=True, separators=(",", ":"))
    return json.dumps(parsed, separators=(",", ":"))
