# ruff: noqa: E402

"""Build the expanded v2 training corpus and freeze its held-out test split."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.data.expanded import DATASET_VERSION, build_expanded_records
from juniper_router.data.validate import validate_records
from juniper_router.provenance.hashing import sha256_file


def _write(path: Path, rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
        newline="\n",
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dataset", type=Path, default=Path("data/generated/juniper-router-dataset-v2.jsonl")
    )
    parser.add_argument("--eval", type=Path, default=Path("evals/frozen/router-eval-v2.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("evals/manifests/formal-v2.json"))
    args = parser.parse_args()
    rows = build_expanded_records()
    result = validate_records(rows, strict_duplicates=True)
    if not result["valid"]:
        raise SystemExit("expanded data validation failed: " + "; ".join(result["errors"][:20]))
    _write(args.dataset, rows)
    formal = [row for row in rows if row["split"] == "test"]
    _write(args.eval, formal)
    manifest = {
        "manifest_version": "juniper-router-eval-manifest-v2",
        "dataset_version": DATASET_VERSION,
        "dataset_path": str(args.dataset).replace("\\", "/"),
        "dataset_sha256": sha256_file(args.dataset),
        "dataset_examples": len(rows),
        "eval_path": str(args.eval).replace("\\", "/"),
        "eval_sha256": sha256_file(args.eval),
        "examples": len(formal),
        "renderer_version": "chatml-router-compact-v1",
        "policy": "configs/evaluation/formal-policy-v2.json",
        "split": "test",
        "status": "frozen",
        "review_status": "generated-stratified-reviewed; independent review pending",
    }
    args.manifest.parent.mkdir(parents=True, exist_ok=True)
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps({**result, **manifest}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
