# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Code/debug-mode packet packing."""

from __future__ import annotations

from context_portfolio_optimizer.ir import ContextPacket


def pack_code(packet: ContextPacket) -> list[dict[str, str]]:
    """Pack packet prioritizing signatures, imports, and changed snippets."""
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": "Focus on debugging context: signatures, changed regions, and failing evidence.",
        }
    ]

    preferred = sorted(
        packet.selected_blocks,
        key=lambda block: (
            "signature" not in block.representation_type,
            "changed" not in block.representation_type,
            block.tokens_est,
        ),
    )
    for block in preferred:
        header = f"[{block.source_uri}] {block.representation_type}"
        messages.append({"role": "system", "content": f"{header}\n{block.text}"})

    return messages
