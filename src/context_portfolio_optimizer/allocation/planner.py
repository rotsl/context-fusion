# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Latency-aware multi-objective budget planner."""

from __future__ import annotations

from dataclasses import dataclass

from context_portfolio_optimizer.allocation.latency_cost import estimate_latency_cost
from context_portfolio_optimizer.allocation.multi_objective import (
    PlannerWeights,
    score_multi_objective,
)
from context_portfolio_optimizer.allocation.value_density import compute_value_density


@dataclass
class RepresentationCandidate:
    """A representation candidate for a parent block."""

    parent_block_id: str
    representation_type: str
    text: str
    tokens: int
    utility: float
    risk: float
    cacheable: bool
    diversity: float
    generation_cost: float
    fingerprint: str | None = None


@dataclass
class PlannerSelection:
    """Planner output for selected representations."""

    selected: list[RepresentationCandidate]
    total_tokens: int
    objective_score: float


class BudgetPlanner:
    """Select compact representations under budget with latency-aware objective."""

    def __init__(self, weights: PlannerWeights | None = None):
        self.weights = weights or PlannerWeights()

    def plan(self, candidates: list[RepresentationCandidate], budget: int) -> PlannerSelection:
        """Plan a token-constrained representation set with one variant per block."""
        if budget <= 0 or not candidates:
            return PlannerSelection(selected=[], total_tokens=0, objective_score=0.0)

        ranked = sorted(candidates, key=self._rank_key, reverse=True)

        selected: list[RepresentationCandidate] = []
        used_parent_ids: set[str] = set()
        used_fingerprints: set[str] = set()
        total_tokens = 0
        total_score = 0.0

        for candidate in ranked:
            if candidate.parent_block_id in used_parent_ids:
                continue
            if candidate.fingerprint and candidate.fingerprint in used_fingerprints:
                continue
            if total_tokens + candidate.tokens > budget:
                continue

            selected.append(candidate)
            used_parent_ids.add(candidate.parent_block_id)
            if candidate.fingerprint:
                used_fingerprints.add(candidate.fingerprint)

            total_tokens += candidate.tokens
            total_score += self._objective(candidate)

        return PlannerSelection(
            selected=selected,
            total_tokens=total_tokens,
            objective_score=total_score,
        )

    def _objective(self, candidate: RepresentationCandidate) -> float:
        token_cost = candidate.tokens / 1000.0
        latency_cost = estimate_latency_cost(
            token_count=candidate.tokens,
            generation_cost=candidate.generation_cost,
            cacheable=candidate.cacheable,
        )
        cacheability = 1.0 if candidate.cacheable else 0.0
        return score_multi_objective(
            utility=candidate.utility,
            risk=candidate.risk,
            token_cost=token_cost,
            latency_cost=latency_cost,
            cacheability=cacheability,
            diversity=candidate.diversity,
            weights=self.weights,
        )

    def _rank_key(self, candidate: RepresentationCandidate) -> tuple[float, float, int]:
        objective = self._objective(candidate)
        density = compute_value_density(candidate.utility, candidate.risk, candidate.tokens)
        return (objective, density, -candidate.tokens)
