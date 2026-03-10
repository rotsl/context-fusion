# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Base loader class for ContextFusion."""

from abc import ABC, abstractmethod
from pathlib import Path

from ..types import RawSegment


class BaseLoader(ABC):
    """Abstract base class for file loaders."""

    @abstractmethod
    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if this loader can handle the file
        """
        pass

    @abstractmethod
    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from the file.

        Args:
            file_path: Path to the file

        Returns:
            List of raw segments
        """
        pass

    def _get_extension(self, file_path: str) -> str:
        """Get file extension in lowercase.

        Args:
            file_path: Path to the file

        Returns:
            Lowercase file extension
        """
        return Path(file_path).suffix.lower()

    def _read_text(self, file_path: str, encoding: str = "utf-8") -> str:
        """Read text from file.

        Args:
            file_path: Path to the file
            encoding: File encoding

        Returns:
            File contents as text
        """
        with open(file_path, "r", encoding=encoding, errors="replace") as f:
            return f.read()
