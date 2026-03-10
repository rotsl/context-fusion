# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Provider protocol and shared provider helpers."""

from __future__ import annotations

from typing import Any, Protocol

from context_portfolio_optimizer.utils.tokenization import count_tokens


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


class BaseAdapter:
    """Shared implementation pieces for provider adapters."""

    def estimate_tokens(self, text: str, model: str) -> int:
        """Estimate token count using project tokenizer."""
        _ = model
        return count_tokens(text)
