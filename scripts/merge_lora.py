"""Merge a LoRA adapter into the pinned base for portable Safetensors export."""

from __future__ import annotations

import argparse
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base", type=Path, required=True)
    parser.add_argument("--adapter", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    from peft import PeftModel
    from transformers import AutoModelForCausalLM, AutoTokenizer

    base = AutoModelForCausalLM.from_pretrained(args.base, local_files_only=True)
    model = PeftModel.from_pretrained(base, args.adapter, is_trainable=False).merge_and_unload()
    args.output.mkdir(parents=True, exist_ok=True)
    model.save_pretrained(args.output, safe_serialization=True)
    AutoTokenizer.from_pretrained(args.base, local_files_only=True).save_pretrained(args.output)
    print(args.output)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
