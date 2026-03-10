# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Agent-loop packet packing."""

from __future__ import annotations

from context_portfolio_optimizer.ir import ContextPacket


def pack_agent(packet: ContextPacket) -> list[dict[str, str]]:
    """Pack packet for iterative agent turns with minimal history churn."""
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": "Use only current constraints, tool deltas, and working memory.",
        }
    ]

    ranked = sorted(
        packet.selected_blocks,
        key=lambda block: (
            "working_memory" not in block.representation_type,
            "constraint" not in block.representation_type,
            block.tokens_est,
        ),
    )

    for block in ranked:
        messages.append({"role": "system", "content": block.text})

    return messages
