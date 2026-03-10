# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Pipeline runner for ContextFusion."""

from typing import Any

from ..allocation.portfolio import PortfolioSelector
from ..ingestion.dispatcher import IngestionDispatcher
from ..logging_utils import get_logger, ProgressLogger
from ..normalization.block_builder import BlockBuilder
from ..representations.base_representation import RepresentationGenerator
from ..settings import Settings
from ..types import ContextBlock, PortfolioSelection, RawSegment
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

    def run(
        self,
        file_paths: list[str],
        budget: int | None = None,
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

            # Select portfolio
            progress.log_step("Selecting optimal portfolio")
            portfolio = self.portfolio_selector.select(blocks, budget)

            # Build context
            progress.log_step("Building final context")
            context = self.context_builder.build(portfolio)

        return {
            "context": context,
            "portfolio": portfolio,
            "stats": {
                "files_ingested": len(file_paths),
                "segments_extracted": len(segments),
                "blocks_created": len(blocks),
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
        for path, segments in results.items():
            all_segments.extend(segments)

        # Continue with pipeline
        blocks = self._normalize_segments(all_segments)
        blocks = self._generate_representations(blocks)
        portfolio = self.portfolio_selector.select(blocks, budget)
        context = self.context_builder.build(portfolio)

        return {
            "context": context,
            "portfolio": portfolio,
            "stats": {
                "files_ingested": len(results),
                "segments_extracted": len(all_segments),
                "blocks_created": len(blocks),
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
                from ..utils.tokenization import count_tokens

                block.representation_tokens[rep_type] = count_tokens(content)

        return blocks
