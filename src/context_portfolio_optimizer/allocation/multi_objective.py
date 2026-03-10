# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Multi-objective scoring for context allocation."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class PlannerWeights:
    """Weights for configurable multi-objective ranking."""

    utility: float = 1.0
    risk: float = 1.0
    token_cost: float = 0.3
    latency_cost: float = 0.25
    cacheability: float = 0.15
    diversity: float = 0.1


def score_multi_objective(
    *,
    utility: float,
    risk: float,
    token_cost: float,
    latency_cost: float,
    cacheability: float,
    diversity: float,
    weights: PlannerWeights,
) -> float:
    """Score candidate using the weighted objective expression."""
    return (
        (weights.utility * utility)
        - (weights.risk * risk)
        - (weights.token_cost * token_cost)
        - (weights.latency_cost * latency_cost)
        + (weights.cacheability * cacheability)
        + (weights.diversity * diversity)
    )
