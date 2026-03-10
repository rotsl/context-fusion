# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Quality evaluation for ContextFusion."""

from typing import Any

from ..types import ContextBlock, PortfolioSelection


class QualityEvaluator:
    """Evaluates quality of context selection."""

    def evaluate(
        self,
        portfolio: PortfolioSelection,
        reference_blocks: list[ContextBlock] | None = None,
    ) -> dict[str, float]:
        """Evaluate portfolio quality.

        Args:
            portfolio: Selected portfolio
            reference_blocks: Optional reference blocks for comparison

        Returns:
            Quality metrics
        """
        metrics = {
            "coverage": self._coverage_score(portfolio),
            "diversity": self._diversity_score(portfolio),
            "relevance": self._relevance_score(portfolio),
            "completeness": self._completeness_score(portfolio, reference_blocks),
        }

        # Overall quality score
        metrics["overall"] = sum(metrics.values()) / len(metrics)

        return metrics

    def _coverage_score(self, portfolio: PortfolioSelection) -> float:
        """Score based on token budget utilization."""
        # Ideal utilization is around 90%
        # Too low = wasted budget, too high = risk of truncation
        utilization = portfolio.total_tokens / max(1, 8000)  # Assume 8k budget
        if utilization < 0.5:
            return utilization * 2  # Penalize under-utilization
        elif utilization > 0.95:
            return max(0, 1 - (utilization - 0.95) * 20)  # Penalize over-utilization
        else:
            return 1.0

    def _diversity_score(self, portfolio: PortfolioSelection) -> float:
        """Score based on source diversity."""
        if not portfolio.blocks:
            return 0.0

        source_types = set(b.source_type for b in portfolio.blocks)
        return min(1.0, len(source_types) / 3)  # Ideal: 3+ source types

    def _relevance_score(self, portfolio: PortfolioSelection) -> float:
        """Score based on average retrieval score."""
        if not portfolio.blocks:
            return 0.0

        avg_retrieval = sum(b.retrieval_score for b in portfolio.blocks) / len(portfolio.blocks)
        return avg_retrieval

    def _completeness_score(
        self,
        portfolio: PortfolioSelection,
        reference_blocks: list[ContextBlock] | None,
    ) -> float:
        """Score based on coverage of reference blocks."""
        if not reference_blocks:
            return 1.0  # No reference, assume complete

        selected_ids = {b.id for b in portfolio.blocks}
        reference_ids = {b.id for b in reference_blocks}

        if not reference_ids:
            return 1.0

        overlap = len(selected_ids & reference_ids)
        return overlap / len(reference_ids)
