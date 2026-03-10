# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Structured JSON representation for ContextFusion."""

import json

from ..types import ContextBlock, RepresentationType
from .base_representation import BaseRepresentation


class StructuredJsonRepresentation(BaseRepresentation):
    """Structured JSON representation with metadata."""

    @property
    def representation_type(self) -> RepresentationType:
        return RepresentationType.STRUCTURED_JSON

    def generate(self, block: ContextBlock) -> str:
        """Generate structured JSON representation.

        Args:
            block: Context block

        Returns:
            JSON representation
        """
        structure = {
            "id": block.id,
            "source_type": block.source_type.name,
            "content_preview": self._truncate(block.content, 200),
            "metadata": {
                "file_path": block.file_path,
                "page": block.page,
                "row": block.row,
                "language": block.language,
                "token_count": block.token_count,
                "trust_score": round(block.trust_score, 3),
                "freshness": round(block.freshness, 3),
                "tags": block.tags,
            },
        }

        return json.dumps(structure, indent=2)

    def can_generate(self, block: ContextBlock) -> bool:
        """Can always generate JSON."""
        return True

    def _truncate(self, text: str, max_length: int) -> str:
        """Truncate text with ellipsis."""
        if len(text) <= max_length:
            return text
        return text[:max_length - 3] + "..."
