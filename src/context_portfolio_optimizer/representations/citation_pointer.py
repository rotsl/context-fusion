# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Citation pointer representation for ContextFusion."""

from pathlib import Path

from ..types import ContextBlock, RepresentationType
from .base_representation import BaseRepresentation


class CitationPointerRepresentation(BaseRepresentation):
    """Compact citation pointer representation."""

    @property
    def representation_type(self) -> RepresentationType:
        return RepresentationType.CITATION_POINTER

    def generate(self, block: ContextBlock) -> str:
        """Generate citation pointer representation.

        Args:
            block: Context block

        Returns:
            Compact citation pointer
        """
        parts = []

        # Source file
        if block.file_path:
            filename = Path(block.file_path).name
            parts.append(filename)

        # Page/row reference
        if block.page is not None:
            parts.append(f"p.{block.page}")
        elif block.row is not None:
            parts.append(f"row {block.row}")

        # Content preview
        preview = self._create_preview(block.content)
        if preview:
            parts.append(f'"{preview}"')

        # ID reference
        parts.append(f"[{block.id[:8]}]")

        return " | ".join(parts)

    def can_generate(self, block: ContextBlock) -> bool:
        """Can always generate citation pointer."""
        return bool(block.file_path or block.content)

    def _create_preview(self, content: str, max_length: int = 50) -> str:
        """Create a short preview of content.

        Args:
            content: Full content
            max_length: Maximum preview length

        Returns:
            Preview string
        """
        # Take first line or sentence
        first_line = content.split("\n")[0].strip()

        if len(first_line) <= max_length:
            return first_line

        # Truncate at word boundary
        truncated = first_line[:max_length - 3]
        last_space = truncated.rfind(" ")
        if last_space > max_length // 2:
            truncated = truncated[:last_space]

        return truncated + "..."
