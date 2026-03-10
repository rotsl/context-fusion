# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""LangChain integration wrappers."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from context_portfolio_optimizer.orchestration.runner import PipelineRunner


@dataclass
class LangChainDocument:
    """Minimal LangChain-like document object."""

    page_content: str
    metadata: dict[str, Any]


class ContextFusionLangChainRetriever:
    """Retriever wrapper compatible with LangChain retrieval style."""

    def __init__(self, file_paths: list[str], budget: int = 3000):
        self.file_paths = file_paths
        self.budget = budget
        self.runner = PipelineRunner()

    def get_relevant_documents(self, query: str) -> list[LangChainDocument]:
        """Return optimized selected blocks as documents."""
        result = self.runner.run(
            self.file_paths, budget=self.budget, query=query, task=query, task_type="chat"
        )
        packet = result["context_packet"]
        return [
            LangChainDocument(
                page_content=block.text,
                metadata={
                    "block_id": block.block_id,
                    "source_uri": block.source_uri,
                    "query": query,
                },
            )
            for block in packet.selected_blocks
        ]
