# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Ingestion dispatcher for ContextFusion."""

from pathlib import Path

from ..logging_utils import get_logger
from ..types import RawSegment
from .base_loader import BaseLoader
from .code_loader import CodeLoader
from .csv_loader import CSVLoader
from .docx_loader import DocxLoader
from .image_loader import ImageLoader
from .json_loader import JSONLoader
from .markdown_loader import MarkdownLoader
from .pdf_loader import PDFLoader
from .text_loader import TextLoader

logger = get_logger("ingestion_dispatcher")


class IngestionDispatcher:
    """Dispatches file loading to appropriate loaders."""

    def __init__(self):
        self.loaders: list[BaseLoader] = [
            TextLoader(),
            PDFLoader(),
            DocxLoader(),
            CSVLoader(),
            JSONLoader(),
            MarkdownLoader(),
            ImageLoader(),
            CodeLoader(),
        ]

    def register_loader(self, loader: BaseLoader) -> None:
        """Register a new loader.

        Args:
            loader: Loader to register
        """
        self.loaders.append(loader)
        logger.debug(f"Registered loader: {loader.__class__.__name__}")

    def get_loader(self, file_path: str) -> BaseLoader | None:
        """Get the appropriate loader for a file.

        Args:
            file_path: Path to the file

        Returns:
            Loader instance or None if no loader supports the file
        """
        for loader in self.loaders:
            if loader.supports(file_path):
                return loader
        return None

    def load_file(self, file_path: str) -> list[RawSegment]:
        """Load segments from a file.

        Args:
            file_path: Path to the file

        Returns:
            List of raw segments
        """
        file_path = str(file_path)
        path = Path(file_path)

        if not path.exists():
            logger.error(f"File not found: {file_path}")
            return []

        loader = self.get_loader(file_path)

        if loader is None:
            logger.warning(f"No loader found for file: {file_path}")
            # Fallback: try to read as text
            try:
                with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                    text = f.read()
                return [RawSegment(text=text, source_path=file_path)]
            except Exception as e:
                logger.error(f"Fallback text loading failed: {e}")
                return []

        logger.debug(f"Loading {file_path} with {loader.__class__.__name__}")

        try:
            segments = loader.load(file_path)
            logger.debug(f"Loaded {len(segments)} segments from {file_path}")
            return segments
        except Exception as e:
            logger.error(f"Error loading {file_path}: {e}")
            return []

    def load_directory(
        self,
        directory: str,
        pattern: str = "*",
        recursive: bool = True,
    ) -> dict[str, list[RawSegment]]:
        """Load segments from all files in a directory.

        Args:
            directory: Path to directory
            pattern: Glob pattern for files
            recursive: Whether to search recursively

        Returns:
            Dictionary mapping file paths to segments
        """
        directory = Path(directory)
        results: dict[str, list[RawSegment]] = {}

        if recursive:
            files = list(directory.rglob(pattern))
        else:
            files = list(directory.glob(pattern))

        # Filter to files only
        files = [f for f in files if f.is_file()]

        logger.info(f"Found {len(files)} files in {directory}")

        for file_path in files:
            segments = self.load_file(str(file_path))
            if segments:
                results[str(file_path)] = segments

        return results

    def supports(self, file_path: str) -> bool:
        """Check if any loader supports the file.

        Args:
            file_path: Path to the file

        Returns:
            True if a loader is available
        """
        return self.get_loader(file_path) is not None
