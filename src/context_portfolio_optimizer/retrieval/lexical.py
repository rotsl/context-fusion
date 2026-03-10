# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Lexical retrieval stage for candidate generation."""

from __future__ import annotations

from context_portfolio_optimizer.retrieval.bm25 import BM25Retriever
from context_portfolio_optimizer.types import ContextBlock


def lexical_retrieve(
    query: str, blocks: list[ContextBlock], limit: int = 100
) -> list[ContextBlock]:
    """Retrieve candidates with deterministic BM25-like lexical ranking."""
    retriever = BM25Retriever()
    return retriever.retrieve(query=query, blocks=blocks, top_k=limit)
