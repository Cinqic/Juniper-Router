from __future__ import annotations

# ruff: noqa: E402
import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from juniper_router.data.generate import build_records
from juniper_router.data.validate import validate_records
from juniper_router.provenance.hashing import sha256_file


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=Path("evals/frozen/router-eval-v1.jsonl"))
    parser.add_argument("--manifest", type=Path, default=Path("evals/manifests/frozen-v1.json"))
    args = parser.parse_args()
    records = [row for row in build_records() if row["split"] in {"dev", "test"}]
    result = validate_records(records)
    if not result["valid"]:
        raise SystemExit("cannot freeze invalid data: " + "; ".join(result["errors"]))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(
        "".join(json.dumps(row, ensure_ascii=False, sort_keys=True) + "\n" for row in records),
        encoding="utf-8",
        newline="\n",
    )
    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    manifest.update(
        {
            "dataset_path": str(args.output).replace("\\", "/"),
            "examples": len(records),
            "sha256": sha256_file(args.output),
            "status": "frozen",
        }
    )
    args.manifest.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    print(json.dumps(manifest, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
