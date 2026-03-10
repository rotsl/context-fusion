# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Markdown file loader for ContextFusion."""

import re

from ..types import RawSegment
from .base_loader import BaseLoader


class MarkdownLoader(BaseLoader):
    """Loader for Markdown files."""

    SUPPORTED_EXTENSIONS = {".md", ".markdown", ".mdown", ".mkd"}

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is Markdown
        """
        return self._get_extension(file_path) in self.SUPPORTED_EXTENSIONS

    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from a Markdown file.

        Segments are created for each section (delimited by headings).

        Args:
            file_path: Path to the Markdown file

        Returns:
            List of raw segments
        """
        text = self._read_text(file_path)
        segments = []

        # Split by headings
        heading_pattern = r"^(#{1,6}\s+.+)$"
        parts = re.split(heading_pattern, text, flags=re.MULTILINE)

        current_heading = ""
        current_content = []

        for part in parts:
            if re.match(heading_pattern, part.strip()):
                # Save previous section
                if current_content:
                    content = "\n".join(current_content).strip()
                    if content:
                        segments.append(
                            RawSegment(
                                text=f"{current_heading}\n{content}"
                                if current_heading
                                else content,
                                metadata={"heading": current_heading},
                                source_path=file_path,
                            )
                        )
                current_heading = part.strip()
                current_content = []
            else:
                current_content.append(part)

        # Don't forget the last section
        if current_content:
            content = "\n".join(current_content).strip()
            if content:
                segments.append(
                    RawSegment(
                        text=f"{current_heading}\n{content}" if current_heading else content,
                        metadata={"heading": current_heading},
                        source_path=file_path,
                    )
                )

        # If no segments were created, treat entire file as one segment
        if not segments and text.strip():
            segments.append(
                RawSegment(
                    text=text.strip(),
                    source_path=file_path,
                )
            )

        return segments
