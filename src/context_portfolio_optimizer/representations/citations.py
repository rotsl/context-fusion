# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Citation-oriented representation helpers."""

from __future__ import annotations

from typing import Any


def generate_citation_variants(block: Any) -> list[dict[str, Any]]:
    """Generate citation-centric context variants."""
    source = block.file_path or f"block:{block.id}"
    return [
        {
            "representation_type": "citation_pointer",
            "text": f"[{block.id}] {source}",
            "generation_cost": 0.05,
            "suitability_tags": ["citation"],
        }
    ]
