# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Reward calculation for ContextFusion."""

from ..constants import DEFAULT_REWARD_WEIGHTS
from ..settings import get_settings
from ..types import PortfolioSelection
from .cost import CostEvaluator
from .quality import QualityEvaluator


class RewardCalculator:
    """Calculates reward for context selection."""

    def __init__(self, weights: dict[str, float] | None = None):
        """Initialize reward calculator.

        Args:
            weights: Optional reward weights
        """
        if weights is None:
            settings = get_settings()
            weights = settings.scoring.reward_weights

        self.weights = {**DEFAULT_REWARD_WEIGHTS, **weights}
        self.quality_evaluator = QualityEvaluator()
        self.cost_evaluator = CostEvaluator()

    def calculate(
        self,
        portfolio: PortfolioSelection,
        latency_ms: float = 0.0,
    ) -> float:
        """Calculate reward for a portfolio.

        reward = alpha * quality - beta * cost - gamma * latency - delta * risk

        Args:
            portfolio: Selected portfolio
            latency_ms: Latency in milliseconds

        Returns:
            Reward value
        """
        # Quality component
        quality_metrics = self.quality_evaluator.evaluate(portfolio)
        quality = quality_metrics["overall"]

        # Cost component (normalize to 0-1 range, assume max 10k tokens)
        cost_metrics = self.cost_evaluator.evaluate(portfolio)
        cost = cost_metrics["input_tokens"] / 10000

        # Risk component
        risk = portfolio.total_risk

        # Calculate reward
        reward = (
            self.weights["alpha"] * quality
            - self.weights["beta"] * cost
            - self.weights["gamma"] * (latency_ms / 1000)
            - self.weights["delta"] * risk
        )

        return reward

    def calculate_with_metrics(
        self,
        portfolio: PortfolioSelection,
        latency_ms: float = 0.0,
    ) -> dict[str, float]:
        """Calculate reward with detailed metrics.

        Args:
            portfolio: Selected portfolio
            latency_ms: Latency in milliseconds

        Returns:
            Dictionary with reward and components
        """
        quality_metrics = self.quality_evaluator.evaluate(portfolio)
        quality = quality_metrics["overall"]

        cost_metrics = self.cost_evaluator.evaluate(portfolio)
        cost = cost_metrics["input_tokens"] / 10000

        risk = portfolio.total_risk

        reward = (
            self.weights["alpha"] * quality
            - self.weights["beta"] * cost
            - self.weights["gamma"] * (latency_ms / 1000)
            - self.weights["delta"] * risk
        )

        return {
            "reward": reward,
            "quality": quality,
            "cost": cost,
            "latency": latency_ms / 1000,
            "risk": risk,
            "quality_breakdown": quality_metrics,
            "cost_breakdown": cost_metrics,
        }
