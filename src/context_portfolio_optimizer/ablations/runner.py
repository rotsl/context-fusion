# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Ablation runner for ContextFusion."""

from typing import Any

from ..allocation.portfolio import PortfolioSelector
from ..evaluators.reward import RewardCalculator
from ..logging_utils import get_logger
from ..types import AblationResult, ContextBlock, PortfolioSelection

logger = get_logger("ablation")


class AblationRunner:
    """Runs ablation studies on context selection."""

    def __init__(
        self,
        portfolio_selector: PortfolioSelector | None = None,
        reward_calculator: RewardCalculator | None = None,
    ):
        """Initialize ablation runner.

        Args:
            portfolio_selector: Portfolio selector
            reward_calculator: Reward calculator
        """
        self.selector = portfolio_selector or PortfolioSelector()
        self.reward_calc = reward_calculator or RewardCalculator()

    def run_leave_one_out(
        self,
        blocks: list[ContextBlock],
        budget: int,
    ) -> list[AblationResult]:
        """Run leave-one-out ablation.

        Removes each block and measures impact on reward.

        Args:
            blocks: All available blocks
            budget: Token budget

        Returns:
            List of ablation results
        """
        # Get baseline
        baseline = self.selector.select(blocks, budget)
        baseline_reward = self.reward_calc.calculate(baseline)

        results = []

        for block in blocks:
            # Remove this block
            reduced_blocks = [b for b in blocks if b.id != block.id]

            # Re-select
            reduced_portfolio = self.selector.select(reduced_blocks, budget)
            reduced_reward = self.reward_calc.calculate(reduced_portfolio)

            # Calculate delta
            delta = baseline_reward - reduced_reward

            result = AblationResult(
                block_id=block.id,
                baseline_reward=baseline_reward,
                removed_reward=reduced_reward,
                delta=delta,
                representation_savings={},
            )
            results.append(result)

        # Sort by delta (most important first)
        results.sort(key=lambda r: r.delta, reverse=True)

        return results

    def run_representation_swap(
        self,
        portfolio: PortfolioSelection,
    ) -> dict[str, Any]:
        """Run representation swap ablation.

        Tests impact of using different representations.

        Args:
            portfolio: Selected portfolio

        Returns:
            Results dictionary
        """
        from ..types import RepresentationType

        results = {}

        for rep_type in RepresentationType:
            # Re-select with this representation
            new_portfolio = self.selector.select_with_representation(
                portfolio.blocks, rep_type
            )

            reward = self.reward_calc.calculate(new_portfolio)
            tokens = new_portfolio.total_tokens

            results[rep_type.value] = {
                "reward": reward,
                "tokens": tokens,
                "blocks": len(new_portfolio.blocks),
            }

        return results

    def analyze_importance(
        self,
        ablation_results: list[AblationResult],
    ) -> dict[str, Any]:
        """Analyze block importance from ablation results.

        Args:
            ablation_results: Ablation results

        Returns:
            Analysis dictionary
        """
        if not ablation_results:
            return {"error": "No ablation results"}

        deltas = [r.delta for r in ablation_results]

        return {
            "most_important": ablation_results[0].block_id if ablation_results else None,
            "least_important": ablation_results[-1].block_id if ablation_results else None,
            "mean_delta": sum(deltas) / len(deltas),
            "max_delta": max(deltas),
            "min_delta": min(deltas),
            "total_blocks": len(ablation_results),
        }
