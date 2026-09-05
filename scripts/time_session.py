"""Append an honest work-session record without inventing end times."""

from __future__ import annotations

import argparse
import json
from datetime import datetime
from pathlib import Path
from uuid import uuid4


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--phase", required=True)
    parser.add_argument("--activity", required=True)
    parser.add_argument("--start", required=True)
    parser.add_argument("--end")
    parser.add_argument("--notes", required=True)
    args = parser.parse_args()
    start = datetime.fromisoformat(args.start.replace("Z", "+00:00"))
    end = datetime.fromisoformat(args.end.replace("Z", "+00:00")) if args.end else None
    record = {
        "record_id": str(uuid4()),
        "phase_id": args.phase,
        "activity_type": args.activity,
        "actor_role": "primary-engineer",
        "actor_id": "luna",
        "machine_id": "spend",
        "os_backend": "Windows/native",
        "start_utc": start.isoformat(),
        "end_utc": end.isoformat() if end else None,
        "elapsed_seconds": (end - start).total_seconds() if end else None,
        "evidence_type": "automatic" if end else "unavailable",
        "related_ids": [],
        "status": "open" if end is None else "completed",
        "notes": args.notes,
    }
    path = Path("docs/time/work-sessions.jsonl")
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8", newline="\n") as handle:
        handle.write(json.dumps(record, sort_keys=True) + "\n")
    print(record["record_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
