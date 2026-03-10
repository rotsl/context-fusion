# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Metadata filtering utilities for retrieval narrowing."""

from __future__ import annotations

from context_portfolio_optimizer.types import ContextBlock


def filter_candidates(
    blocks: list[ContextBlock],
    *,
    source_types: set[str] | None = None,
    min_freshness: float | None = None,
    tags: set[str] | None = None,
    file_path_contains: str | None = None,
    modality: str | None = None,
) -> list[ContextBlock]:
    """Filter candidates by metadata constraints."""
    filtered: list[ContextBlock] = []

    for block in blocks:
        if source_types and block.source_type.name.lower() not in source_types:
            continue
        if min_freshness is not None and block.freshness < min_freshness:
            continue
        if tags and not tags.intersection(set(block.tags)):
            continue
        if file_path_contains and file_path_contains not in block.file_path:
            continue
        if modality and block.source_type.name.lower() != modality.lower():
            continue
        filtered.append(block)

    return filtered
