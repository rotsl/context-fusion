# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Fingerprint helpers for block and packet IR objects."""

from __future__ import annotations

import hashlib
import json

from .context_packet import ContextPacket, SelectedBlock


def block_fingerprint(block: SelectedBlock) -> str:
    """Return deterministic fingerprint for a selected block."""
    payload = {
        "block_id": block.block_id,
        "source_uri": block.source_uri,
        "representation_type": block.representation_type,
        "text": block.text,
        "tokens_est": block.tokens_est,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def packet_fingerprint(packet: ContextPacket) -> str:
    """Return deterministic fingerprint for a context packet."""
    payload = {
        "task": packet.task,
        "task_type": packet.task_type,
        "constraints": packet.constraints,
        "budget": packet.budget,
        "selected_blocks": [
            {
                "id": block.block_id,
                "fp": block.fingerprint or block_fingerprint(block),
            }
            for block in packet.selected_blocks
        ],
        "citations": packet.citations,
    }
    raw = json.dumps(payload, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
