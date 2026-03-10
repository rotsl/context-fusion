# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Chat-mode packet packing."""

from __future__ import annotations

from context_portfolio_optimizer.ir import ContextPacket


def pack_chat(packet: ContextPacket) -> list[dict[str, str]]:
    """Pack packet as concise chat messages."""
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": f"Task: {packet.task}\nMode: {packet.task_type}",
        }
    ]
    for block in packet.selected_blocks:
        messages.append({"role": "system", "content": block.text})
    return messages
