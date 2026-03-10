# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Provider-aware token estimation helpers."""

from __future__ import annotations

from context_portfolio_optimizer.utils.tokenization import count_tokens

PROVIDER_TOKEN_MULTIPLIERS = {
    "openai": 1.0,
    "anthropic": 1.05,
    "ollama": 1.0,
    "openai_compatible": 1.0,
}


def estimate_provider_tokens(provider: str, text: str, model: str) -> int:
    """Estimate tokens with provider-level multiplier heuristics."""
    _ = model
    base = count_tokens(text)
    multiplier = PROVIDER_TOKEN_MULTIPLIERS.get(provider.lower(), 1.0)
    return int(base * multiplier)
