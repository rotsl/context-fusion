# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for deduplication and fingerprinting."""

from context_portfolio_optimizer.dedup.semantic_dedup import deduplicate_blocks
from context_portfolio_optimizer.types import ContextBlock, SourceType


def _block(block_id: str, content: str, file_path: str = "") -> ContextBlock:
    return ContextBlock(
        id=block_id,
        content=content,
        source_type=SourceType.TEXT,
        file_path=file_path or f"/{block_id}.txt",
        token_count=max(1, len(content.split())),
        trust_score=0.8,
        freshness=0.9,
    )


def test_exact_duplicates_collapse() -> None:
    blocks = [
        _block("a", "same payload", "a.txt"),
        _block("b", "same payload", "b.txt"),
    ]

    deduped = deduplicate_blocks(blocks)
    assert len(deduped) == 1
    assert "b.txt" in deduped[0].metadata.get("duplicate_sources", [])


def test_near_duplicates_collapse() -> None:
    blocks = [
        _block("a", "Alpha beta gamma delta", "a.txt"),
        _block("b", "Alpha beta gamma delta extra", "b.txt"),
    ]

    deduped = deduplicate_blocks(blocks, semantic_threshold=0.7, enable_semantic=True)
    assert len(deduped) == 1
