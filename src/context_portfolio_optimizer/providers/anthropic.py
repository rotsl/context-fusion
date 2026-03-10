# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Anthropic provider adapter."""

from __future__ import annotations

import os
from typing import Any

from .base import BaseAdapter, ProviderCapabilities
from .tokenizers import estimate_provider_tokens


class AnthropicProvider(BaseAdapter):
    """Anthropic provider adapter using the official SDK."""

    def __init__(self, api_key: str | None = None):
        try:
            import anthropic
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError("anthropic package required for AnthropicProvider") from exc
        self.client = anthropic.Anthropic(api_key=api_key or os.getenv("ANTHROPIC_API_KEY"))

    def name(self) -> str:
        return "anthropic"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_tools=True,
            supports_structured_output=True,
            supports_prompt_cache=True,
            supports_system_messages=True,
            local=False,
        )

    def estimate_tokens(self, text: str, model: str) -> int:
        return estimate_provider_tokens(self.name(), text, model)

    def build_request(
        self,
        compiled_packet: dict[str, Any],
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        request = dict(compiled_packet.get("request", {}))
        request.setdefault("model", model)
        request.setdefault("messages", compiled_packet.get("messages", []))
        request.update(kwargs)
        return request

    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        system_prompt, chat_messages = _anthropic_message_payload(messages)
        response = self.client.messages.create(
            model=model,
            messages=chat_messages,
            system=system_prompt,
            **kwargs,
        )
        content = []
        for block in response.content:
            text = getattr(block, "text", "")
            if text:
                content.append(text)
        return {
            "provider": self.name(),
            "model": model,
            "content": "\n".join(content),
            "raw": response,
        }

    def tool_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model: str,
    ) -> dict[str, Any]:
        system_prompt, chat_messages = _anthropic_message_payload(messages)
        response = self.client.messages.create(
            model=model,
            messages=chat_messages,
            system=system_prompt,
            tools=tools,
        )
        content = []
        tool_calls: list[dict[str, Any]] = []
        for block in response.content:
            block_type = getattr(block, "type", "")
            if block_type == "text":
                text = getattr(block, "text", "")
                if text:
                    content.append(text)
            elif block_type == "tool_use":
                tool_calls.append(
                    {
                        "id": getattr(block, "id", ""),
                        "name": getattr(block, "name", ""),
                        "input": getattr(block, "input", {}),
                    }
                )
        return {
            "provider": self.name(),
            "model": model,
            "content": "\n".join(content),
            "tool_calls": tool_calls,
            "raw": response,
        }


def _anthropic_message_payload(
    messages: list[dict[str, Any]],
) -> tuple[str | None, list[dict[str, Any]]]:
    """Convert OpenAI-style system messages to Anthropic payload format."""
    system_parts: list[str] = []
    normalized: list[dict[str, Any]] = []

    for message in messages:
        role = str(message.get("role", "user")).strip().lower()
        content = str(message.get("content", ""))
        if role == "system":
            if content:
                system_parts.append(content)
            continue
        normalized.append({"role": role if role in {"user", "assistant"} else "user", "content": content})

    if not normalized:
        normalized = [{"role": "user", "content": "Use the provided context and answer the task."}]

    system_prompt = "\n\n".join(system_parts) if system_parts else None
    return system_prompt, normalized
