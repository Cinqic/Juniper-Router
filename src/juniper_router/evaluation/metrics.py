"""Small, dependency-free metrics for frozen routing evaluations."""

from __future__ import annotations

from collections import Counter, defaultdict
from typing import Any, Iterable, Mapping

from juniper_router.contracts.models import Decision, Registry, TrustedResult
from juniper_router.runtime.validator import HostValidator, ValidationContext


def evaluate_predictions(rows: Iterable[Mapping[str, Any]]) -> dict[str, Any]:
    rows = list(rows)
    decision_correct = 0
    target_correct = 0
    semantic_pass = 0
    syntactic_valid = 0
    expected = Counter()
    predicted = Counter()
    per_class: dict[str, dict[str, int]] = defaultdict(lambda: {"tp": 0, "fp": 0, "fn": 0})
    invalid = 0
    target_required = 0
    target_correct_required = 0
    argument_required = 0
    argument_correct = 0
    clarification_required = 0
    clarification_correct = 0
    critical_escalation_required = 0
    critical_escalation_correct = 0
    for row in rows:
        gold = row["expected_decision"]
        raw = row.get("prediction")
        gold_decision = gold["decision"]
        expected[gold_decision] += 1
        if gold.get("arguments") is not None:
            argument_required += 1
        if gold.get("target_id") is not None:
            target_required += 1
        if gold_decision == "clarify":
            clarification_required += 1
        if gold_decision == "escalate" and "high-risk" in row.get("risk_tags", []):
            critical_escalation_required += 1
        if isinstance(raw, dict):
            try:
                candidate = Decision.from_dict(raw)
                syntactic_valid += 1
                predicted[candidate.decision] += 1
                if candidate.decision == gold_decision:
                    decision_correct += 1
                    per_class[gold_decision]["tp"] += 1
                else:
                    per_class[gold_decision]["fn"] += 1
                    per_class[candidate.decision]["fp"] += 1
                if candidate.target_id == gold.get("target_id"):
                    target_correct += 1
                    if gold.get("target_id") is not None:
                        target_correct_required += 1
                if gold.get("arguments") is not None and candidate.arguments == gold["arguments"]:
                    argument_correct += 1
                if gold_decision == "clarify" and candidate.decision == "clarify":
                    clarification_correct += 1
                if (
                    gold_decision == "escalate"
                    and "high-risk" in row.get("risk_tags", [])
                    and candidate.decision == "escalate"
                ):
                    critical_escalation_correct += 1
                registry = Registry.from_dict(row["registry"])
                confirmed = frozenset(target.target_id for target in registry.targets)
                HostValidator().validate(
                    candidate,
                    ValidationContext(
                        registry=registry,
                        policy=_policy(row),
                        confirmed_targets=confirmed,
                        trusted_result=(
                            TrustedResult(
                                "juniper-router-trusted-result-v1",
                                "evaluation-fixture",
                                "evaluation.fixture",
                                True,
                                {"evaluation_fixture": True},
                            )
                            if candidate.decision == "complete"
                            else None
                        ),
                    ),
                )
                semantic_pass += 1
            except (ValueError, TypeError):
                invalid += 1
                per_class[gold_decision]["fn"] += 1
        else:
            invalid += 1
            per_class[gold_decision]["fn"] += 1
    f1_values = []
    for name in expected:
        item = per_class[name]
        precision = item["tp"] / (item["tp"] + item["fp"]) if item["tp"] + item["fp"] else 0.0
        recall = item["tp"] / (item["tp"] + item["fn"]) if item["tp"] + item["fn"] else 0.0
        f1_values.append(
            2 * precision * recall / (precision + recall) if precision + recall else 0.0
        )
    total = len(rows)
    per_decision = {}
    for name in expected:
        item = per_class[name]
        precision = item["tp"] / (item["tp"] + item["fp"]) if item["tp"] + item["fp"] else 0.0
        recall = item["tp"] / (item["tp"] + item["fn"]) if item["tp"] + item["fn"] else 0.0
        per_decision[name] = {
            **item,
            "support": expected[name],
            "precision": precision,
            "recall": recall,
            "f1": 2 * precision * recall / (precision + recall)
            if precision + recall
            else 0.0,
        }
    return {
        "examples": total,
        "valid_predictions": syntactic_valid,
        "invalid_predictions": invalid,
        "decision_accuracy": decision_correct / total if total else 0.0,
        "target_accuracy": target_correct / total if total else 0.0,
        "target_accuracy_when_required": (
            target_correct_required / target_required if target_required else 0.0
        ),
        "argument_semantic_correctness": (
            argument_correct / argument_required if argument_required else 0.0
        ),
        "clarification_required_accuracy": (
            clarification_correct / clarification_required if clarification_required else 0.0
        ),
        "critical_escalation_recall": (
            critical_escalation_correct / critical_escalation_required
            if critical_escalation_required
            else 0.0
        ),
        "raw_syntactic_validity": syntactic_valid / total if total else 0.0,
        "semantic_validator_pass": semantic_pass / total if total else 0.0,
        "macro_f1": sum(f1_values) / len(f1_values) if f1_values else 0.0,
        "expected_decisions": dict(expected),
        "predicted_decisions": dict(predicted),
        "per_decision": per_decision,
    }


def _policy(row: Mapping[str, Any]):
    from juniper_router.contracts.models import Policy

    return Policy(
        **{
            key: row["policy"][key]
            for key in ("max_rounds", "max_steps", "max_retries")
            if key in row["policy"]
        }
    )
