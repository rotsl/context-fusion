# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Universal compact representations optimized for token efficiency."""

from __future__ import annotations

import json
import re
from typing import Any

_WS_RE = re.compile(r"\s+")


def generate_compact_variants(block: Any) -> list[dict[str, Any]]:
    """Generate universal compact variants for any block."""
    text = str(block.content)
    source = block.file_path or f"block:{block.id}"

    minified_text = _WS_RE.sub(" ", text).strip()
    variants: list[dict[str, Any]] = [
        {
            "representation_type": "minified_text",
            "text": minified_text,
            "generation_cost": 0.2,
            "suitability_tags": ["universal", "compact"],
        },
        {
            "representation_type": "citation_pointer",
            "text": f"[{block.id}] {source}",
            "generation_cost": 0.05,
            "suitability_tags": ["citation", "compact"],
        },
    ]

    pruned_json = _field_pruned_json(text)
    if pruned_json:
        variants.append(
            {
                "representation_type": "field_pruned_json",
                "text": pruned_json,
                "generation_cost": 0.35,
                "suitability_tags": ["json", "compact"],
            }
        )

    return variants


def _field_pruned_json(text: str) -> str:
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        return ""

    if isinstance(data, dict):
        keys = sorted(data)[:6]
        slim = {key: data[key] for key in keys}
        return json.dumps(slim, separators=(",", ":"), ensure_ascii=False)

    if isinstance(data, list):
        slim_list = data[:3]
        return json.dumps(slim_list, separators=(",", ":"), ensure_ascii=False)

    return ""
