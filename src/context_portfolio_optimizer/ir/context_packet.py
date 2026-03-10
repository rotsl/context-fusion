# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Canonical ContextFusion intermediate representation."""

from dataclasses import dataclass, field
from typing import Any

from .cache_segment import CacheSegment


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
    utility: float = 0.0
    risk: float = 0.0
    fingerprint: str | None = None
    parent_block_id: str | None = None


@dataclass
class ContextPacket:
    """Provider-agnostic context packet for chat and agent workflows."""

    task: str
    task_type: str
    constraints: dict[str, Any]
    selected_blocks: list[SelectedBlock]
    citations: list[str]
    budget: dict[str, int]
    cache_segments: list[CacheSegment] = field(default_factory=list)
    output_contract: dict[str, Any] | None = None
    provider_hint: str | None = None
    model_hint: str | None = None
