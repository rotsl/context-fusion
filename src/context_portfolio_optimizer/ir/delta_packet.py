# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Context packet delta type for incremental agent loops."""

from dataclasses import dataclass, field

from .context_packet import SelectedBlock


@dataclass
class ContextDelta:
    """Difference between two context packets."""

    previous_packet_hash: str
    added_blocks: list[SelectedBlock] = field(default_factory=list)
    removed_block_ids: list[str] = field(default_factory=list)
    updated_blocks: list[SelectedBlock] = field(default_factory=list)
    unchanged_block_ids: list[str] = field(default_factory=list)
