# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Planner for ContextFusion."""

from typing import Any

from ..allocation.budget import BudgetManager
from ..logging_utils import get_logger
from ..types import BudgetAllocation

logger = get_logger("planner")


class Planner:
    """Plans context optimization execution."""

    def __init__(self, budget_manager: BudgetManager | None = None):
        """Initialize planner.

        Args:
            budget_manager: Budget manager
        """
        self.budget_manager = budget_manager or BudgetManager()

    def plan(
        self,
        task_description: str,
        available_sources: list[str] | None = None,
    ) -> dict[str, Any]:
        """Create execution plan.

        Args:
            task_description: Description of the task
            available_sources: Optional list of available source types

        Returns:
            Execution plan
        """
        allocation = self.budget_manager.allocation

        plan = {
            "task": task_description,
            "budget_allocation": {
                "instructions": allocation.instructions,
                "retrieval": allocation.retrieval,
                "memory": allocation.memory,
                "examples": allocation.examples,
                "tool_trace": allocation.tool_trace,
                "output_reserve": allocation.output_reserve,
            },
            "phases": [
                {
                    "name": "ingest",
                    "description": "Ingest data from sources",
                    "sources": available_sources or ["all"],
                },
                {
                    "name": "normalize",
                    "description": "Normalize to context blocks",
                },
                {
                    "name": "represent",
                    "description": "Generate alternative representations",
                },
                {
                    "name": "score",
                    "description": "Score utility and risk",
                },
                {
                    "name": "allocate",
                    "description": "Run knapsack optimization",
                },
                {
                    "name": "assemble",
                    "description": "Build final context",
                },
            ],
        }

        return plan

    def estimate_cost(self, plan: dict[str, Any]) -> dict[str, float]:
        """Estimate cost of execution plan.

        Args:
            plan: Execution plan

        Returns:
            Cost estimate
        """
        allocation = plan.get("budget_allocation", {})
        total_tokens = sum(allocation.values())

        # Rough cost estimate (GPT-3.5-turbo pricing)
        cost_per_1k = 0.0015
        estimated_cost = (total_tokens / 1000) * cost_per_1k

        return {
            "estimated_tokens": total_tokens,
            "estimated_cost_usd": estimated_cost,
        }
