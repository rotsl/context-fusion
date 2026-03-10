# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Provider protocol and shared provider helpers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from context_portfolio_optimizer.utils.tokenization import count_tokens


@dataclass(frozen=True)
class ProviderCapabilities:
    """Capability flags for provider adapters."""

    supports_tools: bool
    supports_structured_output: bool
    supports_prompt_cache: bool
    supports_system_messages: bool
    local: bool


class LLMProvider(Protocol):
    """Provider interface for chat and tool-calling APIs."""

    def name(self) -> str:
        """Return provider name."""

    def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count for text and model."""

    def chat(
        self,
        messages: list[dict[str, Any]],
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Perform a chat completion request."""

    def tool_call(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
        model: str,
    ) -> dict[str, Any]:
        """Perform a tool-call capable request."""

    def capabilities(self) -> ProviderCapabilities:
        """Return provider capability flags."""

    def build_request(
        self,
        compiled_packet: dict[str, Any],
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build provider-native request from compiled packet."""


class BaseAdapter:
    """Shared implementation pieces for provider adapters."""

    def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count using project tokenizer."""
        _ = model
        return count_tokens(text)

    def build_request(
        self,
        compiled_packet: dict[str, Any],
        model: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Build request payload for provider APIs."""
        messages = compiled_packet.get("messages", [])
        payload: dict[str, Any] = {"model": model, "messages": messages}
        payload.update(kwargs)
        return payload
