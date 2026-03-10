# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Compression policy definitions for provider packet assembly."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CompressionPolicy:
    """Policy toggles for compact packet assembly."""

    level: str = "none"
    minify_json: bool = False
    prune_schema: bool = False
    compact_citations: bool = False


def resolve_compression_policy(level: str) -> CompressionPolicy:
    """Resolve named compression level into concrete toggles."""
    normalized = level.lower().strip()
    if normalized in {"none", "off"}:
        return CompressionPolicy(level="none")
    if normalized in {"light", "l1"}:
        return CompressionPolicy(level="light", minify_json=True, compact_citations=True)
    if normalized in {"medium", "l2"}:
        return CompressionPolicy(
            level="medium",
            minify_json=True,
            prune_schema=True,
            compact_citations=True,
        )
    if normalized in {"aggressive", "l3"}:
        return CompressionPolicy(
            level="aggressive",
            minify_json=True,
            prune_schema=True,
            compact_citations=True,
        )
    return CompressionPolicy(level=normalized)
