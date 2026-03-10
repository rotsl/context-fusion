# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Portfolio selection for context optimization."""

from ..logging_utils import get_logger
from ..scoring.features import FeatureExtractor
from ..scoring.risk_model import RiskModel
from ..scoring.utility_model import UtilityModel
from ..types import ContextBlock, PortfolioSelection, RepresentationType
from .budget import BudgetManager
from .knapsack import KnapsackOptimizer

logger = get_logger("portfolio")


class PortfolioSelector:
    """Selects optimal context portfolio."""

    def __init__(
        self,
        budget_manager: BudgetManager | None = None,
        utility_model: UtilityModel | None = None,
        risk_model: RiskModel | None = None,
    ):
        """Initialize portfolio selector.

        Args:
            budget_manager: Optional budget manager
            utility_model: Optional utility model
            risk_model: Optional risk model
        """
        self.budget_manager = budget_manager or BudgetManager()
        self.utility_model = utility_model or UtilityModel()
        self.risk_model = risk_model or RiskModel()
        self.feature_extractor = FeatureExtractor()
        self.knapsack = KnapsackOptimizer()

    def select(
        self,
        blocks: list[ContextBlock],
        budget: int | None = None,
        risk_tolerance: float = 1.0,
    ) -> PortfolioSelection:
        """Select optimal context portfolio.

        Args:
            blocks: Available context blocks
            budget: Optional token budget override
            risk_tolerance: Risk tolerance (0-1)

        Returns:
            Selected portfolio
        """
        if budget is None:
            budget = self.budget_manager.get_available_for_category("retrieval")

        if not blocks:
            return PortfolioSelection(
                blocks=[],
                representations_used={},
                total_tokens=0,
                expected_utility=0.0,
                total_risk=0.0,
            )

        logger.debug(f"Selecting portfolio from {len(blocks)} blocks with budget {budget}")

        # Score all blocks
        utility_scores = self.utility_model.score_blocks(blocks, self.feature_extractor)
        risk_scores = self.risk_model.score_blocks(blocks, self.feature_extractor)

        # Create knapsack items
        items = self.knapsack.create_items_from_blocks(
            blocks, utility_scores, risk_scores
        )

        # Optimize
        selected_items = self.knapsack.optimize(items, budget, risk_tolerance)

        # Build result
        selected_blocks = []
        representations_used: dict[str, RepresentationType] = {}
        total_tokens = 0
        expected_utility = 0.0
        total_risk = 0.0

        # Track which blocks we've added
        added_block_ids: set[str] = set()

        for item in selected_items:
            # Find the block
            block = next((b for b in blocks if b.id == item.block_id), None)
            if block and block.id not in added_block_ids:
                selected_blocks.append(block)
                added_block_ids.add(block.id)
                representations_used[block.id] = item.representation
                total_tokens += item.tokens
                expected_utility += item.value
                total_risk += item.risk

        logger.debug(
            f"Selected {len(selected_blocks)} blocks, "
            f"{total_tokens} tokens, utility={expected_utility:.2f}"
        )

        return PortfolioSelection(
            blocks=selected_blocks,
            representations_used=representations_used,
            total_tokens=total_tokens,
            expected_utility=expected_utility,
            total_risk=total_risk,
        )

    def select_with_representation(
        self,
        blocks: list[ContextBlock],
        representation: RepresentationType,
        budget: int | None = None,
    ) -> PortfolioSelection:
        """Select portfolio using a specific representation.

        Args:
            blocks: Available context blocks
            representation: Representation type to use
            budget: Optional token budget override

        Returns:
            Selected portfolio
        """
        if budget is None:
            budget = self.budget_manager.get_available_for_category("retrieval")

        # Score blocks
        utility_scores = self.utility_model.score_blocks(blocks, self.feature_extractor)
        risk_scores = self.risk_model.score_blocks(blocks, self.feature_extractor)

        # Create items with only the specified representation
        items = []
        for block in blocks:
            utility = utility_scores.get(block.id, 0.0)
            risk = risk_scores.get(block.id, 0.0)

            # Get content for this representation
            if representation in block.representations:
                content = block.representations[representation]
                tokens = block.representation_tokens.get(representation, block.token_count)
            else:
                content = block.content
                tokens = block.token_count

            item = self.knapsack.create_items_from_blocks(
                [block], {block.id: utility}, {block.id: risk}
            )[0]
            items.append(item)

        # Optimize
        selected_items = self.knapsack.optimize(items, budget)

        # Build result
        selected_blocks = []
        representations_used: dict[str, RepresentationType] = {}
        total_tokens = 0
        expected_utility = 0.0
        total_risk = 0.0

        for item in selected_items:
            block = next((b for b in blocks if b.id == item.block_id), None)
            if block:
                selected_blocks.append(block)
                representations_used[block.id] = representation
                total_tokens += item.tokens
                expected_utility += item.value
                total_risk += item.risk

        return PortfolioSelection(
            blocks=selected_blocks,
            representations_used=representations_used,
            total_tokens=total_tokens,
            expected_utility=expected_utility,
            total_risk=total_risk,
        )
