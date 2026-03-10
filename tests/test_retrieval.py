# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for two-stage retrieval components."""

from context_portfolio_optimizer.precompute.store import PrecomputedBlock, PrecomputeStore
from context_portfolio_optimizer.retrieval import (
    BM25Retriever,
    SimpleReranker,
    rerank_candidates,
    retrieve_candidates,
)
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


def test_candidate_pipeline_from_precompute_store(tmp_path):
    store = PrecomputeStore(store_dir=tmp_path / "precompute")
    store.put_block(
        PrecomputedBlock(
            block_id="b1",
            source_uri="doc.txt",
            content="Paris is the capital of France.",
            token_count=6,
            fingerprint="fp1",
            representations={"extractive_span": "Paris is capital of France"},
        )
    )

    retrieved = retrieve_candidates(query="capital france", store=store, limit=10)
    reranked = rerank_candidates(query="capital france", candidates=retrieved, limit=5)
    assert reranked
    assert reranked[0].id == "b1"
