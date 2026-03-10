# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Lightweight deterministic latency cost estimation."""


def estimate_latency_cost(
    token_count: int,
    generation_cost: float,
    cacheable: bool,
) -> float:
    """Estimate normalized latency cost for ranking decisions."""
    base = token_count / 1000.0
    overhead = max(0.0, generation_cost)
    cache_discount = 0.2 if cacheable else 0.0
    return max(0.0, base + overhead - cache_discount)
