# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Leave-one-out ablation for ContextFusion."""

from ..types import AblationResult, ContextBlock
from .runner import AblationRunner


class LeaveOneOutAblation:
    """Convenience class for leave-one-out ablation."""

    def __init__(self, runner: AblationRunner | None = None):
        """Initialize ablation.

        Args:
            runner: Optional ablation runner
        """
        self.runner = runner or AblationRunner()

    def run(
        self,
        blocks: list[ContextBlock],
        budget: int,
    ) -> list[AblationResult]:
        """Run leave-one-out ablation.

        Args:
            blocks: Available blocks
            budget: Token budget

        Returns:
            Ablation results
        """
        return self.runner.run_leave_one_out(blocks, budget)

    def get_important_blocks(
        self,
        results: list[AblationResult],
        threshold: float | None = None,
    ) -> list[str]:
        """Get IDs of important blocks.

        Args:
            results: Ablation results
            threshold: Optional delta threshold

        Returns:
            List of block IDs
        """
        if threshold is None:
            # Use mean delta as threshold
            mean_delta = sum(r.delta for r in results) / len(results) if results else 0
            threshold = mean_delta

        return [r.block_id for r in results if r.delta >= threshold]

    def get_redundant_blocks(
        self,
        results: list[AblationResult],
        threshold: float = 0.01,
    ) -> list[str]:
        """Get IDs of redundant (low impact) blocks.

        Args:
            results: Ablation results
            threshold: Delta threshold for redundancy

        Returns:
            List of block IDs
        """
        return [r.block_id for r in results if r.delta < threshold]
