# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Context builder for ContextFusion."""

from typing import Any

from ..logging_utils import get_logger
from ..types import ContextBlock, PortfolioSelection, RepresentationType

logger = get_logger("context_builder")


class ContextBuilder:
    """Builds final prompt context from selected portfolio."""

    def __init__(self):
        self.separator = "\n\n---\n\n"

    def build(
        self,
        portfolio: PortfolioSelection,
        include_headers: bool = True,
    ) -> str:
        """Build context string from portfolio.

        Args:
            portfolio: Selected portfolio
            include_headers: Whether to include source headers

        Returns:
            Context string
        """
        if not portfolio.blocks:
            return ""

        sections = []

        for block in portfolio.blocks:
            # Get the representation to use
            rep_type = portfolio.representations_used.get(block.id, RepresentationType.FULL_TEXT)

            if rep_type in block.representations:
                content = block.representations[rep_type]
            else:
                content = block.content

            # Add header if requested
            if include_headers:
                header = self._build_header(block, rep_type)
                section = f"{header}\n{content}"
            else:
                section = content

            sections.append(section)

        return self.separator.join(sections)

    def build_with_metadata(
        self,
        portfolio: PortfolioSelection,
    ) -> dict[str, Any]:
        """Build context with metadata.

        Args:
            portfolio: Selected portfolio

        Returns:
            Context dictionary with text and metadata
        """
        context_text = self.build(portfolio)

        metadata = {
            "total_tokens": portfolio.total_tokens,
            "expected_utility": portfolio.expected_utility,
            "total_risk": portfolio.total_risk,
            "block_count": len(portfolio.blocks),
            "blocks": [
                {
                    "id": b.id,
                    "source_type": b.source_type.name,
                    "representation": portfolio.representations_used.get(b.id, RepresentationType.FULL_TEXT).value,
                    "tokens": b.token_count,
                }
                for b in portfolio.blocks
            ],
        }

        return {
            "text": context_text,
            "metadata": metadata,
        }

    def _build_header(
        self,
        block: ContextBlock,
        rep_type: RepresentationType,
    ) -> str:
        """Build header for a block.

        Args:
            block: Context block
            rep_type: Representation type

        Returns:
            Header string
        """
        parts = [f"[{block.source_type.name}]"]

        if block.file_path:
            from pathlib import Path
            parts.append(f"Source: {Path(block.file_path).name}")

        if block.page:
            parts.append(f"Page: {block.page}")

        if block.language:
            parts.append(f"Lang: {block.language}")

        parts.append(f"Rep: {rep_type.value}")

        return " | ".join(parts)
