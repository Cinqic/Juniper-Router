import pytest

from juniper_router.contracts import Decision, DuplicateKeyError, Registry, parse_json_object
from juniper_router.data.fixtures import default_registry
from juniper_router.rendering.chatml import render_router_prompt


def valid_decision(**overrides):
    value = {
        "schema_version": "juniper-router-decision-v1",
        "decision": "answer_directly",
        "status": "ok",
        "target_id": None,
        "arguments": None,
        "message": "hello",
        "reason_code": "direct_answer_within_capability",
        "confidence": "high",
    }
    value.update(overrides)
    return value


def test_decision_round_trip_is_exact():
    value = valid_decision()
    assert Decision.from_dict(value).to_dict() == value


def test_extra_fields_are_rejected():
    with pytest.raises(ValueError, match="extra"):
        Decision.from_dict({**valid_decision(), "extra": 1})


def test_duplicate_keys_are_rejected():
    with pytest.raises(DuplicateKeyError):
        parse_json_object('{"a": 1, "a": 2}')


def test_nan_is_rejected():
    with pytest.raises(ValueError):
        parse_json_object('{"a": NaN}')


def test_registry_does_not_coerce_permission_types():
    value = default_registry().to_dict()
    value["targets"][0]["requires_confirmation"] = "false"
    with pytest.raises(ValueError, match="boolean"):
        Registry.from_dict(value)


def test_compact_router_prompt_preserves_dynamic_registry_and_policy():
    prompt = render_router_prompt(
        "Calculate 2+2",
        registry=default_registry().to_dict(),
        policy={"max_steps": 8},
        compact=True,
    )
    assert "calculator.evaluate" in prompt
    assert "max_steps" in prompt
    assert "<|im_start|>assistant\n" in prompt
