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


def test_metrics_count_required_targets_when_predictions_are_invalid():
    from juniper_router.evaluation.metrics import evaluate_predictions

    row = {
        "expected_decision": valid_decision(
            decision="use_tool",
            status="ok",
            target_id="calculator.evaluate",
            arguments={"expression": "2+2"},
            message=None,
            reason_code="deterministic_tool_more_accurate",
        ),
        "prediction": None,
        "registry": {"schema_version": "juniper-router-registry-v1", "targets": []},
        "policy": {"max_rounds": 1, "max_steps": 1, "max_retries": 0},
    }

    metrics = evaluate_predictions([row])
    assert metrics["invalid_predictions"] == 1
    assert metrics["target_accuracy_when_required"] == 0.0


def test_ordered_training_target_leads_with_decision_field():
    from juniper_router.training.sft import _serialize_target

    target = valid_decision(decision="use_tool", target_id="calculator.evaluate")
    assert _serialize_target(target, "ordered-v1").startswith(
        '{"schema_version":"juniper-router-decision-v1","decision":"use_tool"'
    )
    assert _serialize_target(target, "sorted-keys-v1").startswith('{"arguments":null,"confidence"')
