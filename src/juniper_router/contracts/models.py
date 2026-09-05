"""Typed contract values and closed vocabularies for Juniper Router."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping

DECISIONS = (
    "answer_directly",
    "use_tool",
    "delegate_model",
    "delegate_agent",
    "delegate_subagent",
    "escalate",
    "clarify",
    "refuse",
    "retry",
    "wait",
    "continue_orchestration",
    "complete",
)
STATUSES = ("ok", "insufficient_context", "capability_exceeded", "unknown", "error")
CONFIDENCES = ("high", "medium", "low")
CAPABILITIES = ("supported", "unsupported", "unknown")
REASON_CODES = (
    "direct_answer_within_capability",
    "deterministic_tool_more_accurate",
    "fresh_information_required",
    "missing_required_argument",
    "ambiguous_target",
    "insufficient_context",
    "capability_unknown",
    "capability_exceeded",
    "risk_requires_escalation",
    "permission_denied",
    "privacy_conflict",
    "budget_exhausted",
    "malformed_or_untrusted_result",
    "transient_failure",
    "terminal_failure",
    "user_cancelled",
    "successful_completion",
    "unsupported_schema_version",
    "unknown_target",
)
TRUST_LABELS = ("trusted_host", "untrusted_user", "untrusted_model", "untrusted_tool")


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _string(value: Any, name: str, *, allow_empty: bool = False) -> str:
    _require(isinstance(value, str), f"{name} must be a string")
    if not allow_empty:
        _require(bool(value.strip()), f"{name} must not be empty")
    return value


def _object(value: Any, name: str) -> dict[str, Any]:
    _require(isinstance(value, dict), f"{name} must be an object")
    return dict(value)


@dataclass(frozen=True)
class Decision:
    schema_version: str
    decision: str
    status: str
    target_id: str | None
    arguments: dict[str, Any] | None
    message: str | None
    reason_code: str
    confidence: str

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Decision":
        required = {
            "schema_version",
            "decision",
            "status",
            "target_id",
            "arguments",
            "message",
            "reason_code",
            "confidence",
        }
        _require(set(value) == required, "decision has missing or extra top-level keys")
        decision = cls(
            schema_version=_string(value["schema_version"], "schema_version"),
            decision=_string(value["decision"], "decision"),
            status=_string(value["status"], "status"),
            target_id=value["target_id"],
            arguments=value["arguments"],
            message=value["message"],
            reason_code=_string(value["reason_code"], "reason_code"),
            confidence=_string(value["confidence"], "confidence"),
        )
        _require(
            cls.schema_version_is_valid(decision.schema_version), "unsupported decision schema"
        )
        _require(decision.decision in DECISIONS, "unknown decision")
        _require(decision.status in STATUSES, "unknown status")
        _require(decision.reason_code in REASON_CODES, "unknown reason code")
        _require(decision.confidence in CONFIDENCES, "unknown confidence")
        _require(
            decision.target_id is None or isinstance(decision.target_id, str),
            "target_id must be string or null",
        )
        _require(
            decision.arguments is None or isinstance(decision.arguments, dict),
            "arguments must be object or null",
        )
        _require(
            decision.message is None or isinstance(decision.message, str),
            "message must be string or null",
        )
        return decision

    @staticmethod
    def schema_version_is_valid(value: str) -> bool:
        return value == "juniper-router-decision-v1"

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "decision": self.decision,
            "status": self.status,
            "target_id": self.target_id,
            "arguments": self.arguments,
            "message": self.message,
            "reason_code": self.reason_code,
            "confidence": self.confidence,
        }


@dataclass(frozen=True)
class Target:
    target_id: str
    target_type: str
    capability: str
    accepts: tuple[str, ...] = ()
    argument_schema: dict[str, Any] = field(default_factory=dict)
    requires_confirmation: bool = True
    locality: str = "local"

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Target":
        allowed = {
            "target_id",
            "target_type",
            "capability",
            "accepts",
            "argument_schema",
            "requires_confirmation",
            "locality",
        }
        _require(set(value) == allowed, "target has missing or extra keys")
        _require(isinstance(value["accepts"], list), "target accepts must be an array")
        _require(
            isinstance(value["requires_confirmation"], bool),
            "target requires_confirmation must be boolean",
        )
        target = cls(
            target_id=_string(value["target_id"], "target_id"),
            target_type=_string(value["target_type"], "target_type"),
            capability=_string(value["capability"], "capability"),
            accepts=tuple(value["accepts"]),
            argument_schema=_object(value["argument_schema"], "argument_schema"),
            requires_confirmation=value["requires_confirmation"],
            locality=_string(value["locality"], "locality"),
        )
        _require(target.capability in CAPABILITIES, "unknown capability state")
        _require(
            all(isinstance(item, str) and item in DECISIONS for item in target.accepts),
            "invalid target decision",
        )
        return target

    def to_dict(self) -> dict[str, Any]:
        return {
            "target_id": self.target_id,
            "target_type": self.target_type,
            "capability": self.capability,
            "accepts": list(self.accepts),
            "argument_schema": self.argument_schema,
            "requires_confirmation": self.requires_confirmation,
            "locality": self.locality,
        }


@dataclass(frozen=True)
class Registry:
    schema_version: str
    targets: tuple[Target, ...]

    @classmethod
    def from_dict(cls, value: Mapping[str, Any]) -> "Registry":
        _require(set(value) == {"schema_version", "targets"}, "registry has missing or extra keys")
        _require(
            value["schema_version"] == "juniper-router-registry-v1", "unsupported registry schema"
        )
        targets = tuple(Target.from_dict(item) for item in value["targets"])
        _require(
            len({item.target_id for item in targets}) == len(targets),
            "registry target IDs must be unique",
        )
        return cls(value["schema_version"], targets)

    def find(self, target_id: str) -> Target | None:
        return next((item for item in self.targets if item.target_id == target_id), None)

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "targets": [item.to_dict() for item in self.targets],
        }


@dataclass(frozen=True)
class Policy:
    schema_version: str = "juniper-router-policy-v1"
    max_rounds: int = 4
    max_steps: int = 8
    max_retries: int = 2
    max_payload_chars: int = 64_000
    network_allowed: bool = False
    audit_enabled: bool = False

    def __post_init__(self) -> None:
        _require(self.schema_version == "juniper-router-policy-v1", "unsupported policy schema")
        _require(1 <= self.max_rounds <= 16, "max_rounds outside safe bound")
        _require(1 <= self.max_steps <= 64, "max_steps outside safe bound")
        _require(0 <= self.max_retries <= 8, "max_retries outside safe bound")
        _require(1_024 <= self.max_payload_chars <= 1_000_000, "payload bound outside safe range")


@dataclass(frozen=True)
class TrustedResult:
    schema_version: str
    result_id: str
    target_id: str
    success: bool
    payload: dict[str, Any]
    host_authored: bool = True
    provenance: str = "host"

    def __post_init__(self) -> None:
        _require(
            self.schema_version == "juniper-router-trusted-result-v1", "unsupported result schema"
        )
        _string(self.result_id, "result_id")
        _string(self.target_id, "target_id")
        _require(isinstance(self.success, bool), "trusted result success must be boolean")
        _require(self.host_authored is True, "trusted results must be host-authored")
        _require(isinstance(self.payload, dict), "trusted result payload must be an object")
        _require(self.provenance == "host", "trusted result provenance must be host")

    def to_dict(self) -> dict[str, Any]:
        return {
            "schema_version": self.schema_version,
            "result_id": self.result_id,
            "target_id": self.target_id,
            "success": self.success,
            "payload": self.payload,
            "host_authored": self.host_authored,
            "provenance": self.provenance,
        }


@dataclass(frozen=True)
class RouterInput:
    schema_version: str
    user_text: str
    registry: Registry
    policy: Policy
    trusted_result: TrustedResult | None = None
    context: tuple[dict[str, str], ...] = ()

    def __post_init__(self) -> None:
        _require(self.schema_version == "juniper-router-input-v1", "unsupported input schema")
        _require(1 <= len(self.user_text) <= 32_000, "user_text outside bound")
