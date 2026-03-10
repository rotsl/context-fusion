# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Budget management for ContextFusion."""

from ..constants import (
    DEFAULT_EXAMPLES_BUDGET,
    DEFAULT_INSTRUCTIONS_BUDGET,
    DEFAULT_MEMORY_BUDGET,
    DEFAULT_OUTPUT_RESERVE,
    DEFAULT_RETRIEVAL_BUDGET,
    DEFAULT_TOOL_TRACE_BUDGET,
)
from ..settings import get_settings
from ..types import BudgetAllocation


class BudgetManager:
    """Manages token budget allocation."""

    def __init__(self, allocation: BudgetAllocation | None = None):
        """Initialize budget manager.

        Args:
            allocation: Optional budget allocation
        """
        if allocation is None:
            # Load from settings
            settings = get_settings()
            allocation = BudgetAllocation(
                instructions=settings.budget.instructions,
                retrieval=settings.budget.retrieval,
                memory=settings.budget.memory,
                examples=settings.budget.examples,
                tool_trace=settings.budget.tool_trace,
                output_reserve=settings.budget.output_reserve,
            )

        self.allocation = allocation

    @classmethod
    def from_total(cls, total_tokens: int) -> "BudgetManager":
        """Create budget manager from total token budget.

        Args:
            total_tokens: Total token budget

        Returns:
            BudgetManager instance
        """
        # Proportional allocation
        default_total = (
            DEFAULT_INSTRUCTIONS_BUDGET
            + DEFAULT_RETRIEVAL_BUDGET
            + DEFAULT_MEMORY_BUDGET
            + DEFAULT_EXAMPLES_BUDGET
            + DEFAULT_TOOL_TRACE_BUDGET
            + DEFAULT_OUTPUT_RESERVE
        )

        ratio = total_tokens / default_total

        allocation = BudgetAllocation(
            instructions=int(DEFAULT_INSTRUCTIONS_BUDGET * ratio),
            retrieval=int(DEFAULT_RETRIEVAL_BUDGET * ratio),
            memory=int(DEFAULT_MEMORY_BUDGET * ratio),
            examples=int(DEFAULT_EXAMPLES_BUDGET * ratio),
            tool_trace=int(DEFAULT_TOOL_TRACE_BUDGET * ratio),
            output_reserve=int(DEFAULT_OUTPUT_RESERVE * ratio),
        )

        return cls(allocation)

    def get_available_for_category(self, category: str) -> int:
        """Get available tokens for a category.

        Args:
            category: Category name (retrieval, memory, etc.)

        Returns:
            Available tokens
        """
        return getattr(self.allocation, category, 0)

    def get_total_available(self) -> int:
        """Get total available tokens (excluding output reserve).

        Returns:
            Total available tokens
        """
        return (
            self.allocation.instructions
            + self.allocation.retrieval
            + self.allocation.memory
            + self.allocation.examples
            + self.allocation.tool_trace
        )

    def get_total_budget(self) -> int:
        """Get total budget including output reserve.

        Returns:
            Total budget
        """
        return self.allocation.total

    def allocate(self, category: str, tokens: int) -> bool:
        """Allocate tokens to a category.

        Args:
            category: Category name
            tokens: Tokens to allocate

        Returns:
            True if allocation succeeded
        """
        current = getattr(self.allocation, category, 0)
        if current >= tokens:
            setattr(self.allocation, category, current - tokens)
            return True
        return False

    def reserve_output(self, tokens: int) -> bool:
        """Reserve tokens for output generation.

        Args:
            tokens: Tokens to reserve

        Returns:
            True if reservation succeeded
        """
        if self.allocation.output_reserve >= tokens:
            self.allocation.output_reserve -= tokens
            return True
        return False

    def reset(self) -> None:
        """Reset budget to initial allocation."""
        settings = get_settings()
        self.allocation = BudgetAllocation(
            instructions=settings.budget.instructions,
            retrieval=settings.budget.retrieval,
            memory=settings.budget.memory,
            examples=settings.budget.examples,
            tool_trace=settings.budget.tool_trace,
            output_reserve=settings.budget.output_reserve,
        )

    def __repr__(self) -> str:
        return (
            f"BudgetManager("
            f"instructions={self.allocation.instructions}, "
            f"retrieval={self.allocation.retrieval}, "
            f"memory={self.allocation.memory}, "
            f"examples={self.allocation.examples}, "
            f"tool_trace={self.allocation.tool_trace}, "
            f"output_reserve={self.allocation.output_reserve}"
            f")"
        )
