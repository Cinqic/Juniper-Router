"""Small deterministic registry used for contract tests and data generation."""

from __future__ import annotations

from juniper_router.contracts.models import Registry, Target


def _schema(*required: str, **properties: dict[str, object]) -> dict[str, object]:
    return {
        "type": "object",
        "properties": properties,
        "required": list(required),
        "additionalProperties": False,
    }


def default_registry(*, calculator_capability: str = "supported") -> Registry:
    return Registry(
        "juniper-router-registry-v1",
        (
            Target(
                "calculator.evaluate",
                "tool",
                calculator_capability,
                ("use_tool",),
                _schema("expression", expression={"type": "string", "maxLength": 256}),
                True,
                "local",
            ),
            Target(
                "search.query",
                "tool",
                "supported",
                ("use_tool",),
                _schema("query", query={"type": "string", "maxLength": 512}),
                True,
                "remote",
            ),
            Target(
                "coding.specialist",
                "model",
                "supported",
                ("delegate_model",),
                _schema("task", task={"type": "string", "maxLength": 2_000}),
                True,
                "local",
            ),
            Target(
                "strong.reasoner",
                "model",
                "supported",
                ("delegate_model",),
                _schema("task", task={"type": "string", "maxLength": 2_000}),
                True,
                "remote",
            ),
        ),
    )
