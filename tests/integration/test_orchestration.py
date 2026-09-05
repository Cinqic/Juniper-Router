from juniper_router.contracts import Decision, Policy
from juniper_router.data.fixtures import default_registry
from juniper_router.runtime import HostOrchestrator, MockExecutor


def test_model_proposal_becomes_host_trusted_result():
    calls = {"count": 0}

    def provider(_messages, trusted):
        calls["count"] += 1
        if trusted is None:
            return Decision(
                "juniper-router-decision-v1",
                "use_tool",
                "ok",
                "calculator.evaluate",
                {"expression": "2+2"},
                None,
                "deterministic_tool_more_accurate",
                "high",
            )
        return Decision(
            "juniper-router-decision-v1",
            "complete",
            "ok",
            None,
            None,
            "The host calculator returned 4.",
            "successful_completion",
            "high",
        )

    executor = MockExecutor()
    outcome = HostOrchestrator().run(
        provider,
        user_text="calculate 2+2",
        registry=default_registry(),
        policy=Policy(),
        executor=executor,
        confirmed_targets=frozenset({"calculator.evaluate"}),
    )
    assert outcome.decision is not None and outcome.decision.decision == "complete"
    assert outcome.trusted_results[0].host_authored is True
    assert executor.calls == [("calculator.evaluate", {"expression": "2+2"})]
    assert calls["count"] == 2


def test_dry_run_does_not_execute():
    def provider(_messages, _trusted):
        return Decision(
            "juniper-router-decision-v1",
            "use_tool",
            "ok",
            "calculator.evaluate",
            {"expression": "2+2"},
            None,
            "deterministic_tool_more_accurate",
            "high",
        )

    executor = MockExecutor()
    outcome = HostOrchestrator().run(
        provider,
        user_text="calculate",
        registry=default_registry(),
        policy=Policy(),
        executor=executor,
        confirmed_targets=frozenset({"calculator.evaluate"}),
        dry_run=True,
    )
    assert outcome.decision is not None
    assert executor.calls == []


def test_executor_cannot_forge_or_mismatch_trusted_result():
    class ForgingExecutor:
        def execute(self, target_id, arguments):
            from juniper_router.contracts import TrustedResult

            return TrustedResult(
                "juniper-router-trusted-result-v1", "forged", "different.target", True, {}
            )

    def provider(_messages, _trusted):
        return Decision(
            "juniper-router-decision-v1",
            "use_tool",
            "ok",
            "calculator.evaluate",
            {"expression": "2+2"},
            None,
            "deterministic_tool_more_accurate",
            "high",
        )

    outcome = HostOrchestrator().run(
        provider,
        user_text="calculate 2+2",
        registry=default_registry(),
        policy=Policy(),
        executor=ForgingExecutor(),
        confirmed_targets=frozenset({"calculator.evaluate"}),
    )
    assert outcome.decision is None
    assert "does not match" in outcome.errors[0]


def test_cancellation_is_checked_between_rounds():
    def provider(_messages, _trusted):
        return Decision(
            "juniper-router-decision-v1",
            "wait",
            "error",
            None,
            None,
            None,
            "transient_failure",
            "medium",
        )

    outcome = HostOrchestrator().run(
        provider,
        user_text="wait",
        registry=default_registry(),
        policy=Policy(),
        executor=MockExecutor(),
        cancelled=lambda: True,
    )
    assert outcome.decision is None
    assert outcome.errors == ["request cancelled"]
