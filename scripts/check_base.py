from __future__ import annotations

# ruff: noqa: E402
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.provenance.hashing import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", type=Path, required=True)
    args = parser.parse_args()
    try:
        import torch
        from transformers import AutoModelForCausalLM, AutoTokenizer
    except ImportError as exc:
        raise SystemExit("install requirements-model.in") from exc
    manifest = json.loads(Path("manifests/base-model.json").read_text(encoding="utf-8"))
    for entry in manifest["files"]:
        path = args.model / entry["name"]
        if (
            not path.exists()
            or path.stat().st_size != entry["bytes"]
            or sha256_file(path) != entry["sha256"]
        ):
            raise SystemExit(f"hash or size mismatch: {path}")
    tokenizer = AutoTokenizer.from_pretrained(args.model, local_files_only=True)
    model = AutoModelForCausalLM.from_pretrained(args.model, local_files_only=True)
    if model.num_parameters() != manifest["calculated_trainable_parameters"]:
        raise SystemExit(f"parameter count mismatch: {model.num_parameters()}")
    sample = "Hello, User."
    ids = tokenizer(sample, return_tensors="pt")["input_ids"]
    if tokenizer.decode(ids[0], skip_special_tokens=False) != sample:
        raise SystemExit("tokenizer round-trip failed")
    vocab = tokenizer.get_vocab()
    for token in ("<|im_start|>", "<|im_end|>"):
        if token not in vocab:
            raise SystemExit(f"missing ChatML token: {token}")
    torch.manual_seed(42)
    generated = model.generate(ids, max_new_tokens=4, do_sample=False)
    print(
        json.dumps(
            {
                "status": "tested",
                "parameter_count": model.num_parameters(),
                "token_count": int(ids.shape[1]),
                "fixture": tokenizer.decode(generated[0], skip_special_tokens=False),
            },
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
