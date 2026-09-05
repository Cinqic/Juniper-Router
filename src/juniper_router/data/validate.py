"""Validation and contamination checks for the small reviewed dataset."""

from __future__ import annotations

import hashlib
import json
from collections import Counter
from pathlib import Path
from typing import Any, Iterable

from juniper_router.contracts.models import Decision, Registry


def validate_records(records: Iterable[dict[str, Any]]) -> dict[str, Any]:
    rows = list(records)
    errors: list[str] = []
    ids: set[str] = set()
    hashes: set[str] = set()
    lineages: dict[str, str] = {}
    decisions = Counter()
    for index, row in enumerate(rows):
        prefix = f"row {index}"
        required = {
            "schema_version",
            "example_id",
            "split",
            "curriculum_family",
            "lineage_id",
            "messages",
            "registry",
            "policy",
            "expected_decision",
            "source",
            "review_status",
            "quality_flags",
            "difficulty",
            "risk_tags",
            "renderer_version",
            "content_sha256",
        }
        if set(row) != required:
            errors.append(f"{prefix}: missing or extra keys")
            continue
        if row["example_id"] in ids:
            errors.append(f"{prefix}: duplicate example ID")
        ids.add(row["example_id"])
        if row["content_sha256"] in hashes:
            errors.append(f"{prefix}: duplicate content hash")
        hashes.add(row["content_sha256"])
        try:
            Registry.from_dict(row["registry"])
            decision = Decision.from_dict(row["expected_decision"])
            decisions[decision.decision] += 1
        except (ValueError, TypeError) as exc:
            errors.append(f"{prefix}: contract error: {exc}")
        canonical = json.dumps(
            {k: v for k, v in row.items() if k != "content_sha256"},
            sort_keys=True,
            separators=(",", ":"),
        )
        actual = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
        if actual != row["content_sha256"]:
            errors.append(f"{prefix}: content hash mismatch")
        prior = lineages.get(row["lineage_id"])
        if prior is not None and prior != row["split"]:
            errors.append(f"{prefix}: lineage crosses splits")
        lineages[row["lineage_id"]] = row["split"]
        if row["review_status"] not in {"primary-engineer-reviewed", "independent-reviewed"}:
            errors.append(f"{prefix}: record is not reviewed")
    return {
        "valid": not errors,
        "records": len(rows),
        "errors": errors,
        "decision_counts": dict(decisions),
        "duplicate_rate": 0.0 if len(rows) == len(ids) else 1.0,
    }


def load_jsonl(path: Path) -> list[dict[str, Any]]:
    return [
        json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()
    ]
