"""Bounded, opt-in JSONL audit logging with basic secret redaction."""

from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_SECRET = re.compile(r"(?i)(api[_-]?key|token|password|secret)(\s*[:=]\s*)[^,\s}]+")
_SECRET_KEYS = {"api_key", "apikey", "token", "password", "secret", "access_token"}


def _redact(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[REDACTED]" if key.lower() in _SECRET_KEYS else _redact(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [_redact(item) for item in value]
    return value


class AuditLogger:
    def __init__(self, path: Path | None = None, *, max_bytes: int = 1_000_000) -> None:
        self.path = path
        self.max_bytes = max_bytes

    def append(self, event: dict[str, Any]) -> None:
        if self.path is None:
            return
        self.path.parent.mkdir(parents=True, exist_ok=True)
        payload = _redact(dict(event))
        payload["timestamp_utc"] = datetime.now(timezone.utc).isoformat()
        encoded = _SECRET.sub(r"\1\2[REDACTED]", json.dumps(payload, sort_keys=True)) + "\n"
        if (
            self.path.exists()
            and self.path.stat().st_size + len(encoded.encode("utf-8")) > self.max_bytes
        ):
            raise ValueError("audit log size budget exhausted")
        with self.path.open("a", encoding="utf-8", newline="\n") as handle:
            handle.write(encoded)
