# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""QA-mode packet packing."""

from __future__ import annotations

from context_portfolio_optimizer.ir import ContextPacket


def pack_qa(packet: ContextPacket) -> list[dict[str, str]]:
    """Pack packet prioritizing extractive/citation material."""
    messages: list[dict[str, str]] = [
        {
            "role": "system",
            "content": "Answer with concise evidence and citations.",
        }
    ]

    ranked = sorted(
        packet.selected_blocks,
        key=lambda block: (
            "extractive" not in block.representation_type,
            "citation" not in block.representation_type,
            block.tokens_est,
        ),
    )
    for block in ranked:
        messages.append({"role": "system", "content": block.text})

    if packet.citations:
        citation_map = "\n".join(
            f"[{idx + 1}] {source}" for idx, source in enumerate(packet.citations)
        )
        messages.append({"role": "system", "content": f"Citation map:\n{citation_map}"})

    return messages
