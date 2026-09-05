from __future__ import annotations

# ruff: noqa: E402
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.data.generate import build_records, write_records
from juniper_router.data.validate import validate_records
from juniper_router.provenance.hashing import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output", type=Path, default=Path("data/generated/juniper-router-dataset-v1.jsonl")
    )
    args = parser.parse_args()
    records = build_records()
    result = validate_records(records)
    if not result["valid"]:
        raise SystemExit("data validation failed: " + "; ".join(result["errors"]))
    write_records(args.output, records)
    stats = {
        **result,
        "sha256": sha256_file(args.output),
        "path": str(args.output).replace("\\", "/"),
        "status": "tested",
    }
    args.output.with_suffix(".stats.json").write_text(
        json.dumps(stats, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(stats, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
