# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Canonical ContextFusion intermediate representation."""

from dataclasses import dataclass
from typing import Any


@dataclass
class SelectedBlock:
    """A selected context block in canonical IR form."""

    block_id: str
    source_uri: str
    modality: str
    representation_type: str
    text: str
    tokens_est: int
    score: float
    freshness: float
    trust: float
    cacheable: bool


@dataclass
class ContextPacket:
    """Provider-agnostic context packet for chat and agent workflows."""

    task: str
    task_type: str
    constraints: dict[str, Any]
    selected_blocks: list[SelectedBlock]
    citations: list[str]
    budget: dict[str, int]
    cache_segments: list[str]
    output_contract: dict[str, Any] | None
