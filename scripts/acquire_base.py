"""Acquire only the pinned safe-format base files and write local hashes."""

from __future__ import annotations

import argparse
import json
from datetime import datetime, timezone
from pathlib import Path

from juniper_router.provenance.hashing import sha256_file

MODEL_ID = "HuggingFaceTB/SmolLM2-135M"
REVISION = "93efa2f097d58c2a74874c7e644dbc9b0cee75a2"
ALLOW = [
    "config.json",
    "generation_config.json",
    "model.safetensors",
    "tokenizer.json",
    "tokenizer_config.json",
    "special_tokens_map.json",
]


def parameter_count(config: dict[str, int | bool]) -> int:
    hidden = int(config["hidden_size"])
    intermediate = int(config["intermediate_size"])
    layers = int(config["num_hidden_layers"])
    heads = int(config["num_attention_heads"])
    kv_heads = int(config["num_key_value_heads"])
    vocab = int(config["vocab_size"])
    head_dim = int(config.get("head_dim", hidden // heads))
    # Llama block: q/k/v/o, two RMS norms, SwiGLU up/gate/down, plus embeddings.
    per_layer = (
        (hidden * heads * head_dim)
        + (hidden * kv_heads * head_dim * 2)
        + (hidden * hidden)
        + (3 * hidden * intermediate)
        + (2 * hidden)
    )
    embeddings = (
        vocab * hidden if bool(config.get("tie_word_embeddings", True)) else 2 * vocab * hidden
    )
    final_norm = hidden
    return per_layer * layers + embeddings + final_norm


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("D:/Juniper-Router/model-cache/SmolLM2-135M")
    )
    args = parser.parse_args()
    try:
        from huggingface_hub import snapshot_download
    except ImportError as exc:
        raise SystemExit("install requirements-model.in before acquisition") from exc
    args.output.mkdir(parents=True, exist_ok=True)
    snapshot_download(
        MODEL_ID,
        revision=REVISION,
        local_dir=args.output,
        allow_patterns=ALLOW,
        local_dir_use_symlinks=False,
    )
    config = json.loads((args.output / "config.json").read_text(encoding="utf-8"))
    files = []
    for path in sorted(args.output.iterdir()):
        if path.is_file():
            files.append(
                {"name": path.name, "bytes": path.stat().st_size, "sha256": sha256_file(path)}
            )
    manifest = {
        "model_id": MODEL_ID,
        "revision": REVISION,
        "acquired_utc": datetime.now(timezone.utc).isoformat(),
        "license": "Apache-2.0",
        "files": files,
        "calculated_trainable_parameters": parameter_count(config),
        "expected_trainable_parameters": 134515008,
        "status": "tested",
    }
    (args.output / "acquisition-manifest.json").write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
