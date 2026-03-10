# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Table summary representation for ContextFusion."""

import re

from ..types import ContextBlock, RepresentationType
from .base_representation import BaseRepresentation


class TableSummaryRepresentation(BaseRepresentation):
    """Summary representation for table content."""

    @property
    def representation_type(self) -> RepresentationType:
        return RepresentationType.TABLE_SUMMARY

    def generate(self, block: ContextBlock) -> str:
        """Generate table summary representation.

        Args:
            block: Context block

        Returns:
            Table summary
        """
        content = block.content

        # Check if it's actually a table
        if not self._is_table(content):
            return ""

        # Extract table structure
        rows = self._parse_table(content)

        if not rows:
            return ""

        # Generate summary
        summary_parts = []

        # Header info
        if rows:
            summary_parts.append(f"Table with {len(rows)} rows")

        # Column info
        if rows and len(rows[0]) > 0:
            summary_parts.append(f"{len(rows[0])} columns")

        # Column names (if first row looks like headers)
        if rows and len(rows[0]) > 0:
            headers = rows[0]
            summary_parts.append(f"Columns: {', '.join(headers[:5])}")

        # Sample data
        if len(rows) > 1:
            sample_row = rows[1]
            sample = ", ".join(f"{v}" for v in sample_row[:3])
            summary_parts.append(f"Sample: {sample}")

        return " | ".join(summary_parts)

    def can_generate(self, block: ContextBlock) -> bool:
        """Can generate if content looks like a table."""
        return self._is_table(block.content)

    def _is_table(self, content: str) -> bool:
        """Check if content appears to be a table.

        Args:
            content: Content to check

        Returns:
            True if content looks like a table
        """
        # Check for pipe-delimited format
        if "|" in content:
            lines = content.splitlines()
            pipe_lines = sum(1 for line in lines if "|" in line)
            return pipe_lines >= 2

        # Check for CSV-like format
        lines = content.splitlines()
        if len(lines) >= 2:
            first_line_commas = lines[0].count(",")
            if first_line_commas > 0:
                # Check if other lines have similar comma count
                matching = sum(
                    1 for line in lines[1:3] if abs(line.count(",") - first_line_commas) <= 1
                )
                return matching >= 1

        return False

    def _parse_table(self, content: str) -> list[list[str]]:
        """Parse table content into rows.

        Args:
            content: Table content

        Returns:
            List of rows, each row is a list of cells
        """
        rows = []

        # Try pipe-delimited
        if "|" in content:
            for line in content.splitlines():
                if "|" in line:
                    cells = [cell.strip() for cell in line.split("|")]
                    # Remove empty cells from ends
                    while cells and not cells[0]:
                        cells.pop(0)
                    while cells and not cells[-1]:
                        cells.pop()
                    if cells:
                        rows.append(cells)

        # Try CSV
        elif "," in content:
            for line in content.splitlines():
                if "," in line:
                    cells = [cell.strip() for cell in line.split(",")]
                    rows.append(cells)

        return rows
