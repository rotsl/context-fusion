# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Lightweight BM25-style lexical retriever."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from context_portfolio_optimizer.types import ContextBlock


class BM25Retriever:
    """Simple BM25 retriever for ContextBlock sets."""

    def __init__(self, k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b

    def retrieve(
        self,
        query: str,
        blocks: list[ContextBlock],
        top_k: int = 100,
    ) -> list[ContextBlock]:
        """Retrieve top-K blocks by lexical relevance."""
        if not query or not blocks:
            return []

        tokenized_docs = [self._tokenize(block.content) for block in blocks]
        doc_freq: defaultdict[str, int] = defaultdict(int)
        for tokens in tokenized_docs:
            for token in set(tokens):
                doc_freq[token] += 1

        avgdl = sum(len(tokens) for tokens in tokenized_docs) / max(1, len(tokenized_docs))
        query_tokens = self._tokenize(query)

        scored: list[tuple[float, ContextBlock]] = []
        total_docs = len(blocks)

        for block, tokens in zip(blocks, tokenized_docs, strict=False):
            tf = Counter(tokens)
            score = 0.0
            for token in query_tokens:
                if token not in tf:
                    continue
                df = doc_freq[token]
                idf = math.log((total_docs - df + 0.5) / (df + 0.5) + 1)
                freq = tf[token]
                denom = freq + self.k1 * (1 - self.b + self.b * (len(tokens) / max(1e-6, avgdl)))
                score += idf * (freq * (self.k1 + 1) / denom)
            scored.append((score, block))

        scored.sort(key=lambda pair: pair[0], reverse=True)
        return [block for _, block in scored[:top_k] if _ > 0]

    def _tokenize(self, text: str) -> list[str]:
        return [token.strip(".,:;!?()[]{}\"'").lower() for token in text.split() if token.strip()]
