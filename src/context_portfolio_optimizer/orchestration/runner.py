# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Pipeline runner for ContextFusion."""

from __future__ import annotations

from typing import Any

from context_portfolio_optimizer.allocation import (
    BudgetPlanner,
    PlannerWeights,
    RepresentationCandidate,
)
from context_portfolio_optimizer.allocation.portfolio import PortfolioSelector
from context_portfolio_optimizer.caching import build_cache_segments
from context_portfolio_optimizer.dedup import deduplicate_blocks, normalized_text_hash
from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.ir import ContextPacket, SelectedBlock
from context_portfolio_optimizer.ir.fingerprints import block_fingerprint
from context_portfolio_optimizer.logging_utils import ProgressLogger
from context_portfolio_optimizer.normalization.block_builder import BlockBuilder
from context_portfolio_optimizer.precompute import PrecomputeStore
from context_portfolio_optimizer.representations.base_representation import RepresentationGenerator
from context_portfolio_optimizer.representations.registry import RepresentationRegistry
from context_portfolio_optimizer.retrieval import classify_query, run_candidate_pipeline
from context_portfolio_optimizer.types import (
    ContextBlock,
    PortfolioSelection,
    RawSegment,
    RepresentationType,
)
from context_portfolio_optimizer.utils.tokenization import count_tokens

from .context_builder import ContextBuilder


class PipelineRunner:
    """Runs the full context optimization pipeline."""

    def __init__(
        self,
        dispatcher: IngestionDispatcher | None = None,
        block_builder: BlockBuilder | None = None,
        representation_generator: RepresentationGenerator | None = None,
        representation_registry: RepresentationRegistry | None = None,
        portfolio_selector: PortfolioSelector | None = None,
        context_builder: ContextBuilder | None = None,
        precompute_store: PrecomputeStore | None = None,
        planner_weights: PlannerWeights | None = None,
    ):
        self.dispatcher = dispatcher or IngestionDispatcher()
        self.block_builder = block_builder or BlockBuilder()
        self.rep_generator = representation_generator or RepresentationGenerator()
        self.rep_registry = representation_registry or RepresentationRegistry()
        self.portfolio_selector = portfolio_selector or PortfolioSelector()
        self.context_builder = context_builder or ContextBuilder()
        self.precompute_store = precompute_store or PrecomputeStore()
        self.budget_planner = BudgetPlanner(weights=planner_weights)

    def run(
        self,
        file_paths: list[str],
        budget: int | None = None,
        task: str = "context_optimization",
        task_type: str = "retrieval",
        query: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        precomputed_only: bool = False,
    ) -> dict[str, Any]:
        """Run full pipeline on explicit file paths."""
        with ProgressLogger("Context optimization pipeline") as progress:
            progress.log_step("Ingesting files")
            segments = self._ingest_files(file_paths)

            progress.log_step("Normalizing to blocks")
            blocks = self._normalize_segments(segments)

            return self._execute_on_blocks(
                blocks=blocks,
                budget=budget,
                task=task,
                task_type=task_type,
                query=query,
                provider=provider,
                model=model,
                precomputed_only=precomputed_only,
                file_count=len(file_paths),
                segment_count=len(segments),
            )

    def run_on_directory(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = True,
        budget: int | None = None,
        task: str = "context_optimization",
        task_type: str = "retrieval",
        query: str | None = None,
        provider: str | None = None,
        model: str | None = None,
        precomputed_only: bool = False,
    ) -> dict[str, Any]:
        """Run pipeline on a directory path."""
        results = self.dispatcher.load_directory(directory, pattern=pattern, recursive=recursive)

        all_segments: list[RawSegment] = []
        for segments in results.values():
            all_segments.extend(segments)

        blocks = self._normalize_segments(all_segments)

        return self._execute_on_blocks(
            blocks=blocks,
            budget=budget,
            task=task,
            task_type=task_type,
            query=query,
            provider=provider,
            model=model,
            precomputed_only=precomputed_only,
            file_count=len(results),
            segment_count=len(all_segments),
        )

    def _execute_on_blocks(
        self,
        *,
        blocks: list[ContextBlock],
        budget: int | None,
        task: str,
        task_type: str,
        query: str | None,
        provider: str | None,
        model: str | None,
        precomputed_only: bool,
        file_count: int,
        segment_count: int,
    ) -> dict[str, Any]:
        blocks = deduplicate_blocks(blocks, enable_semantic=True)
        blocks = self._hydrate_or_generate_representations(blocks, task_type, precomputed_only)

        candidate_blocks = blocks
        effective_task_type = task_type
        if query:
            query_class = classify_query(query)
            effective_task_type = query_class.task_type
            retrieved = run_candidate_pipeline(
                query=query,
                blocks=blocks,
                retrieve_limit=100,
                rerank_limit=25,
            )
            if retrieved:
                candidate_blocks = retrieved

        utility_scores = self.portfolio_selector.utility_model.score_blocks(
            candidate_blocks,
            self.portfolio_selector.feature_extractor,
        )
        risk_scores = self.portfolio_selector.risk_model.score_blocks(
            candidate_blocks,
            self.portfolio_selector.feature_extractor,
        )

        retrieval_budget = budget
        if retrieval_budget is None:
            retrieval_budget = self.portfolio_selector.budget_manager.get_available_for_category(
                "retrieval"
            )

        candidates = self._build_representation_candidates(
            candidate_blocks,
            task_type=effective_task_type,
            utility_scores=utility_scores,
            risk_scores=risk_scores,
        )

        planner_selection = self.budget_planner.plan(candidates, retrieval_budget)
        if planner_selection.selected:
            portfolio, selected_texts, selected_lookup = self._portfolio_from_planner(
                blocks=candidate_blocks,
                selection=planner_selection,
            )
            context = "\n\n---\n\n".join(selected_texts)
        else:
            portfolio = self.portfolio_selector.select(candidate_blocks, retrieval_budget)
            context = self.context_builder.build(portfolio)
            selected_lookup = {}

        context_packet = self._build_context_packet(
            task=task,
            task_type=effective_task_type,
            budget=retrieval_budget,
            portfolio=portfolio,
            file_count=file_count,
            utility_scores=utility_scores,
            risk_scores=risk_scores,
            selected_lookup=selected_lookup,
            provider=provider,
            model=model,
        )

        return {
            "context": context,
            "context_packet": context_packet,
            "portfolio": portfolio,
            "stats": {
                "files_ingested": file_count,
                "segments_extracted": segment_count,
                "blocks_created": len(blocks),
                "blocks_retrieved": len(candidate_blocks),
                "blocks_selected": len(portfolio.blocks),
                "total_tokens": portfolio.total_tokens,
                "expected_utility": portfolio.expected_utility,
            },
        }

    def _ingest_files(self, file_paths: list[str]) -> list[RawSegment]:
        all_segments: list[RawSegment] = []
        for path in file_paths:
            all_segments.extend(self.dispatcher.load_file(path))
        return all_segments

    def _normalize_segments(self, segments: list[RawSegment]) -> list[ContextBlock]:
        return self.block_builder.build_blocks(segments)

    def _hydrate_or_generate_representations(
        self,
        blocks: list[ContextBlock],
        task_type: str,
        precomputed_only: bool,
    ) -> list[ContextBlock]:
        for block in blocks:
            precomputed = self.precompute_store.get_block(block.id)
            if precomputed is not None:
                block.metadata["fingerprint"] = precomputed.fingerprint
                for pre_rep_type, content in precomputed.representations.items():
                    try:
                        enum_type = RepresentationType(pre_rep_type)
                    except ValueError:
                        continue
                    block.representations[enum_type] = content
                    block.representation_tokens[enum_type] = count_tokens(content)

            if precomputed_only and block.representations:
                continue

            generated = self.rep_generator.generate_for_block(block)
            for generated_rep_type, content in generated.items():
                block.representations[generated_rep_type] = content
                block.representation_tokens[generated_rep_type] = count_tokens(content)

            variants = self.rep_registry.generate_all(block, task_type=task_type)
            block.metadata["compact_variants"] = [
                {
                    "type": variant.representation_type,
                    "text": variant.text,
                    "tokens": variant.token_estimate,
                    "generation_cost": variant.generation_cost,
                    "fidelity": variant.fidelity_score,
                }
                for variant in variants
            ]

            block.metadata.setdefault("fingerprint", normalized_text_hash(block.content))

        return blocks

    def _build_representation_candidates(
        self,
        blocks: list[ContextBlock],
        task_type: str,
        utility_scores: dict[str, float],
        risk_scores: dict[str, float],
    ) -> list[RepresentationCandidate]:
        source_counts: dict[str, int] = {}
        for block in blocks:
            key = block.source_type.name.lower()
            source_counts[key] = source_counts.get(key, 0) + 1

        candidates: list[RepresentationCandidate] = []
        for block in blocks:
            utility = utility_scores.get(block.id, 0.0)
            risk = risk_scores.get(block.id, 0.0)
            source_key = block.source_type.name.lower()
            diversity = 1.0 / max(1, source_counts.get(source_key, 1))
            fingerprint = str(block.metadata.get("fingerprint", "")) or None

            for rep_type, content in block.representations.items():
                tokens = block.representation_tokens.get(rep_type, block.token_count)
                candidates.append(
                    RepresentationCandidate(
                        parent_block_id=block.id,
                        representation_type=rep_type.value,
                        text=content,
                        tokens=tokens,
                        utility=utility,
                        risk=risk,
                        cacheable=block.privacy_score < 0.5,
                        diversity=diversity,
                        generation_cost=0.05,
                        fingerprint=fingerprint,
                    )
                )

            for variant in block.metadata.get("compact_variants", []):
                candidates.append(
                    RepresentationCandidate(
                        parent_block_id=block.id,
                        representation_type=str(variant.get("type", "compact")),
                        text=str(variant.get("text", "")),
                        tokens=int(variant.get("tokens", block.token_count)),
                        utility=utility,
                        risk=risk,
                        cacheable=block.privacy_score < 0.5,
                        diversity=diversity,
                        generation_cost=float(variant.get("generation_cost", 0.1)),
                        fingerprint=fingerprint,
                    )
                )

            # Full text fallback candidate
            candidates.append(
                RepresentationCandidate(
                    parent_block_id=block.id,
                    representation_type="full_text",
                    text=block.content,
                    tokens=block.token_count,
                    utility=utility,
                    risk=risk,
                    cacheable=block.privacy_score < 0.5,
                    diversity=diversity,
                    generation_cost=0.0,
                    fingerprint=fingerprint,
                )
            )

        return candidates

    def _portfolio_from_planner(
        self,
        *,
        blocks: list[ContextBlock],
        selection,
    ) -> tuple[PortfolioSelection, list[str], dict[str, RepresentationCandidate]]:
        block_by_id = {block.id: block for block in blocks}

        selected_blocks: list[ContextBlock] = []
        representations_used: dict[str, RepresentationType] = {}
        selected_texts: list[str] = []
        selected_lookup: dict[str, RepresentationCandidate] = {}
        total_risk = 0.0

        for candidate in selection.selected:
            block = block_by_id.get(candidate.parent_block_id)
            if block is None:
                continue

            selected_blocks.append(block)
            selected_lookup[block.id] = candidate
            selected_texts.append(candidate.text)
            total_risk += candidate.risk

            rep_type_value = candidate.representation_type
            try:
                rep_type = RepresentationType(rep_type_value)
            except ValueError:
                rep_type = RepresentationType.FULL_TEXT
                block.representations[RepresentationType.FULL_TEXT] = candidate.text
                block.representation_tokens[RepresentationType.FULL_TEXT] = candidate.tokens

            representations_used[block.id] = rep_type

        portfolio = PortfolioSelection(
            blocks=selected_blocks,
            representations_used=representations_used,
            total_tokens=selection.total_tokens,
            expected_utility=selection.objective_score,
            total_risk=total_risk,
        )

        return portfolio, selected_texts, selected_lookup

    def _build_context_packet(
        self,
        *,
        task: str,
        task_type: str,
        budget: int,
        portfolio: PortfolioSelection,
        file_count: int,
        utility_scores: dict[str, float],
        risk_scores: dict[str, float],
        selected_lookup: dict[str, RepresentationCandidate],
        provider: str | None,
        model: str | None,
    ) -> ContextPacket:
        selected_blocks: list[SelectedBlock] = []
        citations: list[str] = []

        for block in portfolio.blocks:
            selected_candidate = selected_lookup.get(block.id)
            if selected_candidate is not None:
                rep_type = selected_candidate.representation_type
                text = selected_candidate.text
                tokens_est = selected_candidate.tokens
            else:
                rep_enum = portfolio.representations_used.get(
                    block.id, RepresentationType.FULL_TEXT
                )
                rep_type = rep_enum.value
                text = block.representations.get(rep_enum, block.content)
                tokens_est = block.representation_tokens.get(rep_enum, block.token_count)

            source_uri = block.file_path or f"block:{block.id}"
            if source_uri not in citations:
                citations.append(source_uri)

            selected = SelectedBlock(
                block_id=block.id,
                source_uri=source_uri,
                modality=block.source_type.name.lower(),
                representation_type=rep_type,
                text=text,
                tokens_est=tokens_est,
                score=utility_scores.get(block.id, 0.0) - risk_scores.get(block.id, 0.0),
                utility=utility_scores.get(block.id, 0.0),
                risk=risk_scores.get(block.id, 0.0),
                freshness=block.freshness,
                trust=block.trust_score,
                cacheable=block.privacy_score < 0.5,
                fingerprint=str(block.metadata.get("fingerprint") or normalized_text_hash(text)),
                parent_block_id=block.id,
            )
            selected.fingerprint = selected.fingerprint or block_fingerprint(selected)
            selected_blocks.append(selected)

        packet = ContextPacket(
            task=task,
            task_type=task_type,
            constraints={"file_count": file_count, "retrieval_budget": budget},
            selected_blocks=selected_blocks,
            citations=citations,
            budget={"retrieval": budget, "selected_tokens": portfolio.total_tokens},
            output_contract=None,
            provider_hint=provider,
            model_hint=model,
        )
        packet.cache_segments = build_cache_segments(packet)
        return packet
