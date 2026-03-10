# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Precompute pipeline for low-latency context optimization."""

from __future__ import annotations

from pathlib import Path
from typing import Any

from context_portfolio_optimizer.dedup import deduplicate_blocks, normalized_text_hash
from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.normalization.block_builder import BlockBuilder
from context_portfolio_optimizer.precompute.embeddings import pseudo_embedding
from context_portfolio_optimizer.precompute.store import PrecomputedBlock, PrecomputeStore
from context_portfolio_optimizer.precompute.summaries import outline_summary, summarize_sentences
from context_portfolio_optimizer.precompute.token_stats import token_features
from context_portfolio_optimizer.representations.registry import RepresentationRegistry


class PrecomputeRunner:
    """Runs offline precomputation for summaries/tokens/hashes/embeddings."""

    def __init__(
        self,
        dispatcher: IngestionDispatcher | None = None,
        block_builder: BlockBuilder | None = None,
        store: PrecomputeStore | None = None,
        rep_registry: RepresentationRegistry | None = None,
    ):
        self.dispatcher = dispatcher or IngestionDispatcher()
        self.block_builder = block_builder or BlockBuilder()
        self.store = store or PrecomputeStore()
        self.rep_registry = rep_registry or RepresentationRegistry()

    def run_on_directory(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = True,
        enable_semantic_dedup: bool = True,
    ) -> dict[str, Any]:
        """Precompute context artifacts for all files in a directory."""
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        results = self.dispatcher.load_directory(directory, pattern=pattern, recursive=recursive)

        all_blocks = []
        total_segments = 0

        for source_path, segments in results.items():
            total_segments += len(segments)
            blocks = self.block_builder.build_blocks(segments)
            for block in blocks:
                if not block.file_path:
                    block.file_path = source_path
            all_blocks.extend(blocks)

        deduped_blocks = deduplicate_blocks(
            all_blocks,
            enable_semantic=enable_semantic_dedup,
        )

        stored_entries = 0
        for block in deduped_blocks:
            variants = self.rep_registry.generate_all(block, task_type="retrieval")
            representations = {variant.representation_type: variant.text for variant in variants}
            representations.setdefault(
                "summary_3", summarize_sentences(block.content, max_sentences=3)
            )
            representations.setdefault("outline", outline_summary(block.content))

            features = token_features(block.content)
            features["line_count"] = len(
                [line for line in block.content.splitlines() if line.strip()]
            )
            metadata = {
                "source_path": block.file_path,
                "duplicate_sources": block.metadata.get("duplicate_sources", []),
                "embedding": pseudo_embedding(block.content),
            }

            self.store.put_block(
                PrecomputedBlock(
                    block_id=block.id,
                    source_uri=block.file_path or f"block:{block.id}",
                    content=block.content,
                    token_count=block.token_count,
                    fingerprint=normalized_text_hash(block.content),
                    representations=representations,
                    retrieval_features=features,
                    metadata=metadata,
                )
            )
            stored_entries += 1

        return {
            "files_processed": len(results),
            "segments_processed": total_segments,
            "blocks_processed": len(all_blocks),
            "blocks_after_dedup": len(deduped_blocks),
            "entries_stored": stored_entries,
        }
