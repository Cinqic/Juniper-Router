"""A bounded host state machine; model output never crosses directly to execution."""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from typing import Any, Callable, Mapping, Protocol

from juniper_router.contracts.models import Decision, Policy, Registry, TrustedResult

from .audit import AuditLogger
from .validator import DecisionValidationError, HostValidator, ValidationContext


class Executor(Protocol):
    def execute(self, target_id: str, arguments: Mapping[str, Any]) -> TrustedResult: ...


@dataclass
class OrchestrationOutcome:
    decision: Decision | None
    trusted_results: list[TrustedResult] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)
    steps: int = 0


class MockExecutor:
    """Deterministic harmless fixtures used by tests and dry-run demos."""

    def __init__(self) -> None:
        self.calls: list[tuple[str, dict[str, Any]]] = []

    def execute(self, target_id: str, arguments: Mapping[str, Any]) -> TrustedResult:
        args = dict(arguments)
        self.calls.append((target_id, args))
        if target_id == "calculator.evaluate":
            expression = args["expression"]
            # The fixture intentionally handles only a closed set, never Python eval.
            values = {"2+2": 4, "6*7": 42, "10-3": 7}
            if expression not in values:
                return TrustedResult(
                    "juniper-router-trusted-result-v1",
                    str(uuid.uuid4()),
                    target_id,
                    False,
                    {"error": "fixture expression unavailable"},
                )
            return TrustedResult(
                "juniper-router-trusted-result-v1",
                str(uuid.uuid4()),
                target_id,
                True,
                {"value": values[expression]},
            )
        if target_id == "search.query":
            return TrustedResult(
                "juniper-router-trusted-result-v1",
                str(uuid.uuid4()),
                target_id,
                True,
                {"items": [], "query": args["query"]},
            )
        return TrustedResult(
            "juniper-router-trusted-result-v1",
            str(uuid.uuid4()),
            target_id,
            False,
            {"error": "no fixture"},
        )


class HostOrchestrator:
    def __init__(
        self, *, validator: HostValidator | None = None, audit: AuditLogger | None = None
    ) -> None:
        self.validator = validator or HostValidator()
        self.audit = audit or AuditLogger()

    def run(
        self,
        provider: Callable[[list[dict[str, Any]], TrustedResult | None], Decision],
        *,
        user_text: str,
        registry: Registry,
        policy: Policy,
        executor: Executor,
        confirmed_targets: frozenset[str] = frozenset(),
        dry_run: bool = False,
    ) -> OrchestrationOutcome:
        messages = [{"role": "user", "content": user_text, "trust": "untrusted_user"}]
        trusted: TrustedResult | None = None
        results: list[TrustedResult] = []
        errors: list[str] = []
        retries = 0
        for round_number in range(policy.max_rounds):
            decision = provider(messages, trusted)
            try:
                checked = self.validator.validate(
                    decision,
                    ValidationContext(
                        registry=registry,
                        policy=policy,
                        round_number=round_number,
                        step_number=len(results),
                        retry_count=retries,
                        confirmed_targets=confirmed_targets,
                        trusted_result=trusted.to_dict() if trusted else None,
                    ),
                )
            except (DecisionValidationError, ValueError) as exc:
                errors.append(str(exc))
                self.audit.append({"event": "decision_rejected", "error": str(exc)})
                return OrchestrationOutcome(None, results, errors, len(results))
            self.audit.append(
                {
                    "event": "decision_validated",
                    "decision": checked.decision,
                    "target_id": checked.target_id,
                }
            )
            if checked.decision in {
                "use_tool",
                "delegate_model",
                "delegate_agent",
                "delegate_subagent",
            }:
                if dry_run:
                    return OrchestrationOutcome(checked, results, errors, len(results))
                assert checked.target_id is not None and checked.arguments is not None
                trusted = executor.execute(checked.target_id, checked.arguments)
                results.append(trusted)
                messages.append(
                    {"role": "tool_result", "content": trusted.to_dict(), "trust": "trusted_host"}
                )
                continue
            if checked.decision == "retry":
                retries += 1
                continue
            return OrchestrationOutcome(checked, results, errors, len(results))
        errors.append("orchestration round budget exhausted")
        self.audit.append({"event": "orchestration_stopped", "error": errors[-1]})
        return OrchestrationOutcome(None, results, errors, len(results))
