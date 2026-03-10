# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Extracted facts representation for ContextFusion."""

import re

from ..types import ContextBlock, RepresentationType
from .base_representation import BaseRepresentation


class ExtractedFactsRepresentation(BaseRepresentation):
    """Extract key facts from content."""

    @property
    def representation_type(self) -> RepresentationType:
        return RepresentationType.EXTRACTED_FACTS

    # Patterns that often indicate facts
    FACT_PATTERNS = [
        r"is\s+(?:a|an|the)\s+([^\.]+)",
        r"has\s+([^\.]+)",
        r"contains\s+([^\.]+)",
        r"supports?\s+([^\.]+)",
        r"requires?\s+([^\.]+)",
        r"returns?\s+([^\.]+)",
        r"(?:value|value is)\s+[:=]?\s*([^\.\n]+)",
        r"(?:default|default is)\s+[:=]?\s*([^\.\n]+)",
    ]

    def generate(self, block: ContextBlock) -> str:
        """Generate extracted facts representation.

        Args:
            block: Context block

        Returns:
            Extracted facts as bullet points
        """
        content = block.content
        facts = []

        # Extract facts using patterns
        for pattern in self.FACT_PATTERNS:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                fact = match.group(1).strip()
                if fact and len(fact) > 5:
                    facts.append(fact)

        # Extract definitions
        definitions = self._extract_definitions(content)
        facts.extend(definitions)

        # Remove duplicates while preserving order
        seen = set()
        unique_facts = []
        for fact in facts:
            if fact.lower() not in seen:
                seen.add(fact.lower())
                unique_facts.append(fact)

        if not unique_facts:
            return ""

        # Format as bullets
        return "\n".join(f"• {fact}" for fact in unique_facts[:10])

    def can_generate(self, block: ContextBlock) -> bool:
        """Can generate if content is substantial."""
        return len(block.content) > 50

    def _extract_definitions(self, content: str) -> list[str]:
        """Extract definition-like statements.

        Args:
            content: Input content

        Returns:
            List of definitions
        """
        definitions = []

        # Pattern: "X is Y" or "X: Y"
        def_patterns = [
            r"([A-Z][a-zA-Z\s]+)\s+is\s+(?:defined as|a|an|the)\s+([^\.]+)",
            r"([A-Z][a-zA-Z\s]+):\s*([^\.\n]+)",
        ]

        for pattern in def_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                term = match.group(1).strip()
                definition = match.group(2).strip()
                if term and definition:
                    definitions.append(f"{term}: {definition}")

        return definitions
