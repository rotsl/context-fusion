# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Structure detection for content blocks."""

import re
from typing import Any

from ..types import ContextBlock


class StructureDetector:
    """Detects structural patterns in content blocks."""

    HEADING_PATTERN = re.compile(r"^(#{1,6}\s+.+)$", re.MULTILINE)
    LIST_PATTERN = re.compile(r"^\s*[-*+\d]+[.)]?\s+", re.MULTILINE)
    CODE_BLOCK_PATTERN = re.compile(r"```[\s\S]*?```")
    TABLE_PATTERN = re.compile(r"\|.+\|\n\|[-:|\s]+\|\n(\|.+\|\n?)+")
    LINK_PATTERN = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")

    def detect(self, block: ContextBlock) -> dict[str, Any]:
        """Detect structural features in a block.

        Args:
            block: Context block to analyze

        Returns:
            Dictionary of structural features
        """
        text = block.content

        features = {
            "has_headings": bool(self.HEADING_PATTERN.search(text)),
            "heading_count": len(self.HEADING_PATTERN.findall(text)),
            "has_lists": bool(self.LIST_PATTERN.search(text)),
            "list_item_count": len(self.LIST_PATTERN.findall(text)),
            "has_code_blocks": bool(self.CODE_BLOCK_PATTERN.search(text)),
            "code_block_count": len(self.CODE_BLOCK_PATTERN.findall(text)),
            "has_tables": bool(self.TABLE_PATTERN.search(text)),
            "table_count": len(self.TABLE_PATTERN.findall(text)),
            "has_links": bool(self.LINK_PATTERN.search(text)),
            "link_count": len(self.LINK_PATTERN.findall(text)),
            "line_count": len(text.splitlines()),
            "paragraph_count": len([p for p in text.split("\n\n") if p.strip()]),
            "avg_line_length": self._avg_line_length(text),
            "structure_type": self._classify_structure(text),
        }

        return features

    def _avg_line_length(self, text: str) -> float:
        """Compute average line length.

        Args:
            text: Input text

        Returns:
            Average line length
        """
        lines = text.splitlines()
        if not lines:
            return 0.0
        return sum(len(line) for line in lines) / len(lines)

    def _classify_structure(self, text: str) -> str:
        """Classify the structure type of text.

        Args:
            text: Input text

        Returns:
            Structure type classification
        """
        # Check for code
        if self.CODE_BLOCK_PATTERN.search(text):
            code_ratio = len(self.CODE_BLOCK_PATTERN.findall(text)) / max(1, len(text.splitlines()))
            if code_ratio > 0.3:
                return "code"

        # Check for table
        if self.TABLE_PATTERN.search(text):
            return "table"

        # Check for structured document
        if self.HEADING_PATTERN.search(text):
            if self.LIST_PATTERN.search(text):
                return "structured_document"
            return "document_with_headings"

        # Check for list-heavy content
        if self.LIST_PATTERN.search(text):
            list_ratio = len(self.LIST_PATTERN.findall(text)) / max(1, len(text.splitlines()))
            if list_ratio > 0.5:
                return "list"

        # Check for prose
        paragraphs = [p for p in text.split("\n\n") if p.strip()]
        if len(paragraphs) > 3:
            return "prose"

        return "unstructured"

    def extract_sections(self, text: str) -> list[dict[str, Any]]:
        """Extract sections from structured text.

        Args:
            text: Input text

        Returns:
            List of sections with headings and content
        """
        sections = []
        current_heading = ""
        current_content = []

        for line in text.splitlines():
            heading_match = self.HEADING_PATTERN.match(line)
            if heading_match:
                # Save previous section
                if current_content:
                    sections.append(
                        {
                            "heading": current_heading,
                            "content": "\n".join(current_content).strip(),
                        }
                    )
                current_heading = heading_match.group(1).lstrip("# ")
                current_content = []
            else:
                current_content.append(line)

        # Don't forget the last section
        if current_content:
            sections.append(
                {
                    "heading": current_heading,
                    "content": "\n".join(current_content).strip(),
                }
            )

        return sections
