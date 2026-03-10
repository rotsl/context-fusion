# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for multi-objective latency-aware budget planner."""

from context_portfolio_optimizer.allocation.planner import BudgetPlanner, RepresentationCandidate


def test_planner_prefers_compact_variant_under_small_budget() -> None:
    planner = BudgetPlanner()
    candidates = [
        RepresentationCandidate(
            parent_block_id="b1",
            representation_type="full_text",
            text="x" * 1000,
            tokens=300,
            utility=0.9,
            risk=0.2,
            cacheable=False,
            diversity=0.4,
            generation_cost=0.0,
        ),
        RepresentationCandidate(
            parent_block_id="b1",
            representation_type="bullet_summary_3",
            text="short",
            tokens=40,
            utility=0.75,
            risk=0.1,
            cacheable=True,
            diversity=0.4,
            generation_cost=0.1,
        ),
    ]

    selection = planner.plan(candidates, budget=80)
    assert len(selection.selected) == 1
    assert selection.selected[0].representation_type == "bullet_summary_3"
