# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""OpenAI provider adapter."""

from __future__ import annotations

import os
from typing import Any

from .base import BaseAdapter


class OpenAIProvider(BaseAdapter):
    """OpenAI provider adapter using the official SDK."""

    def __init__(self, api_key: str | None = None):
        try:
            from openai import OpenAI
        except ImportError as exc:  # pragma: no cover - optional dependency
            raise ImportError("openai package required for OpenAIProvider") from exc
        self.client = OpenAI(api_key=api_key or os.getenv("OPENAI_API_KEY"))

    def name(self) -> str:
        return "openai"

    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        response = self.client.responses.create(
            model=model,
            input=messages,
            **kwargs,
        )
        output_text = getattr(response, "output_text", "")
        return {
            "provider": self.name(),
            "model": model,
            "content": output_text or "",
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
