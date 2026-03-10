# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for cache-aware segment assembly."""

from context_portfolio_optimizer.caching.segments import build_cache_segments
from context_portfolio_optimizer.ir import ContextPacket, SelectedBlock


def _packet() -> ContextPacket:
    return ContextPacket(
        task="qa",
        task_type="qa",
        constraints={},
        selected_blocks=[
            SelectedBlock(
                block_id="b1",
                source_uri="doc.txt",
                modality="text",
                representation_type="extractive_span",
                text="Evidence line",
                tokens_est=3,
                score=0.8,
                freshness=1.0,
                trust=0.9,
                cacheable=True,
            )
        ],
        citations=["doc.txt"],
        budget={"retrieval": 100, "selected_tokens": 3},
    )


def test_cache_segments_deterministic() -> None:
    packet = _packet()
    first = build_cache_segments(packet)
    second = build_cache_segments(packet)

    assert [segment.cache_key for segment in first] == [segment.cache_key for segment in second]
    assert any(segment.stable for segment in first)
