"""Run raw-base and prompt-only base generations before candidate training."""

# ruff: noqa: E402

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.contracts.models import Decision
from juniper_router.data.validate import load_jsonl
from juniper_router.evaluation.metrics import evaluate_predictions
from juniper_router.rendering.chatml import render_router_prompt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    parser.add_argument("--eval", type=Path, default=Path("evals/frozen/router-eval-v1.jsonl"))
    parser.add_argument("--output", type=Path, default=Path("artifacts-local/baselines"))
    parser.add_argument("--max-new-tokens", type=int, default=48)
    args = parser.parse_args()
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit("install requirements-model.in") from exc
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True)
    model.eval()
    rows = load_jsonl(args.eval)
    args.output.mkdir(parents=True, exist_ok=True)
    torch.manual_seed(42)
    for label in ("raw-base", "prompt-only-base"):
        path = args.output / f"{label}.jsonl"
        output_rows = []
        with path.open("w", encoding="utf-8", newline="\n") as handle:
            for row in rows:
                user_text = row["messages"][0]["content"]
                prompt = (
                    user_text
                    if label == "raw-base"
                    else render_router_prompt(
                        user_text, registry=row["registry"], policy=row["policy"]
                    )
                )
                tokens = tokenizer(prompt, return_tensors="pt", truncation=True, max_length=512)
                with torch.no_grad():
                    generated = model.generate(
                        **tokens, do_sample=False, max_new_tokens=args.max_new_tokens
                    )
                continuation = tokenizer.decode(
                    generated[0][tokens["input_ids"].shape[1] :], skip_special_tokens=False
                )
                prediction = None
                try:
                    start = continuation.find("{")
                    end = continuation.rfind("}")
                    if start >= 0 and end > start:
                        prediction = Decision.from_dict(
                            json.loads(continuation[start : end + 1])
                        ).to_dict()
                except (ValueError, json.JSONDecodeError):
                    prediction = None
                output_row = {
                    "example_id": row["example_id"],
                    "expected_decision": row["expected_decision"],
                    "registry": row["registry"],
                    "policy": row["policy"],
                    "prediction": prediction,
                    "raw_output": continuation,
                }
                output_rows.append(output_row)
                handle.write(json.dumps(output_row, ensure_ascii=False, sort_keys=True) + "\n")
        metrics_path = args.output / f"{label}.metrics.json"
        metrics_path.write_text(
            json.dumps(evaluate_predictions(output_rows), indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        print(path)
        print(metrics_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
