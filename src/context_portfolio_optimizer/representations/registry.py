# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Registry for compact, task-aware representation variants."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from context_portfolio_optimizer.utils.tokenization import count_tokens

from .agent import generate_agent_variants
from .citations import generate_citation_variants
from .code import generate_code_variants
from .compact import generate_compact_variants
from .qa import generate_qa_variants


@dataclass
class RepresentationVariant:
    """Task-aware representation variant."""

    representation_type: str
    text: str
    token_estimate: int
    generation_cost: float
    suitability_tags: list[str] = field(default_factory=list)
    fidelity_score: float = 1.0


class RepresentationRegistry:
    """Generate and rank compact representation variants for a block."""

    def generate_all(self, block: Any, task_type: str) -> list[RepresentationVariant]:
        """Generate representation variants for a given block and task type."""
        raw_variants: list[dict[str, Any]] = []

        raw_variants.extend(generate_compact_variants(block))
        raw_variants.extend(generate_citation_variants(block))

        task = task_type.lower()
        if task in {"qa", "retrieval", "chat"}:
            raw_variants.extend(generate_qa_variants(block))
        if task in {"code", "debug"}:
            raw_variants.extend(generate_code_variants(block))
        if task in {"agent", "planning", "tool"}:
            raw_variants.extend(generate_agent_variants(block))

        # Code-like blocks also get code variants independent of task.
        path = str(getattr(block, "file_path", "")).lower()
        source_name = str(getattr(getattr(block, "source_type", None), "name", "")).upper()
        if source_name == "CODE" or path.endswith((".py", ".js", ".ts", ".go", ".rs", ".java")):
            raw_variants.extend(generate_code_variants(block))

        variants: list[RepresentationVariant] = []
        seen: set[tuple[str, str]] = set()

        for item in raw_variants:
            rep_type = str(item.get("representation_type", "unknown"))
            text = str(item.get("text", "")).strip()
            if not text:
                continue
            key = (rep_type, text)
            if key in seen:
                continue
            seen.add(key)

            fidelity = min(1.0, len(text) / max(1, len(str(block.content))))
            variants.append(
                RepresentationVariant(
                    representation_type=rep_type,
                    text=text,
                    token_estimate=count_tokens(text),
                    generation_cost=float(item.get("generation_cost", 0.1)),
                    suitability_tags=list(item.get("suitability_tags", [])),
                    fidelity_score=fidelity,
                )
            )

        variants.sort(key=lambda variant: (variant.token_estimate, -variant.fidelity_score))
        return variants
