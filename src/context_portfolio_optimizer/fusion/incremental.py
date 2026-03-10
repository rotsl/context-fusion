# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Incremental fusion helpers for repeated agent turns."""

from __future__ import annotations

from context_portfolio_optimizer.fusion.packet_diff import diff_packets
from context_portfolio_optimizer.ir import ContextDelta, ContextPacket


class IncrementalFusion:
    """Stateful helper to compute packet deltas across turns."""

    def __init__(self):
        self.previous_packet: ContextPacket | None = None

    def next_delta(self, packet: ContextPacket) -> ContextDelta:
        """Compute delta against previous packet and update internal state."""
        delta = diff_packets(self.previous_packet, packet)
        self.previous_packet = packet
        return delta
