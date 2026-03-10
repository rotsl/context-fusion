# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Deterministic pseudo-embedding functions for precompute."""

from __future__ import annotations

from context_portfolio_optimizer.utils.hashing import compute_hash


def pseudo_embedding(text: str, dims: int = 16) -> list[float]:
    """Generate deterministic pseudo-embedding from text hash."""
    digest = compute_hash(text)
    values: list[float] = []
    for idx in range(dims):
        start = (idx * 2) % len(digest)
        chunk = digest[start : start + 2]
        values.append(int(chunk, 16) / 255.0)
    return values
