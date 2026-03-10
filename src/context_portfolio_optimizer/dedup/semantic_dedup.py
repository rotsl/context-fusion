# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Semantic and deterministic deduplication for context blocks."""

from __future__ import annotations

from dataclasses import replace

from context_portfolio_optimizer.dedup.ast_hash import code_aware_hash, table_signature_hash
from context_portfolio_optimizer.dedup.hashing import sha256_text
from context_portfolio_optimizer.dedup.normalized_hash import normalized_text_hash
from context_portfolio_optimizer.types import ContextBlock


def _token_set(text: str) -> set[str]:
    return {token.lower().strip(".,:;!?()[]{}\"'") for token in text.split() if token.strip()}


def _jaccard_similarity(left: str, right: str) -> float:
    left_set = _token_set(left)
    right_set = _token_set(right)
    if not left_set and not right_set:
        return 1.0
    union = left_set | right_set
    if not union:
        return 0.0
    return len(left_set & right_set) / len(union)


def _is_code_block(block: ContextBlock) -> bool:
    suffix = block.file_path.lower()
    return block.source_type.name == "CODE" or suffix.endswith(
        (".py", ".js", ".ts", ".java", ".go", ".rs", ".cpp", ".c")
    )


def _is_table_like(block: ContextBlock) -> bool:
    suffix = block.file_path.lower()
    return suffix.endswith((".csv", ".tsv", ".json", ".jsonl"))


def _primary_fingerprint(block: ContextBlock) -> str:
    if _is_code_block(block):
        return code_aware_hash(block.content)
    if _is_table_like(block):
        return table_signature_hash(block.content, source_path=block.file_path)
    return normalized_text_hash(block.content)


def deduplicate_blocks(
    blocks: list[ContextBlock],
    semantic_threshold: float = 0.9,
    enable_semantic: bool = True,
) -> list[ContextBlock]:
    """Deduplicate blocks while preserving source provenance.

    The returned block list is stable: representatives keep the first-seen ordering.
    """
    if not blocks:
        return []

    # 1) Exact duplicate collapse by raw hash.
    exact_map: dict[str, ContextBlock] = {}
    order: list[str] = []

    for block in blocks:
        raw_hash = sha256_text(block.content)
        if raw_hash not in exact_map:
            replica = replace(block)
            replica.metadata = dict(block.metadata)
            replica.metadata.setdefault("duplicate_sources", [])
            replica.metadata["raw_hash"] = raw_hash
            replica.metadata["normalized_hash"] = _primary_fingerprint(block)
            exact_map[raw_hash] = replica
            order.append(raw_hash)
            continue

        existing = exact_map[raw_hash]
        duplicate_sources = list(existing.metadata.get("duplicate_sources", []))
        source = block.file_path or block.id
        if source not in duplicate_sources:
            duplicate_sources.append(source)
        existing.metadata["duplicate_sources"] = duplicate_sources

    deduped = [exact_map[key] for key in order]
    if not enable_semantic or len(deduped) <= 1:
        return deduped

    # 2) Near-duplicate collapse by normalized fingerprint + lightweight similarity.
    representatives: list[ContextBlock] = []

    for candidate in deduped:
        candidate_fp = str(
            candidate.metadata.get("normalized_hash") or _primary_fingerprint(candidate)
        )
        merged = False

        for idx, rep in enumerate(representatives):
            rep_fp = str(rep.metadata.get("normalized_hash") or _primary_fingerprint(rep))
            if candidate_fp == rep_fp:
                representatives[idx] = _merge_representative(rep, candidate)
                merged = True
                break

            similarity = _jaccard_similarity(rep.content, candidate.content)
            if similarity >= semantic_threshold:
                representatives[idx] = _merge_representative(rep, candidate)
                merged = True
                break

        if not merged:
            representatives.append(candidate)

    return representatives


def _merge_representative(original: ContextBlock, duplicate: ContextBlock) -> ContextBlock:
    """Merge provenance for a duplicate block cluster."""
    merged = replace(original)
    merged.metadata = dict(original.metadata)

    existing_sources = list(merged.metadata.get("duplicate_sources", []))
    for source in [
        duplicate.file_path or duplicate.id,
        *duplicate.metadata.get("duplicate_sources", []),
    ]:
        if source and source not in existing_sources:
            existing_sources.append(source)

    merged.metadata["duplicate_sources"] = existing_sources

    # Prefer higher trust / freshness representative deterministically.
    if (duplicate.trust_score, duplicate.freshness, -duplicate.token_count) > (
        original.trust_score,
        original.freshness,
        -original.token_count,
    ):
        merged.content = duplicate.content
        merged.token_count = duplicate.token_count
        merged.file_path = duplicate.file_path

    return merged
