# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""LlamaIndex integration wrappers."""

from __future__ import annotations

from typing import Any

from context_portfolio_optimizer.orchestration.runner import PipelineRunner


class ContextFusionLlamaIndexRetriever:
    """Retriever wrapper in a LlamaIndex-like shape."""

    def __init__(self, file_paths: list[str], budget: int = 3000):
        self.file_paths = file_paths
        self.budget = budget
        self.runner = PipelineRunner()

    def retrieve(self, query: str) -> list[dict[str, Any]]:
        """Return selected blocks in a node-like dictionary form."""
        result = self.runner.run(self.file_paths, budget=self.budget)
        packet = result["context_packet"]
        return [
            {
                "text": block.text,
                "metadata": {
                    "id": block.block_id,
                    "source": block.source_uri,
                    "query": query,
                },
            }
            for block in packet.selected_blocks
        ]
