# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Full text representation for ContextFusion."""

from ..types import ContextBlock, RepresentationType
from .base_representation import BaseRepresentation


class FullTextRepresentation(BaseRepresentation):
    """Full text representation - the original content unchanged."""

    @property
    def representation_type(self) -> RepresentationType:
        return RepresentationType.FULL_TEXT

    def generate(self, block: ContextBlock) -> str:
        """Generate full text representation.

        Args:
            block: Context block

        Returns:
            Full content of the block
        """
        return block.content

    def can_generate(self, block: ContextBlock) -> bool:
        """Always can generate full text."""
        return bool(block.content)
