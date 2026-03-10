# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Ollama provider adapter."""

from __future__ import annotations

from typing import Any

import requests

from .base import BaseAdapter, ProviderCapabilities
from .tokenizers import estimate_provider_tokens


class OllamaProvider(BaseAdapter):
    """Ollama adapter using local HTTP API."""

    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url.rstrip("/")

    def name(self) -> str:
        return "ollama"

    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            supports_tools=True,
            supports_structured_output=False,
            supports_prompt_cache=False,
            supports_system_messages=True,
            local=True,
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
        request.setdefault("stream", False)
        request.update(kwargs)
        return request

    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "stream": False,
            **kwargs,
        }
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "provider": self.name(),
            "model": model,
            "content": data.get("message", {}).get("content", ""),
            "raw": data,
        }

    def tool_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model: str,
    ) -> dict[str, Any]:
        payload: dict[str, Any] = {
            "model": model,
            "messages": messages,
            "tools": tools,
            "stream": False,
        }
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        data = response.json()
        return {
            "provider": self.name(),
            "model": model,
            "content": data.get("message", {}).get("content", ""),
            "tool_calls": data.get("message", {}).get("tool_calls", []),
            "raw": data,
        }
