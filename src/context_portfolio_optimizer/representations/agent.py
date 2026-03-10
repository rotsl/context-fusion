# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Agent-loop-oriented compact representations."""

from __future__ import annotations

import re
from typing import Any

_ENTITY_RE = re.compile(r"\b[A-Z][a-zA-Z0-9_]+\b")


def generate_agent_variants(block: Any) -> list[dict[str, Any]]:
    """Generate context forms tuned for agent state updates."""
    text = str(block.content)
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    first_lines = lines[:5]

    constraints = [
        line for line in lines if any(key in line.lower() for key in ("must", "should", "require"))
    ]
    entities = sorted(set(_ENTITY_RE.findall(text)))[:12]

    return [
        {
            "representation_type": "state_summary",
            "text": " ".join(first_lines[:2]),
            "generation_cost": 0.1,
            "suitability_tags": ["agent", "state"],
        },
        {
            "representation_type": "constraint_delta",
            "text": "\n".join(constraints[:6]),
            "generation_cost": 0.2,
            "suitability_tags": ["agent", "constraints"],
        },
        {
            "representation_type": "tool_result_minified",
            "text": " ".join(first_lines),
            "generation_cost": 0.05,
            "suitability_tags": ["agent", "tools"],
        },
        {
            "representation_type": "entity_memory",
            "text": ", ".join(entities),
            "generation_cost": 0.12,
            "suitability_tags": ["agent", "memory"],
        },
        {
            "representation_type": "working_memory_brief",
            "text": "\n".join(f"- {line}" for line in first_lines[:4]),
            "generation_cost": 0.18,
            "suitability_tags": ["agent", "working_memory"],
        },
    ]
