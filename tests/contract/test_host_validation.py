import pytest

from juniper_router.contracts import Decision, Policy
from juniper_router.data.fixtures import default_registry
from juniper_router.runtime.validator import (
    DecisionValidationError,
    HostValidator,
    ValidationContext,
)


def decision(**overrides):
    value = {
        "schema_version": "juniper-router-decision-v1",
        "decision": "answer_directly",
        "status": "ok",
        "target_id": None,
        "arguments": None,
        "message": "ok",
        "reason_code": "direct_answer_within_capability",
        "confidence": "high",
    }
    value.update(overrides)
    return Decision.from_dict(value)


def context(**kwargs):
    return ValidationContext(registry=default_registry(), policy=Policy(), **kwargs)


def test_unknown_target_fails_closed():
    with pytest.raises(DecisionValidationError, match="unknown target"):
        HostValidator().validate(
            decision(decision="use_tool", target_id="magic.shell", arguments={}),
            context(confirmed_targets=frozenset()),
        )


def test_unknown_capability_fails_closed():
    registry = default_registry(calculator_capability="unknown")
    with pytest.raises(DecisionValidationError, match="capability"):
        HostValidator().validate(
            decision(
                decision="use_tool",
                target_id="calculator.evaluate",
                arguments={"expression": "2+2"},
            ),
            ValidationContext(
                registry, Policy(), confirmed_targets=frozenset({"calculator.evaluate"})
            ),
        )


def test_permission_is_checked_after_schema():
    with pytest.raises(DecisionValidationError, match="confirmation"):
        HostValidator().validate(
            decision(
                decision="use_tool",
                target_id="calculator.evaluate",
                arguments={"expression": "2+2"},
            ),
            context(),
        )


def test_arguments_are_schema_checked():
    with pytest.raises(DecisionValidationError, match="unknown argument"):
        HostValidator().validate(
            decision(
                decision="use_tool",
                target_id="calculator.evaluate",
                arguments={"expression": "2+2", "shell": "del"},
            ),
            context(confirmed_targets=frozenset({"calculator.evaluate"})),
        )


def test_completion_requires_trusted_result():
    with pytest.raises(DecisionValidationError, match="trusted"):
        HostValidator().validate(
            decision(decision="complete", reason_code="successful_completion"), context()
        )
