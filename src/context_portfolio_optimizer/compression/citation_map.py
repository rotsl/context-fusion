# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Citation ID mapping helpers."""

from __future__ import annotations


def build_citation_id_map(citations: list[str]) -> dict[str, int]:
    """Build deterministic citation map from source URI to compact index."""
    return {citation: idx + 1 for idx, citation in enumerate(citations)}


def apply_citation_map(text: str, citation_map: dict[str, int]) -> str:
    """Replace verbose citation strings with compact [id] markers."""
    compact = text
    for source, idx in citation_map.items():
        compact = compact.replace(source, f"[{idx}]")
    return compact
