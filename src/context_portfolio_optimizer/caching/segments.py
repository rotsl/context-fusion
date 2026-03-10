# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Cache segmentation for context packets."""

from __future__ import annotations

from context_portfolio_optimizer.ir import CacheSegment, ContextPacket
from context_portfolio_optimizer.utils.tokenization import count_tokens

from .keys import stable_cache_key


def build_cache_segments(packet: ContextPacket) -> list[CacheSegment]:
    """Split packet into stable and dynamic segments for prompt caching."""
    segments: list[CacheSegment] = []

    instruction_text = f"Task: {packet.task}\nTaskType: {packet.task_type}"
    instruction_segment = CacheSegment(
        name="system_instruction",
        text=instruction_text,
        stable=True,
        cache_key=stable_cache_key("system_instruction", instruction_text),
        tokens_est=count_tokens(instruction_text),
    )
    segments.append(instruction_segment)

    citation_text = "\n".join(packet.citations)
    citation_segment = CacheSegment(
        name="citation_map",
        text=citation_text,
        stable=True,
        cache_key=stable_cache_key("citation_map", citation_text),
        tokens_est=count_tokens(citation_text),
    )
    segments.append(citation_segment)

    for block in packet.selected_blocks:
        stable = bool(block.cacheable)
        name = f"block:{block.block_id}"
        cache_key = stable_cache_key(name, block.text) if stable else None
        segments.append(
            CacheSegment(
                name=name,
                text=block.text,
                stable=stable,
                cache_key=cache_key,
                tokens_est=block.tokens_est,
            )
        )

    return segments
