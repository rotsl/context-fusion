# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for context compiler utilities."""

from context_portfolio_optimizer.assembly.compiler import (
    compile_for_chat,
    compile_for_provider,
    compile_plain_text,
)
from context_portfolio_optimizer.ir import CacheSegment, ContextPacket, SelectedBlock


def _packet() -> ContextPacket:
    return ContextPacket(
        task="Summarize",
        task_type="chat",
        constraints={"max_tokens": 1000},
        selected_blocks=[
            SelectedBlock(
                block_id="blk_1",
                source_uri="doc.txt",
                modality="text",
                representation_type="full_text",
                text="Important context block",
                tokens_est=4,
                score=0.8,
                freshness=1.0,
                trust=0.9,
                cacheable=True,
            )
        ],
        citations=["doc.txt"],
        budget={"retrieval": 1000},
        cache_segments=[
            CacheSegment(
                name="block:blk_1",
                text="Important context block",
                stable=True,
                cache_key="seg:test",
                tokens_est=4,
            )
        ],
        output_contract=None,
    )


def test_compile_for_chat():
    messages = compile_for_chat(_packet())
    assert messages[0]["role"] == "system"
    assert any("Important context block" in msg["content"] for msg in messages)


def test_compile_plain_text_and_provider_payload():
    packet = _packet()
    text = compile_plain_text(packet)
    assert "Important context block" in text

    payload = compile_for_provider(packet, provider_name="anthropic")
    assert "messages" in payload
    assert payload["metadata"]["citations"] == ["doc.txt"]
