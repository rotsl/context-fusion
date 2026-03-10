# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Base representation class for ContextFusion."""

from abc import ABC, abstractmethod

from ..types import ContextBlock, RepresentationType


class BaseRepresentation(ABC):
    """Abstract base class for content representations."""

    @property
    @abstractmethod
    def representation_type(self) -> RepresentationType:
        """Return the type of this representation."""
        pass

    @abstractmethod
    def generate(self, block: ContextBlock) -> str:
        """Generate representation for a block.

        Args:
            block: Context block to represent

        Returns:
            Representation as string
        """
        pass

    def can_generate(self, block: ContextBlock) -> bool:
        """Check if this representation can be generated for the block.

        Args:
            block: Context block to check

        Returns:
            True if representation can be generated
        """
        return True


class RepresentationGenerator:
    """Generates multiple representations for context blocks."""

    def __init__(self):
        self.representations: list[BaseRepresentation] = []
        self._register_default_representations()

    def _register_default_representations(self) -> None:
        """Register default representation generators."""
        from .bullet_summary import BulletSummaryRepresentation
        from .citation_pointer import CitationPointerRepresentation
        from .code_signature_summary import CodeSignatureRepresentation
        from .extracted_facts import ExtractedFactsRepresentation
        from .full_text import FullTextRepresentation
        from .structured_json import StructuredJsonRepresentation
        from .table_summary import TableSummaryRepresentation

        self.register(FullTextRepresentation())
        self.register(BulletSummaryRepresentation())
        self.register(StructuredJsonRepresentation())
        self.register(ExtractedFactsRepresentation())
        self.register(CitationPointerRepresentation())
        self.register(TableSummaryRepresentation())
        self.register(CodeSignatureRepresentation())

    def register(self, representation: BaseRepresentation) -> None:
        """Register a representation generator.

        Args:
            representation: Representation to register
        """
        self.representations.append(representation)

    def generate_for_block(
        self,
        block: ContextBlock,
        types: list[RepresentationType] | None = None,
    ) -> dict[RepresentationType, str]:
        """Generate representations for a block.

        Args:
            block: Context block
            types: Optional list of representation types to generate

        Returns:
            Dictionary of representation type to content
        """
        results: dict[RepresentationType, str] = {}

        for rep in self.representations:
            if types is not None and rep.representation_type not in types:
                continue

            if rep.can_generate(block):
                try:
                    content = rep.generate(block)
                    if content:
                        results[rep.representation_type] = content
                except Exception:
                    # Skip representations that fail
                    pass

        return results

    def generate_for_blocks(
        self,
        blocks: list[ContextBlock],
        types: list[RepresentationType] | None = None,
    ) -> dict[str, dict[RepresentationType, str]]:
        """Generate representations for multiple blocks.

        Args:
            blocks: List of context blocks
            types: Optional list of representation types to generate

        Returns:
            Dictionary mapping block IDs to representations
        """
        results: dict[str, dict[RepresentationType, str]] = {}

        for block in blocks:
            block_reps = self.generate_for_block(block, types)
            if block_reps:
                results[block.id] = block_reps

        return results
