# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Two-stage retrieval pipeline with query classification and reranking."""

from __future__ import annotations

from context_portfolio_optimizer.retrieval.lexical import lexical_retrieve
from context_portfolio_optimizer.retrieval.metadata_filters import filter_candidates
from context_portfolio_optimizer.retrieval.query_classifier import classify_query
from context_portfolio_optimizer.retrieval.reranker import rerank_candidates
from context_portfolio_optimizer.types import ContextBlock, SourceType


def retrieve_candidates(
    query: str,
    store: object | None = None,
    blocks: list[ContextBlock] | None = None,
    limit: int = 100,
) -> list[ContextBlock]:
    """Retrieve top lexical candidates after query-aware metadata filtering.

    Accepts either raw `blocks` or a precompute `store` exposing `list_blocks()`.
    """
    source_blocks = blocks or _blocks_from_store(store)
    if not source_blocks:
        return []

    query_class = classify_query(query)
    filtered = filter_candidates(
        source_blocks,
        source_types=query_class.source_types or None,
        min_freshness=query_class.min_freshness,
    )
    stage_limit = min(limit, query_class.preferred_limit)
    return lexical_retrieve(query, filtered or source_blocks, limit=stage_limit)


def run_candidate_pipeline(
    query: str,
    blocks: list[ContextBlock],
    retrieve_limit: int = 100,
    rerank_limit: int = 20,
) -> list[ContextBlock]:
    """Run classify -> retrieve -> rerank flow."""
    candidates = retrieve_candidates(query=query, blocks=blocks, limit=retrieve_limit)
    return rerank_candidates(query=query, candidates=candidates, limit=rerank_limit)


def _blocks_from_store(store: object | None) -> list[ContextBlock]:
    if store is None or not hasattr(store, "list_blocks"):
        return []

    records = store.list_blocks()
    blocks: list[ContextBlock] = []
    for record in records:
        blocks.append(
            ContextBlock(
                id=record.block_id,
                content=record.content,
                source_type=SourceType.RETRIEVAL,
                file_path=record.source_uri,
                token_count=record.token_count,
                metadata={"fingerprint": record.fingerprint},
            )
        )
    return blocks
