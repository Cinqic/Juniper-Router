"""Run an offline Transformers or LoRA model against a frozen JSONL suite."""

from __future__ import annotations

# ruff: noqa: E402
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.contracts import Decision, JsonParseError, parse_json_object
from juniper_router.data.validate import load_jsonl
from juniper_router.evaluation.metrics import evaluate_predictions
from juniper_router.rendering.chatml import render_router_prompt


def _extract_object(text: str) -> dict | None:
    start = text.find("{")
    while start >= 0:
        depth = 0
        quoted = False
        escaped = False
        for index in range(start, len(text)):
            char = text[index]
            if quoted:
                if escaped:
                    escaped = False
                elif char == "\\":
                    escaped = True
                elif char == '"':
                    quoted = False
                continue
            if char == '"':
                quoted = True
            elif char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    try:
                        return parse_json_object(text[start : index + 1])
                    except JsonParseError:
                        break
        start = text.find("{", start + 1)
    return None


def _load_model(model_path: Path, adapter: Path | None):
    import torch
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(model_path, local_files_only=True)
    if adapter is not None:
        from peft import PeftModel

        model = PeftModel.from_pretrained(model, adapter, is_trainable=False)
    model.eval()
    return torch, tokenizer, model


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--adapter", type=Path)
    parser.add_argument("--eval", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--max-new-tokens", type=int, default=96)
    parser.add_argument("--prompt-mode", choices=("full", "compact"), default="compact")
    parser.add_argument("--limit", type=int)
    parser.add_argument("--batch-size", type=int, default=1)
    args = parser.parse_args()
    if args.batch_size < 1:
        parser.error("--batch-size must be positive")
    torch, tokenizer, model = _load_model(args.model, args.adapter)
    tokenizer.padding_side = "left"
    if tokenizer.pad_token is None:
        tokenizer.pad_token = tokenizer.eos_token
    rows = load_jsonl(args.eval)
    if args.limit is not None:
        rows = rows[: args.limit]
    predictions = []
    args.output.parent.mkdir(parents=True, exist_ok=True)
    with torch.no_grad(), args.output.open("w", encoding="utf-8", newline="\n") as handle:
        for offset in range(0, len(rows), args.batch_size):
            batch = rows[offset : offset + args.batch_size]
            prompts = [
                render_router_prompt(
                    row["messages"][0]["content"],
                    registry=row["registry"],
                    policy=row["policy"],
                    trusted_result=row["policy"].get("trusted_result"),
                    compact=args.prompt_mode == "compact",
                )
                for row in batch
            ]
            encoded = tokenizer(
                prompts,
                return_tensors="pt",
                padding=True,
                add_special_tokens=False,
            )
            generated = model.generate(
                **encoded,
                do_sample=False,
                max_new_tokens=args.max_new_tokens,
                pad_token_id=tokenizer.eos_token_id,
            )
            prompt_width = encoded["input_ids"].shape[1]
            for row, generated_row in zip(batch, generated):
                raw = tokenizer.decode(
                    generated_row[prompt_width:], skip_special_tokens=False
                )
                payload = _extract_object(raw)
                prediction = None
                if payload is not None:
                    try:
                        prediction = Decision.from_dict(payload).to_dict()
                    except (TypeError, ValueError):
                        prediction = None
                output = {
                    "example_id": row["example_id"],
                    "expected_decision": row["expected_decision"],
                    "registry": row["registry"],
                    "policy": row["policy"],
                    "risk_tags": row.get("risk_tags", []),
                    "prediction": prediction,
                    "raw_output": raw,
                }
                predictions.append(output)
                handle.write(json.dumps(output, ensure_ascii=False, sort_keys=True) + "\n")
    metrics = evaluate_predictions(predictions)
    metrics_path = args.output.with_suffix(".metrics.json")
    metrics_path.write_text(json.dumps(metrics, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(metrics, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
