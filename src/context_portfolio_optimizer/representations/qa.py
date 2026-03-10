# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Task-specific QA representations."""

from __future__ import annotations

import json
from typing import Any


def generate_qa_variants(block: Any) -> list[dict[str, Any]]:
    """Generate compact QA-focused variants."""
    lines = [line.strip() for line in str(block.content).splitlines() if line.strip()]
    body = " ".join(lines)
    sentences = [part.strip() for part in body.split(".") if part.strip()]

    extractive = sentences[0] if sentences else body[:240]
    bullets = "\n".join(f"- {sentence}" for sentence in sentences[:3])
    facts = {"facts": sentences[:3], "source": block.file_path or block.id}
    outline = "\n".join(f"{idx + 1}. {sentence}" for idx, sentence in enumerate(sentences[:5]))

    return [
        {
            "representation_type": "extractive_span",
            "text": extractive,
            "generation_cost": 0.1,
            "suitability_tags": ["qa", "evidence"],
        },
        {
            "representation_type": "bullet_summary_3",
            "text": bullets,
            "generation_cost": 0.2,
            "suitability_tags": ["qa", "summary"],
        },
        {
            "representation_type": "json_fact",
            "text": json.dumps(facts, separators=(",", ":"), ensure_ascii=False),
            "generation_cost": 0.3,
            "suitability_tags": ["qa", "structured"],
        },
        {
            "representation_type": "citation_only",
            "text": f"[{block.id}] {block.file_path or block.id}",
            "generation_cost": 0.05,
            "suitability_tags": ["qa", "citation"],
        },
        {
            "representation_type": "outline",
            "text": outline,
            "generation_cost": 0.25,
            "suitability_tags": ["qa", "outline"],
        },
    ]
