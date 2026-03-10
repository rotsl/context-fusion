# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Tests for knapsack optimizer."""

import pytest

from context_portfolio_optimizer.allocation.knapsack import KnapsackItem, KnapsackOptimizer
from context_portfolio_optimizer.types import RepresentationType


class TestKnapsackOptimizer:
    """Tests for KnapsackOptimizer."""

    def test_optimize_simple(self):
        optimizer = KnapsackOptimizer()

        items = [
            KnapsackItem("1", RepresentationType.FULL_TEXT, "content1", 100, 10.0, 0.1),
            KnapsackItem("2", RepresentationType.FULL_TEXT, "content2", 200, 15.0, 0.1),
            KnapsackItem("3", RepresentationType.FULL_TEXT, "content3", 150, 12.0, 0.1),
        ]

        selected = optimizer.optimize(items, budget=300)

        assert len(selected) > 0
        total_tokens = sum(item.tokens for item in selected)
        assert total_tokens <= 300

    def test_optimize_empty(self):
        optimizer = KnapsackOptimizer()
        selected = optimizer.optimize([], budget=100)
        assert len(selected) == 0

    def test_optimize_zero_budget(self):
        optimizer = KnapsackOptimizer()
        items = [
            KnapsackItem("1", RepresentationType.FULL_TEXT, "content", 100, 10.0, 0.1),
        ]
        selected = optimizer.optimize(items, budget=0)
        assert len(selected) == 0

    def test_optimize_respects_budget(self):
        optimizer = KnapsackOptimizer()

        items = [
            KnapsackItem("1", RepresentationType.FULL_TEXT, "c1", 500, 50.0, 0.1),
            KnapsackItem("2", RepresentationType.FULL_TEXT, "c2", 600, 60.0, 0.1),
        ]

        selected = optimizer.optimize(items, budget=400)

        # Should not select any item as both exceed budget
        assert len(selected) == 0

    def test_value_density_selection(self):
        optimizer = KnapsackOptimizer()

        # Item 1: high value density (0.2 value/token)
        # Item 2: low value density (0.05 value/token)
        items = [
            KnapsackItem("1", RepresentationType.FULL_TEXT, "c1", 100, 20.0, 0.1),
            KnapsackItem("2", RepresentationType.FULL_TEXT, "c2", 100, 5.0, 0.1),
        ]

        selected = optimizer.optimize(items, budget=100)

        # Should prefer high value density item
        assert len(selected) == 1
        assert selected[0].block_id == "1"
