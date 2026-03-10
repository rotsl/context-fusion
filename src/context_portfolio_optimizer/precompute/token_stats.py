# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Token statistics helpers for precompute stage."""

from __future__ import annotations

from context_portfolio_optimizer.utils.tokenization import count_tokens


def token_features(text: str) -> dict[str, int]:
    """Compute deterministic token-level features."""
    tokens = count_tokens(text)
    chars = len(text)
    words = len([part for part in text.split() if part])
    return {
        "tokens": tokens,
        "chars": chars,
        "words": words,
    }
