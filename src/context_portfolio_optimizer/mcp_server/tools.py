# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""MCP-like tool handlers for ContextFusion."""

from __future__ import annotations

from typing import Any

from context_portfolio_optimizer.ablations.runner import AblationRunner
from context_portfolio_optimizer.allocation.budget import BudgetManager
from context_portfolio_optimizer.assembly.compiler import compile_for_chat
from context_portfolio_optimizer.memory.store import MemoryStore
from context_portfolio_optimizer.orchestration.planner import Planner
from context_portfolio_optimizer.orchestration.runner import PipelineRunner


def context_search(query: str, limit: int = 10) -> dict[str, Any]:
    """Search cached memory entries."""
    store = MemoryStore()
    return {"results": store.search(query=query, limit=limit)}


def context_compile(file_paths: list[str], budget: int = 3000) -> dict[str, Any]:
    """Compile optimized context into chat payload."""
    runner = PipelineRunner()
    result = runner.run(file_paths=file_paths, budget=budget)
    packet = result["context_packet"]
    return {
        "packet": packet,
        "messages": compile_for_chat(packet),
        "stats": result["stats"],
    }


def context_plan(task: str, budget: int = 8000) -> dict[str, Any]:
    """Build execution plan for a task."""
    planner = Planner(BudgetManager.from_total(budget))
    return planner.plan(task)


def context_memory(query: str | None = None, limit: int = 10) -> dict[str, Any]:
    """Read memory entries."""
    store = MemoryStore()
    return {"entries": store.search(query=query, limit=limit)}


def context_ablate(file_paths: list[str], budget: int = 3000) -> dict[str, Any]:
    """Run leave-one-out ablation on optimized blocks."""
    runner = PipelineRunner()
    result = runner.run(file_paths=file_paths, budget=budget)
    ablation_runner = AblationRunner()
    ablations = ablation_runner.run_leave_one_out(result["portfolio"].blocks, budget)
    return {
        "baseline": ablations[0].baseline_reward if ablations else 0.0,
        "count": len(ablations),
    }
