# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Second-stage reranker for retrieved context blocks."""

from __future__ import annotations

from typing import TYPE_CHECKING

from context_portfolio_optimizer.utils.similarity import text_similarity

if TYPE_CHECKING:
    from context_portfolio_optimizer.types import ContextBlock


class SimpleReranker:
    """Rerank blocks by lexical similarity and trust."""

    def rerank(
        self,
        query: str,
        blocks: list[ContextBlock],
        top_k: int = 20,
    ) -> list[ContextBlock]:
        """Rerank and return top-K blocks."""
        if not query or not blocks:
            return []

        scored: list[tuple[float, ContextBlock]] = []
        for block in blocks:
            similarity = text_similarity(query, block.content)
            score = (0.8 * similarity) + (0.2 * block.trust_score)
            scored.append((score, block))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [block for _, block in scored[:top_k]]
