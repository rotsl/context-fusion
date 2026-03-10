# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Pipeline runner for ContextFusion."""

from typing import Any

from context_portfolio_optimizer.allocation.portfolio import PortfolioSelector
from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.ir import ContextPacket, SelectedBlock
from context_portfolio_optimizer.logging_utils import ProgressLogger, get_logger
from context_portfolio_optimizer.normalization.block_builder import BlockBuilder
from context_portfolio_optimizer.representations.base_representation import (
    RepresentationGenerator,
)
from context_portfolio_optimizer.retrieval import BM25Retriever, SimpleReranker
from context_portfolio_optimizer.settings import Settings
from context_portfolio_optimizer.types import (
    ContextBlock,
    PortfolioSelection,
    RawSegment,
    RepresentationType,
)
from context_portfolio_optimizer.utils.tokenization import count_tokens

from .context_builder import ContextBuilder

logger = get_logger("pipeline")


class PipelineRunner:
    """Runs the full context optimization pipeline."""

    def __init__(
        self,
        settings: Settings | None = None,
        dispatcher: IngestionDispatcher | None = None,
        block_builder: BlockBuilder | None = None,
        representation_generator: RepresentationGenerator | None = None,
        portfolio_selector: PortfolioSelector | None = None,
        context_builder: ContextBuilder | None = None,
    ):
        """Initialize pipeline runner.

        Args:
            settings: Settings
            dispatcher: Ingestion dispatcher
            block_builder: Block builder
            representation_generator: Representation generator
            portfolio_selector: Portfolio selector
            context_builder: Context builder
        """
        self.settings = settings
        self.dispatcher = dispatcher or IngestionDispatcher()
        self.block_builder = block_builder or BlockBuilder()
        self.rep_generator = representation_generator or RepresentationGenerator()
        self.portfolio_selector = portfolio_selector or PortfolioSelector()
        self.context_builder = context_builder or ContextBuilder()
        self.retriever = BM25Retriever()
        self.reranker = SimpleReranker()

    def run(
        self,
        file_paths: list[str],
        budget: int | None = None,
        task: str = "context_optimization",
        task_type: str = "retrieval",
        query: str | None = None,
    ) -> dict[str, Any]:
        """Run full pipeline.

        Args:
            file_paths: List of file paths to ingest
            budget: Optional token budget override

        Returns:
            Pipeline results
        """
        with ProgressLogger("Context optimization pipeline") as progress:
            # Ingest
            progress.log_step("Ingesting files")
            segments = self._ingest_files(file_paths)

            # Normalize
            progress.log_step("Normalizing to blocks")
            blocks = self._normalize_segments(segments)

            # Generate representations
            progress.log_step("Generating representations")
            blocks = self._generate_representations(blocks)

            # Optional two-stage retrieval prior to knapsack optimization
            candidate_blocks = blocks
            if query:
                progress.log_step("Two-stage retrieval (BM25 + rerank)")
                stage1 = self.retriever.retrieve(query=query, blocks=blocks, top_k=100)
                stage2 = self.reranker.rerank(query=query, blocks=stage1, top_k=20)
                if stage2:
                    candidate_blocks = stage2

            # Select portfolio
            progress.log_step("Selecting optimal portfolio")
            portfolio = self.portfolio_selector.select(candidate_blocks, budget)

            # Build context
            progress.log_step("Building final context")
            context = self.context_builder.build(portfolio)
            context_packet = self._build_context_packet(
                task=task,
                task_type=task_type,
                budget=budget,
                portfolio=portfolio,
                file_count=len(file_paths),
            )

        return {
            "context": context,
            "context_packet": context_packet,
            "portfolio": portfolio,
            "stats": {
                "files_ingested": len(file_paths),
                "segments_extracted": len(segments),
                "blocks_created": len(blocks),
                "blocks_retrieved": len(candidate_blocks),
                "blocks_selected": len(portfolio.blocks),
                "total_tokens": portfolio.total_tokens,
                "expected_utility": portfolio.expected_utility,
            },
        }

    def run_on_directory(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = True,
        budget: int | None = None,
        task: str = "context_optimization",
        task_type: str = "retrieval",
        query: str | None = None,
    ) -> dict[str, Any]:
        """Run pipeline on directory.

        Args:
            directory: Directory path
            pattern: File pattern
            recursive: Search recursively
            budget: Optional token budget

        Returns:
            Pipeline results
        """
        results = self.dispatcher.load_directory(directory, pattern, recursive)

        # Flatten segments
        all_segments: list[RawSegment] = []
        for segments in results.values():
            all_segments.extend(segments)

        # Continue with pipeline
        blocks = self._normalize_segments(all_segments)
        blocks = self._generate_representations(blocks)
        candidate_blocks = blocks
        if query:
            stage1 = self.retriever.retrieve(query=query, blocks=blocks, top_k=100)
            stage2 = self.reranker.rerank(query=query, blocks=stage1, top_k=20)
            if stage2:
                candidate_blocks = stage2
        portfolio = self.portfolio_selector.select(candidate_blocks, budget)
        context = self.context_builder.build(portfolio)
        context_packet = self._build_context_packet(
            task=task,
            task_type=task_type,
            budget=budget,
            portfolio=portfolio,
            file_count=len(results),
        )

        return {
            "context": context,
            "context_packet": context_packet,
            "portfolio": portfolio,
            "stats": {
                "files_ingested": len(results),
                "segments_extracted": len(all_segments),
                "blocks_created": len(blocks),
                "blocks_retrieved": len(candidate_blocks),
                "blocks_selected": len(portfolio.blocks),
                "total_tokens": portfolio.total_tokens,
            },
        }

    def _ingest_files(self, file_paths: list[str]) -> list[RawSegment]:
        """Ingest files and extract segments."""
        all_segments: list[RawSegment] = []

        for path in file_paths:
            segments = self.dispatcher.load_file(path)
            all_segments.extend(segments)

        return all_segments

    def _normalize_segments(self, segments: list[RawSegment]) -> list[ContextBlock]:
        """Normalize segments to blocks."""
        return self.block_builder.build_blocks(segments)

    def _generate_representations(self, blocks: list[ContextBlock]) -> list[ContextBlock]:
        """Generate alternative representations for blocks."""
        for block in blocks:
            representations = self.rep_generator.generate_for_block(block)
            for rep_type, content in representations.items():
                block.representations[rep_type] = content
                block.representation_tokens[rep_type] = count_tokens(content)

        return blocks

    def _build_context_packet(
        self,
        task: str,
        task_type: str,
        budget: int | None,
        portfolio: PortfolioSelection,
        file_count: int,
    ) -> ContextPacket:
        """Build canonical context packet from portfolio selection."""
        retrieval_budget = budget
        if retrieval_budget is None:
            retrieval_budget = self.portfolio_selector.budget_manager.get_available_for_category(
                "retrieval"
            )

        selected_blocks: list[SelectedBlock] = []
        citations: list[str] = []
        cache_segments: list[str] = []

        for block in portfolio.blocks:
            rep_type = portfolio.representations_used.get(block.id, RepresentationType.FULL_TEXT)
            text = block.representations.get(rep_type, block.content)
            tokens_est = block.representation_tokens.get(rep_type, block.token_count)

            source_uri = block.file_path or f"block:{block.id}"
            if source_uri not in citations:
                citations.append(source_uri)

            cache_segments.append(block.id)

            selected_blocks.append(
                SelectedBlock(
                    block_id=block.id,
                    source_uri=source_uri,
                    modality=block.source_type.name.lower(),
                    representation_type=rep_type.value,
                    text=text,
                    tokens_est=tokens_est,
                    score=(block.trust_score + block.freshness) / 2,
                    freshness=block.freshness,
                    trust=block.trust_score,
                    cacheable=block.privacy_score < 0.5,
                )
            )

        return ContextPacket(
            task=task,
            task_type=task_type,
            constraints={
                "file_count": file_count,
                "retrieval_budget": retrieval_budget,
            },
            selected_blocks=selected_blocks,
            citations=citations,
            budget={
                "retrieval": retrieval_budget,
                "selected_tokens": portfolio.total_tokens,
            },
            cache_segments=cache_segments,
            output_contract=None,
        )
