# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Deterministic query classification for retrieval strategy selection."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class QueryClass:
    """Query classification result."""

    task_type: str
    source_types: set[str]
    min_freshness: float | None
    preferred_limit: int


def classify_query(query: str) -> QueryClass:
    """Classify task for retrieval and packing decisions."""
    text = query.lower()

    if any(token in text for token in {"code", "bug", "stacktrace", "function", "test"}):
        return QueryClass(
            task_type="code", source_types={"code", "text"}, min_freshness=None, preferred_limit=120
        )

    if any(token in text for token in {"agent", "tool", "plan", "state", "next step"}):
        return QueryClass(
            task_type="agent", source_types=set(), min_freshness=0.2, preferred_limit=80
        )

    if any(token in text for token in {"cite", "citation", "evidence", "source"}):
        return QueryClass(
            task_type="qa", source_types=set(), min_freshness=0.1, preferred_limit=100
        )

    return QueryClass(task_type="chat", source_types=set(), min_freshness=None, preferred_limit=100)
