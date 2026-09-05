from __future__ import annotations

# ruff: noqa: E402
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.training.config import SFTConfig
from juniper_router.training.sft import run_sft


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument(
        "--train", type=Path, default=Path("data/generated/juniper-router-dataset-v1.jsonl")
    )
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--steps", type=int, default=2)
    parser.add_argument("--sequence-length", type=int, default=512)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--gradient-accumulation-steps", type=int, default=1)
    parser.add_argument("--save-every", type=int, default=50)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--resume", type=Path)
    args = parser.parse_args()
    result = run_sft(
        SFTConfig(
            model_path=args.model,
            train_path=args.train,
            output_dir=args.output,
            sequence_length=args.sequence_length,
            learning_rate=args.learning_rate,
            batch_size=args.batch_size,
            gradient_accumulation_steps=args.gradient_accumulation_steps,
            max_steps=args.steps,
            seed=args.seed,
            save_every=args.save_every,
        ),
        resume=args.resume,
    )
    print(result)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
