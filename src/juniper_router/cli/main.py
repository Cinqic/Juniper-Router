"""Small local CLI for contract inspection and safe mock orchestration."""

from __future__ import annotations

import argparse
import json

from juniper_router.contracts import Decision
from juniper_router.data.fixtures import default_registry
from juniper_router.data.generate import build_records
from juniper_router.data.validate import validate_records
from juniper_router.rendering.chatml import render_router_prompt
from juniper_router.runtime import HostOrchestrator, MockExecutor


def _rule_provider(user_text: str, confirmed: bool):
    def provider(_messages, _trusted):
        low = user_text.lower()
        if low.startswith(("hi", "hello", "what's up")):
            return Decision(
                "juniper-router-decision-v1",
                "answer_directly",
                "ok",
                None,
                None,
                "Not much. Existing locally and routing requests.",
                "direct_answer_within_capability",
                "high",
            )
        if "calculate" in low or "compute" in low:
            expr = "2+2" if "2 + 2" in low or "2+2" in low else "6*7" if "6*7" in low else None
            if expr is None:
                return Decision(
                    "juniper-router-decision-v1",
                    "clarify",
                    "insufficient_context",
                    None,
                    None,
                    "What expression should I calculate?",
                    "missing_required_argument",
                    "high",
                )
            return Decision(
                "juniper-router-decision-v1",
                "use_tool",
                "ok",
                "calculator.evaluate",
                {"expression": expr},
                None,
                "deterministic_tool_more_accurate",
                "high",
            )
        if "today" in low or "latest" in low or "current" in low:
            return Decision(
                "juniper-router-decision-v1",
                "use_tool",
                "ok",
                "search.query",
                {"query": user_text},
                None,
                "fresh_information_required",
                "high",
            )
        return Decision(
            "juniper-router-decision-v1",
            "escalate",
            "capability_exceeded",
            None,
            None,
            "I don't have enough evidence to route that safely.",
            "capability_exceeded",
            "low",
        )

    return provider


def main() -> int:
    parser = argparse.ArgumentParser(prog="juniper-router")
    sub = parser.add_subparsers(dest="command", required=True)
    inspect = sub.add_parser("inspect")
    inspect.add_argument("--registry", action="store_true")
    prompt = sub.add_parser("prompt")
    prompt.add_argument("text")
    route = sub.add_parser("route")
    route.add_argument("text")
    route.add_argument("--confirm", action="store_true")
    sub.add_parser("data-check")
    args = parser.parse_args()
    if args.command == "inspect":
        print(json.dumps(default_registry().to_dict(), indent=2, sort_keys=True))
    elif args.command == "prompt":
        print(
            render_router_prompt(
                args.text, registry=default_registry().to_dict(), policy={"max_rounds": 4}
            )
        )
    elif args.command == "route":
        executor = MockExecutor()
        outcome = HostOrchestrator().run(
            _rule_provider(args.text, args.confirm),
            user_text=args.text,
            registry=default_registry(),
            policy=__import__("juniper_router.contracts", fromlist=["Policy"]).Policy(),
            executor=executor,
            confirmed_targets=frozenset({"calculator.evaluate", "search.query"})
            if args.confirm
            else frozenset(),
        )
        print(
            json.dumps(
                {
                    "decision": outcome.decision.to_dict() if outcome.decision else None,
                    "trusted_results": [r.to_dict() for r in outcome.trusted_results],
                    "errors": outcome.errors,
                    "steps": outcome.steps,
                },
                indent=2,
                sort_keys=True,
            )
        )
    else:
        result = validate_records(build_records())
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0 if result["valid"] else 1
    return 0
