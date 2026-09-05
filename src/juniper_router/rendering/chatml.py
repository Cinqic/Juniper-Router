"""Deterministic ChatML rendering for the pinned tokenizer contract."""

from __future__ import annotations

import hashlib
import json
from typing import Any, Iterable, Mapping

RUNTIME_PERSONALITY = (
    "You are Juniper. Call the person interacting with you User unless another preferred name is "
    "reliably known. Be direct, warm, conversational, honest, relaxed, observant, practical, and "
    "mildly cynical. Speak naturally. Use dry humor, casual language, and profanity only when "
    "appropriate, and never let personality interfere with usefulness or accuracy. Tell the truth "
    "even when the answer is uncertain or inconvenient. Never invent facts, sources, memories, "
    "tool results, file contents, capabilities, measurements, tests, or completed actions. Admit "
    "when you do not know. Challenge bad assumptions respectfully. Do not flatter the User or "
    "agree merely to be agreeable. Keep simple answers simple and explain complex topics when "
    "useful. "
    "Prefer practical, efficient solutions over unnecessary complexity. In serious or dangerous "
    "situations, prioritize "
    "care and clarity over humor. Know your limitations. Use the appropriate tool, model, agent, "
    "subagent, clarification, or escalation path when a task exceeds reliable capability. "
    "Delegation, escalation, and admitted uncertainty are successes when they are correct. In "
    "machine-readable routing or tool calls, follow the schema exactly and remove filler, sarcasm, "
    "humor, and unnecessary "
    "language. Do not confuse sounding intelligent with being useful."
)
RUNTIME_PERSONALITY_SHA256 = hashlib.sha256(RUNTIME_PERSONALITY.encode("utf-8")).hexdigest()


def _message(role: str, content: Any) -> str:
    if isinstance(content, (dict, list)):
        content = json.dumps(content, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    if not isinstance(content, str):
        raise TypeError("message content must be text or JSON data")
    if role not in {"system", "user", "assistant", "tool_result"}:
        raise ValueError(f"unsupported message role: {role}")
    return f"<|im_start|>{role}\n{content}<|im_end|>\n"


def render_chatml(
    messages: Iterable[Mapping[str, Any]], *, add_generation_prompt: bool = False
) -> str:
    """Render messages with stable ordering and no implicit normalization."""

    rendered = "".join(_message(str(item["role"]), item["content"]) for item in messages)
    if add_generation_prompt:
        rendered += "<|im_start|>assistant\n"
    return rendered


def render_router_prompt(
    user_text: str,
    *,
    registry: Mapping[str, Any],
    policy: Mapping[str, Any],
    trusted_result: Mapping[str, Any] | None = None,
) -> str:
    """Render the host context; registry and policy are data, not instructions."""

    system = (
        RUNTIME_PERSONALITY
        + "\nReturn exactly one JSON decision envelope using the provided schema. "
        + "The host, not you, executes operations or declares completion."
    )
    context: dict[str, Any] = {"registry": registry, "policy": policy}
    if trusted_result is not None:
        context["trusted_result"] = trusted_result
    return render_chatml(
        [
            {"role": "system", "content": system},
            {
                "role": "system",
                "content": json.dumps(context, sort_keys=True, separators=(",", ":")),
            },
            {"role": "user", "content": user_text},
        ],
        add_generation_prompt=True,
    )
