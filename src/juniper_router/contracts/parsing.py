"""Strict JSON parsing used at the model/host boundary."""

from __future__ import annotations

import json
from typing import Any


class JsonParseError(ValueError):
    """The payload is not valid JSON for an operational boundary."""


class DuplicateKeyError(JsonParseError):
    """A JSON object repeated a key, making its meaning ambiguous."""


def _pairs(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        result[key] = value
    return result


def _constant(value: str) -> Any:
    raise JsonParseError(f"non-standard JSON constant: {value}")


def parse_json_object(payload: str, *, max_chars: int = 64_000) -> dict[str, Any]:
    """Parse one finite JSON object with duplicate-key rejection."""

    if not isinstance(payload, str) or len(payload) > max_chars:
        raise JsonParseError("payload is missing or exceeds the JSON size limit")
    try:
        value = json.loads(
            payload,
            object_pairs_hook=_pairs,
            parse_constant=_constant,
        )
    except (json.JSONDecodeError, TypeError) as exc:
        raise JsonParseError(f"invalid JSON: {exc}") from exc
    if not isinstance(value, dict):
        raise JsonParseError("operational payload must be a JSON object")
    return value
