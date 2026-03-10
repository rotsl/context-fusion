# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Packet diff convenience helpers."""

from __future__ import annotations

from context_portfolio_optimizer.fusion.delta import compute_context_delta
from context_portfolio_optimizer.ir import ContextDelta, ContextPacket


def diff_packets(old_packet: ContextPacket | None, new_packet: ContextPacket) -> ContextDelta:
    """Return full-add delta if old packet is missing, else compute normal delta."""
    if old_packet is None:
        return ContextDelta(
            previous_packet_hash="",
            added_blocks=list(new_packet.selected_blocks),
            removed_block_ids=[],
            updated_blocks=[],
            unchanged_block_ids=[],
        )
    return compute_context_delta(old_packet, new_packet)
