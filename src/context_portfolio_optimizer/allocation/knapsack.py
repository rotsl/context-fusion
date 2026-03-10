# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Knapsack optimizer for context block selection."""

from dataclasses import dataclass

import numpy as np

from ..logging_utils import get_logger
from ..types import ContextBlock, RepresentationType

logger = get_logger("knapsack")


@dataclass
class KnapsackItem:
    """Item for knapsack optimization."""

    block_id: str
    representation: RepresentationType
    content: str
    tokens: int
    value: float
    risk: float


class KnapsackOptimizer:
    """0/1 Knapsack optimizer for context selection."""

    def __init__(self):
        pass

    def optimize(
        self,
        items: list[KnapsackItem],
        budget: int,
        risk_tolerance: float = 1.0,
    ) -> list[KnapsackItem]:
        """Solve 0/1 knapsack problem for context selection.

        Maximizes total value subject to token budget and risk constraints.

        Args:
            items: List of candidate items
            budget: Token budget
            risk_tolerance: Maximum acceptable total risk (0-1)

        Returns:
            List of selected items
        """
        if not items or budget <= 0:
            return []

        # Filter items that fit in budget
        feasible_items = [item for item in items if item.tokens <= budget]

        if not feasible_items:
            logger.warning("No feasible items fit in budget")
            return []

        # Sort by value density (value per token) for greedy fallback
        sorted_items = sorted(
            feasible_items,
            key=lambda x: x.value / max(1, x.tokens),
            reverse=True,
        )

        # Try greedy first (fast)
        greedy_selection = self._greedy_select(sorted_items, budget, risk_tolerance)
        greedy_value = sum(item.value for item in greedy_selection)

        # Try dynamic programming for optimal solution (if not too large)
        if len(feasible_items) <= 100 and budget <= 10000:
            dp_selection = self._dp_solve(feasible_items, budget, risk_tolerance)
            dp_value = sum(item.value for item in dp_selection)

            if dp_value > greedy_value:
                return dp_selection

        return greedy_selection

    def _greedy_select(
        self,
        items: list[KnapsackItem],
        budget: int,
        risk_tolerance: float,
    ) -> list[KnapsackItem]:
        """Greedy selection by value density.

        Args:
            items: Sorted list of items
            budget: Token budget
            risk_tolerance: Risk tolerance

        Returns:
            Selected items
        """
        selected = []
        remaining_budget = budget
        total_risk = 0.0

        for item in items:
            if item.tokens <= remaining_budget:
                new_risk = total_risk + item.risk
                if new_risk <= risk_tolerance * (len(selected) + 1):
                    selected.append(item)
                    remaining_budget -= item.tokens
                    total_risk = new_risk

        return selected

    def _dp_solve(
        self,
        items: list[KnapsackItem],
        budget: int,
        risk_tolerance: float,
    ) -> list[KnapsackItem]:
        """Dynamic programming solution.

        Args:
            items: List of items
            budget: Token budget
            risk_tolerance: Risk tolerance

        Returns:
            Selected items
        """
        n = len(items)

        # DP table: dp[i][w] = max value using first i items with weight w
        dp = np.zeros((n + 1, budget + 1))

        for i in range(1, n + 1):
            item = items[i - 1]
            for w in range(budget + 1):
                # Don't take item i
                dp[i][w] = dp[i - 1][w]

                # Take item i if it fits
                if item.tokens <= w:
                    new_value = dp[i - 1][w - item.tokens] + item.value
                    if new_value > dp[i][w]:
                        dp[i][w] = new_value

        # Backtrack to find selected items
        selected = []
        w = budget
        for i in range(n, 0, -1):
            if dp[i][w] != dp[i - 1][w]:
                item = items[i - 1]
                selected.append(item)
                w -= item.tokens

        return list(reversed(selected))

    def create_items_from_blocks(
        self,
        blocks: list[ContextBlock],
        utility_scores: dict[str, float],
        risk_scores: dict[str, float],
    ) -> list[KnapsackItem]:
        """Create knapsack items from context blocks.

        Args:
            blocks: List of context blocks
            utility_scores: Dictionary mapping block IDs to utility scores
            risk_scores: Dictionary mapping block IDs to risk scores

        Returns:
            List of knapsack items
        """
        items = []

        for block in blocks:
            utility = utility_scores.get(block.id, 0.0)
            risk = risk_scores.get(block.id, 0.0)

            # Create item for each representation
            for rep_type in block.representations:
                content = block.representations[rep_type]
                tokens = block.representation_tokens.get(rep_type, block.token_count)

                # Adjust utility for compact representations
                rep_utility = utility * (block.token_count / max(1, tokens))

                item = KnapsackItem(
                    block_id=block.id,
                    representation=rep_type,
                    content=content,
                    tokens=tokens,
                    value=rep_utility,
                    risk=risk,
                )
                items.append(item)

            # Also add full text as option
            item = KnapsackItem(
                block_id=block.id,
                representation=RepresentationType.FULL_TEXT,
                content=block.content,
                tokens=block.token_count,
                value=utility,
                risk=risk,
            )
            items.append(item)

        return items
