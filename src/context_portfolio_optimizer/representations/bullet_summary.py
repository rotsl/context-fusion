# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Bullet summary representation for ContextFusion."""

import re

from ..types import ContextBlock, RepresentationType
from ..utils.text_utils import split_sentences
from .base_representation import BaseRepresentation


class BulletSummaryRepresentation(BaseRepresentation):
    """Bullet point summary representation."""

    @property
    def representation_type(self) -> RepresentationType:
        return RepresentationType.BULLET_SUMMARY

    def generate(self, block: ContextBlock) -> str:
        """Generate bullet summary representation.

        Args:
            block: Context block

        Returns:
            Bullet point summary
        """
        content = block.content

        # If content already has bullet points, use them
        if re.search(r"^\s*[-*+]\s+", content, re.MULTILINE):
            return self._extract_existing_bullets(content)

        # Otherwise, create bullets from sentences
        sentences = split_sentences(content)

        # Filter to key sentences (first, last, and key content)
        key_sentences = self._select_key_sentences(sentences)

        # Format as bullets
        bullets = [f"- {s}" for s in key_sentences]

        return "\n".join(bullets)

    def can_generate(self, block: ContextBlock) -> bool:
        """Can generate if content has multiple sentences."""
        sentences = split_sentences(block.content)
        return len(sentences) >= 2

    def _extract_existing_bullets(self, content: str) -> str:
        """Extract existing bullet points from content."""
        lines = content.splitlines()
        bullets = []

        for line in lines:
            if re.match(r"^\s*[-*+]\s+", line):
                bullets.append(line.strip())

        return "\n".join(bullets)

    def _select_key_sentences(self, sentences: list[str]) -> list[str]:
        """Select key sentences for summary.

        Args:
            sentences: List of sentences

        Returns:
            List of key sentences
        """
        if not sentences:
            return []

        if len(sentences) <= 3:
            return sentences

        # Always include first and last
        selected = [sentences[0]]

        # Add middle sentences if content is substantial
        if len(sentences) > 5:
            # Take every Nth sentence
            step = max(1, len(sentences) // 3)
            for i in range(step, len(sentences) - 1, step):
                selected.append(sentences[i])

        selected.append(sentences[-1])

        return selected
