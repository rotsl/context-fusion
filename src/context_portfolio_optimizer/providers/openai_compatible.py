# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""OpenAI-compatible provider adapter."""

from __future__ import annotations

from typing import Any

from .base import BaseAdapter, ProviderCapabilities
from .tokenizers import estimate_provider_tokens


class OpenAICompatibleProvider(BaseAdapter):
    """OpenAI-compatible adapter for Grok/Kimi/DeepSeek/Together/Groq-style APIs."""

    def __init__(self, base_url: str, api_key: str):
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError("openai package required for OpenAICompatibleProvider") from exc
        self.client = OpenAI(base_url=base_url, api_key=api_key)

    def name(self) -> str:
        return "openai_compatible"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_tools=True,
            supports_structured_output=True,
            supports_prompt_cache=False,
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
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            **kwargs,
        )
        message = response.choices[0].message
        return {
            "provider": self.name(),
            "model": model,
            "content": message.content or "",
            "raw": response,
        }

    def tool_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model: str,
    ) -> dict[str, Any]:
        response = self.client.chat.completions.create(
            model=model,
            messages=messages,
            tools=tools,
            tool_choice="auto",
        )
        message = response.choices[0].message
        return {
            "provider": self.name(),
            "model": model,
            "content": message.content or "",
            "tool_calls": [tc.model_dump() for tc in message.tool_calls or []],
            "raw": response,
        }
