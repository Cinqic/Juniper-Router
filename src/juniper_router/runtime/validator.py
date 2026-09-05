"""Fail-closed validation after model output has been parsed."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from juniper_router.contracts.models import Decision, Policy, Registry, Target, TrustedResult


class DecisionValidationError(ValueError):
    """A decision cannot be safely admitted to the host state machine."""


@dataclass(frozen=True)
class ValidationContext:
    registry: Registry
    policy: Policy
    round_number: int = 0
    step_number: int = 0
    retry_count: int = 0
    confirmed_targets: frozenset[str] = frozenset()
    trusted_result: Mapping[str, Any] | None = None


class HostValidator:
    """Schema-independent semantic policy checks for operational decisions."""

    def validate(self, decision: Decision, context: ValidationContext) -> Decision:
        if decision.schema_version != "juniper-router-decision-v1":
            raise DecisionValidationError("unsupported decision schema")
        if context.round_number >= context.policy.max_rounds:
            raise DecisionValidationError("round budget exhausted")
        self._check_shape(decision)
        if decision.decision in {
            "use_tool",
            "delegate_model",
            "delegate_agent",
            "delegate_subagent",
        }:
            if context.step_number >= context.policy.max_steps:
                raise DecisionValidationError("step budget exhausted")
            self._check_target(decision, context)
        elif decision.decision == "complete":
            if not isinstance(context.trusted_result, TrustedResult):
                raise DecisionValidationError("completion requires a host-authored trusted result")
        elif decision.decision == "continue_orchestration":
            if context.step_number >= context.policy.max_steps:
                raise DecisionValidationError("step budget exhausted")
        elif decision.decision == "retry":
            if context.retry_count >= context.policy.max_retries:
                raise DecisionValidationError("retry budget exhausted")
        return decision

    def _check_shape(self, decision: Decision) -> None:
        terminal_without_target = {
            "answer_directly",
            "clarify",
            "refuse",
            "escalate",
            "wait",
            "retry",
            "continue_orchestration",
            "complete",
        }
        if decision.decision in terminal_without_target and decision.target_id is not None:
            raise DecisionValidationError("decision cannot name a target")
        if decision.decision in terminal_without_target and decision.arguments is not None:
            raise DecisionValidationError("decision cannot carry executable arguments")
        if decision.decision in {"answer_directly", "clarify", "refuse", "escalate"}:
            if not decision.message or not decision.message.strip():
                raise DecisionValidationError("human-facing decision requires a message")
        if decision.decision == "answer_directly" and decision.status != "ok":
            raise DecisionValidationError("direct answer must have ok status")
        if decision.decision == "clarify" and decision.status != "insufficient_context":
            raise DecisionValidationError("clarify must have insufficient_context status")
        if decision.decision == "escalate" and decision.status not in {
            "capability_exceeded",
            "unknown",
            "error",
        }:
            raise DecisionValidationError("escalation status must explain the escalation")
        if decision.decision == "complete" and decision.status != "ok":
            raise DecisionValidationError("complete must have ok status")

    def _check_target(self, decision: Decision, context: ValidationContext) -> Target:
        if not decision.target_id:
            raise DecisionValidationError("delegation requires target_id")
        target = context.registry.find(decision.target_id)
        if target is None:
            raise DecisionValidationError("unknown target ID")
        if target.capability != "supported":
            raise DecisionValidationError(
                f"target capability is {target.capability}, not supported"
            )
        if decision.decision not in target.accepts:
            raise DecisionValidationError("target does not accept this decision kind")
        if target.requires_confirmation and target.target_id not in context.confirmed_targets:
            raise DecisionValidationError("target requires explicit confirmation")
        if decision.arguments is None:
            raise DecisionValidationError("delegation requires arguments object")
        self._validate_arguments(decision.arguments, target.argument_schema)
        return target

    @staticmethod
    def _validate_arguments(arguments: Mapping[str, Any], schema: Mapping[str, Any]) -> None:
        required = schema.get("required", [])
        properties = schema.get("properties", {})
        if schema.get("additionalProperties") is False:
            unknown = set(arguments) - set(properties)
            if unknown:
                raise DecisionValidationError(f"unknown argument fields: {sorted(unknown)}")
        missing = set(required) - set(arguments)
        if missing:
            raise DecisionValidationError(f"missing argument fields: {sorted(missing)}")
        for name, spec in properties.items():
            if name not in arguments:
                continue
            value = arguments[name]
            if spec.get("type") == "string" and not isinstance(value, str):
                raise DecisionValidationError(f"argument {name} must be a string")
            if spec.get("type") == "integer" and (
                not isinstance(value, int) or isinstance(value, bool)
            ):
                raise DecisionValidationError(f"argument {name} must be an integer")
            if (
                spec.get("maxLength") is not None
                and isinstance(value, str)
                and len(value) > spec["maxLength"]
            ):
                raise DecisionValidationError(f"argument {name} exceeds maxLength")
