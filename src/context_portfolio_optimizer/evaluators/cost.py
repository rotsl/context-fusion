# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Cost evaluation for ContextFusion."""

from ..types import PortfolioSelection


class CostEvaluator:
    """Evaluates cost of context selection."""

    # Approximate cost per 1K tokens (in USD)
    COST_PER_1K_TOKENS = {
        "gpt-4": 0.03,
        "gpt-4-turbo": 0.01,
        "gpt-3.5-turbo": 0.0015,
    }

    def evaluate(
        self,
        portfolio: PortfolioSelection,
        model: str = "gpt-3.5-turbo",
    ) -> dict[str, float]:
        """Evaluate portfolio cost.

        Args:
            portfolio: Selected portfolio
            model: Model name for pricing

        Returns:
            Cost metrics
        """
        tokens = portfolio.total_tokens
        cost_per_1k = self.COST_PER_1K_TOKENS.get(model, 0.0015)

        return {
            "input_tokens": tokens,
            "estimated_cost_usd": (tokens / 1000) * cost_per_1k,
            "cost_per_1k_tokens": cost_per_1k,
        }

    def compare_costs(
        self,
        portfolios: dict[str, PortfolioSelection],
        model: str = "gpt-3.5-turbo",
    ) -> dict[str, dict[str, float]]:
        """Compare costs of multiple portfolios.

        Args:
            portfolios: Dictionary of portfolio name to portfolio
            model: Model name

        Returns:
            Cost comparison
        """
        results = {}
        for name, portfolio in portfolios.items():
            results[name] = self.evaluate(portfolio, model)
        return results
