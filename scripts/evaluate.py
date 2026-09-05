from __future__ import annotations

# ruff: noqa: E402
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.data.validate import load_jsonl
from juniper_router.evaluation.metrics import evaluate_predictions


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--predictions",
        type=Path,
        required=True,
        help="JSONL with expected_decision and prediction",
    )
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = evaluate_predictions(load_jsonl(args.predictions))
    text = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
