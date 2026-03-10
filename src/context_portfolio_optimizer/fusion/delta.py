# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Delta computation between context packets."""

from __future__ import annotations

from context_portfolio_optimizer.ir import ContextDelta, ContextPacket, packet_fingerprint


def compute_context_delta(old_packet: ContextPacket, new_packet: ContextPacket) -> ContextDelta:
    """Compute incremental packet delta for agent loops."""
    old_by_id = {block.block_id: block for block in old_packet.selected_blocks}
    new_by_id = {block.block_id: block for block in new_packet.selected_blocks}

    added_blocks = [block for block_id, block in new_by_id.items() if block_id not in old_by_id]
    removed_block_ids = [block_id for block_id in old_by_id if block_id not in new_by_id]

    updated_blocks = []
    unchanged_block_ids = []

    for block_id, new_block in new_by_id.items():
        if block_id not in old_by_id:
            continue
        old_block = old_by_id[block_id]

        old_fp = (
            old_block.fingerprint
            or f"{old_block.representation_type}:{old_block.tokens_est}:{old_block.text}"
        )
        new_fp = (
            new_block.fingerprint
            or f"{new_block.representation_type}:{new_block.tokens_est}:{new_block.text}"
        )

        if old_fp == new_fp:
            unchanged_block_ids.append(block_id)
        else:
            updated_blocks.append(new_block)

    return ContextDelta(
        previous_packet_hash=packet_fingerprint(old_packet),
        added_blocks=added_blocks,
        removed_block_ids=removed_block_ids,
        updated_blocks=updated_blocks,
        unchanged_block_ids=unchanged_block_ids,
    )
