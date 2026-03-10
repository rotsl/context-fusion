# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Precompute pipeline for low-latency context optimization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.memory.store import MemoryStore
from context_portfolio_optimizer.normalization.block_builder import BlockBuilder
from context_portfolio_optimizer.representations.base_representation import RepresentationGenerator
from context_portfolio_optimizer.utils.hashing import compute_hash


class PrecomputeRunner:
    """Runs offline precomputation for summaries/tokens/hashes/embeddings."""

    def __init__(
        self,
        dispatcher: IngestionDispatcher | None = None,
        block_builder: BlockBuilder | None = None,
        rep_generator: RepresentationGenerator | None = None,
        memory_store: MemoryStore | None = None,
    ):
        self.dispatcher = dispatcher or IngestionDispatcher()
        self.block_builder = block_builder or BlockBuilder()
        self.rep_generator = rep_generator or RepresentationGenerator()
        self.memory_store = memory_store or MemoryStore()

    def run_on_directory(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = True,
    ) -> dict[str, Any]:
        """Precompute context artifacts for all files in a directory."""
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        results = self.dispatcher.load_directory(directory, pattern=pattern, recursive=recursive)

        total_segments = 0
        total_blocks = 0
        stored_entries = 0

        for source_path, segments in results.items():
            total_segments += len(segments)
            blocks = self.block_builder.build_blocks(segments)
            total_blocks += len(blocks)

            for block in blocks:
                reps = self.rep_generator.generate_for_block(block)
                serializable_reps = {rep_type.value: content for rep_type, content in reps.items()}
                embedding = self._pseudo_embedding(block.content)
                metadata = {
                    "source_path": source_path,
                    "block_id": block.id,
                    "token_count": block.token_count,
                    "content_hash": compute_hash(block.content),
                    "representations": serializable_reps,
                    "embedding": embedding,
                }
                self.memory_store.append(
                    content=block.content,
                    metadata=metadata,
                    entry_type="precompute",
                )
                stored_entries += 1

        return {
            "files_processed": len(results),
            "segments_processed": total_segments,
            "blocks_processed": total_blocks,
            "entries_stored": stored_entries,
        }

    def _pseudo_embedding(self, text: str, dims: int = 16) -> list[float]:
        """Deterministic embedding placeholder for latency precompute path."""
        digest = compute_hash(text)
        values: list[float] = []
        for idx in range(dims):
            start = (idx * 2) % len(digest)
            chunk = digest[start : start + 2]
            values.append(int(chunk, 16) / 255.0)
        return values
