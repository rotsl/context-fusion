# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for provider-aware packet compilation."""

from context_portfolio_optimizer.assembly.compiler import compile_packet
from context_portfolio_optimizer.ir import ContextPacket, SelectedBlock


def _packet() -> ContextPacket:
    return ContextPacket(
        task="Answer with citations",
        task_type="qa",
        constraints={},
        selected_blocks=[
            SelectedBlock(
                block_id="b1",
                source_uri="doc.txt",
                modality="text",
                representation_type="extractive_span",
                text="Important evidence",
                tokens_est=2,
                score=0.9,
                freshness=1.0,
                trust=0.9,
                cacheable=True,
            )
        ],
        citations=["doc.txt"],
        budget={"retrieval": 400, "selected_tokens": 2},
    )


def test_compile_packet_openai_shape() -> None:
    payload = compile_packet(_packet(), provider="openai", model="gpt-5-mini", mode="qa")
    assert payload["provider"] == "openai"
    assert "request" in payload
    assert "messages" in payload["request"]


def test_compile_packet_ollama_shape() -> None:
    payload = compile_packet(_packet(), provider="ollama", model="qwen2.5", mode="chat")
    assert payload["request"]["model"] == "qwen2.5"
    assert payload["request"].get("stream") is False
