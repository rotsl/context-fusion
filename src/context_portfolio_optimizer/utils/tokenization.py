# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Tokenization utilities for ContextFusion."""

from functools import lru_cache

from ..constants import DEFAULT_ENCODING, TOKENS_PER_CHARACTER


def estimate_tokens(text: str) -> int:
    """Estimate token count using character-based heuristic.

    This is a fast approximation that doesn't require tiktoken.

    Args:
        text: Input text

    Returns:
        Estimated token count
    """
    if not text:
        return 0
    return max(1, int(len(text) * TOKENS_PER_CHARACTER))


@lru_cache(maxsize=1)
def _get_tiktoken_encoder():
    """Get cached tiktoken encoder.

    Returns:
        Tiktoken encoder or None if not available
    """
    try:
        import tiktoken

        return tiktoken.get_encoding(DEFAULT_ENCODING)
    except Exception:
        # Fall back to heuristic estimation when tiktoken cannot load
        # (for example in offline CI environments).
        return None


def count_tokens(text: str, encoding: str | None = None) -> int:
    """Count tokens in text.

    Uses tiktoken if available, falls back to estimation.

    Args:
        text: Input text
        encoding: Optional encoding name

    Returns:
        Token count
    """
    if not text:
        return 0

    encoder = _get_tiktoken_encoder()
    if encoder is not None:
        try:
            return len(encoder.encode(text))
        except Exception:
            pass

    return estimate_tokens(text)


def truncate_to_tokens(text: str, max_tokens: int, encoding: str | None = None) -> str:
    """Truncate text to fit within token budget.

    Args:
        text: Input text
        max_tokens: Maximum tokens allowed
        encoding: Optional encoding name

    Returns:
        Truncated text
    """
    if not text:
        return text

    encoder = _get_tiktoken_encoder()
    if encoder is not None:
        try:
            tokens = encoder.encode(text)
            if len(tokens) <= max_tokens:
                return text
            return encoder.decode(tokens[:max_tokens])
        except Exception:
            pass

    # Fallback to character-based truncation
    char_limit = int(max_tokens / TOKENS_PER_CHARACTER)
    return text[:char_limit]


def get_token_stats(texts: list[str]) -> dict:
    """Get token statistics for a list of texts.

    Args:
        texts: List of texts

    Returns:
        Dictionary with statistics
    """
    if not texts:
        return {
            "total": 0,
            "mean": 0,
            "min": 0,
            "max": 0,
            "count": 0,
        }

    token_counts = [count_tokens(t) for t in texts]

    return {
        "total": sum(token_counts),
        "mean": sum(token_counts) / len(token_counts),
        "min": min(token_counts),
        "max": max(token_counts),
        "count": len(token_counts),
    }
