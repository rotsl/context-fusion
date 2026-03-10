# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for two-stage retrieval components."""

from context_portfolio_optimizer.retrieval import BM25Retriever, SimpleReranker
from context_portfolio_optimizer.types import ContextBlock, SourceType


def _blocks() -> list[ContextBlock]:
    return [
        ContextBlock(
            id="b1",
            content="Paris is the capital of France.",
            source_type=SourceType.TEXT,
            token_count=6,
            trust_score=0.9,
        ),
        ContextBlock(
            id="b2",
            content="Docker deploy checklist for backend services.",
            source_type=SourceType.TEXT,
            token_count=6,
            trust_score=0.7,
        ),
    ]


def test_bm25_retrieves_relevant_block():
    retriever = BM25Retriever()
    results = retriever.retrieve("capital france", _blocks(), top_k=2)
    assert results
    assert results[0].id == "b1"


def test_reranker_orders_by_similarity_and_trust():
    reranker = SimpleReranker()
    ranked = reranker.rerank("capital france", _blocks(), top_k=2)
    assert ranked[0].id == "b1"
