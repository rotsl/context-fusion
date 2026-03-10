# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for context delta fusion."""

from context_portfolio_optimizer.fusion.delta import compute_context_delta
from context_portfolio_optimizer.ir import ContextPacket, SelectedBlock


def _packet(block_id: str, text: str) -> ContextPacket:
    return ContextPacket(
        task="agent",
        task_type="agent",
        constraints={},
        selected_blocks=[
            SelectedBlock(
                block_id=block_id,
                source_uri=f"{block_id}.txt",
                modality="text",
                representation_type="working_memory_brief",
                text=text,
                tokens_est=5,
                score=0.7,
                freshness=1.0,
                trust=0.8,
                cacheable=True,
            )
        ],
        citations=[f"{block_id}.txt"],
        budget={"retrieval": 200, "selected_tokens": 5},
    )


def test_delta_excludes_unchanged_blocks() -> None:
    old_packet = _packet("b1", "same")
    new_packet = _packet("b1", "same")

    delta = compute_context_delta(old_packet, new_packet)
    assert delta.unchanged_block_ids == ["b1"]
    assert not delta.added_blocks
    assert not delta.updated_blocks


def test_delta_detects_added_and_removed() -> None:
    old_packet = _packet("b1", "old")
    new_packet = _packet("b2", "new")

    delta = compute_context_delta(old_packet, new_packet)
    assert len(delta.added_blocks) == 1
    assert delta.removed_block_ids == ["b1"]
