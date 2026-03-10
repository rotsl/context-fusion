# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Text file loader for ContextFusion."""

from ..types import RawSegment
from ..utils.text_utils import split_paragraphs
from .base_loader import BaseLoader


class TextLoader(BaseLoader):
    """Loader for plain text files (.txt, .log)."""

    SUPPORTED_EXTENSIONS = {".txt", ".log"}

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is a text file
        """
        return self._get_extension(file_path) in self.SUPPORTED_EXTENSIONS

    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from a text file.

        Args:
            file_path: Path to the text file

        Returns:
            List of raw segments (one per paragraph)
        """
        text = self._read_text(file_path)
        paragraphs = split_paragraphs(text)

        segments = []
        for i, paragraph in enumerate(paragraphs):
            segment = RawSegment(
                text=paragraph,
                metadata={"paragraph_index": i},
                source_path=file_path,
            )
            segments.append(segment)

        return segments
