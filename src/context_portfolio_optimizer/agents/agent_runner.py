# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Agent loop support for ContextFusion."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from context_portfolio_optimizer.assembly.compiler import compile_for_chat
from context_portfolio_optimizer.fusion.incremental import IncrementalFusion
from context_portfolio_optimizer.orchestration.runner import PipelineRunner

if TYPE_CHECKING:
    from context_portfolio_optimizer.providers.base import LLMProvider


def agent_step(
    state: dict[str, Any],
    tools: list[dict[str, Any]],
    provider: LLMProvider,
    model: str,
) -> dict[str, Any]:
    """Run one agent step using optimized context and optional tool calls.

    Responsibilities:
    - update memory
    - call optimizer
    - assemble context
    - execute tool calls
    """
    next_state = dict(state)

    file_paths = list(next_state.get("file_paths", []))
    budget = int(next_state.get("budget", 3000))
    task = str(next_state.get("task", "agent_step"))

    runner = next_state.get("runner") or PipelineRunner()
    result = runner.run(
        file_paths=file_paths, budget=budget, task=task, task_type="agent", query=task
    )
    packet = result["context_packet"]
    incremental = next_state.get("incremental_fusion") or IncrementalFusion()
    delta = incremental.next_delta(packet)

    messages = compile_for_chat(packet)
    messages.append({"role": "user", "content": task})

    if tools:
        response = provider.tool_call(messages=messages, tools=tools, model=model)
    else:
        response = provider.chat(messages=messages, model=model)

    memory = list(next_state.get("memory", []))
    memory.append(
        {
            "task": task,
            "context_packet": packet,
            "delta": delta,
            "response": response,
        }
    )

    next_state["last_result"] = result
    next_state["last_delta"] = delta
    next_state["last_response"] = response
    next_state["memory"] = memory
    next_state["incremental_fusion"] = incremental

    return next_state
