# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Agent-loop delta fusion benchmark."""

from __future__ import annotations

import tempfile
from pathlib import Path

from context_portfolio_optimizer.fusion.delta import compute_context_delta
from context_portfolio_optimizer.orchestration.runner import PipelineRunner


def run_agent_loop_benchmark() -> dict[str, int]:
    runner = PipelineRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir)
        file_a = data_dir / "state.txt"
        file_a.write_text("Initial state for the agent loop benchmark.", encoding="utf-8")

        old_packet = runner.run_on_directory(
            str(data_dir), budget=900, query="Agent state summary", task_type="agent"
        )["context_packet"]

        file_a.write_text(
            "Initial state for the agent loop benchmark.\nTool result: one more update.",
            encoding="utf-8",
        )
        new_packet = runner.run_on_directory(
            str(data_dir), budget=900, query="Agent state summary", task_type="agent"
        )["context_packet"]

    delta = compute_context_delta(old_packet, new_packet)
    return {
        "added": len(delta.added_blocks),
        "updated": len(delta.updated_blocks),
        "removed": len(delta.removed_block_ids),
        "unchanged": len(delta.unchanged_block_ids),
    }


if __name__ == "__main__":
    metrics = run_agent_loop_benchmark()
    print(metrics)
