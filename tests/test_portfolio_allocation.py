# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Tests for portfolio allocation."""

import pytest

from context_portfolio_optimizer.allocation.budget import BudgetManager
from context_portfolio_optimizer.allocation.portfolio import PortfolioSelector
from context_portfolio_optimizer.types import BudgetAllocation, ContextBlock, SourceType


class TestBudgetManager:
    """Tests for BudgetManager."""

    def test_from_total(self):
        manager = BudgetManager.from_total(8000)

        assert manager.allocation.total == 8000
        assert manager.allocation.instructions > 0
        assert manager.allocation.retrieval > 0
        assert manager.allocation.output_reserve > 0

    def test_get_available_for_category(self):
        allocation = BudgetAllocation(
            instructions=1000,
            retrieval=3000,
            memory=2000,
            examples=1500,
            tool_trace=1000,
            output_reserve=1000,
        )
        manager = BudgetManager(allocation)

        assert manager.get_available_for_category("retrieval") == 3000
        assert manager.get_available_for_category("memory") == 2000

    def test_get_total_available(self):
        allocation = BudgetAllocation(
            instructions=1000,
            retrieval=3000,
            memory=2000,
            examples=1500,
            tool_trace=1000,
            output_reserve=1000,
        )
        manager = BudgetManager(allocation)

        # Total available excludes output_reserve
        assert manager.get_total_available() == 8500


class TestPortfolioSelector:
    """Tests for PortfolioSelector."""

    def test_select_empty_blocks(self):
        selector = PortfolioSelector()
        portfolio = selector.select([], budget=1000)

        assert len(portfolio.blocks) == 0
        assert portfolio.total_tokens == 0

    def test_select_single_block(self):
        selector = PortfolioSelector()

        blocks = [
            ContextBlock(
                id="test1",
                content="Test content",
                source_type=SourceType.TEXT,
                token_count=100,
            ),
        ]

        portfolio = selector.select(blocks, budget=1000)

        assert len(portfolio.blocks) == 1
        assert portfolio.blocks[0].id == "test1"

    def test_select_respects_budget(self):
        selector = PortfolioSelector()

        blocks = [
            ContextBlock(
                id=f"test{i}",
                content=f"Content {i}",
                source_type=SourceType.TEXT,
                token_count=500,
            )
            for i in range(5)
        ]

        portfolio = selector.select(blocks, budget=1000)

        # Should select at most 2 blocks (500 tokens each)
        assert portfolio.total_tokens <= 1000
        assert len(portfolio.blocks) <= 2

    def test_expected_utility_positive(self):
        selector = PortfolioSelector()

        blocks = [
            ContextBlock(
                id="test1",
                content="Test content with good metadata",
                source_type=SourceType.TEXT,
                token_count=100,
                trust_score=0.8,
                retrieval_score=0.9,
            ),
        ]

        portfolio = selector.select(blocks, budget=1000)

        assert portfolio.expected_utility > 0
