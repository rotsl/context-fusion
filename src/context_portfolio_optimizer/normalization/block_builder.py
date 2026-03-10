# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Block builder for normalizing raw segments to context blocks."""

from datetime import datetime
from pathlib import Path
from typing import Any

from ..constants import (
    DOCUMENT_EXTENSIONS,
    IMAGE_EXTENSIONS,
    STRUCTURED_EXTENSIONS,
    TEXT_EXTENSIONS,
)
from ..logging_utils import get_logger
from ..types import ContextBlock, RawSegment, RepresentationType, SourceType
from ..utils.hashing import compute_id
from ..utils.tokenization import count_tokens
from .metadata_extractor import MetadataExtractor

logger = get_logger("block_builder")


class BlockBuilder:
    """Builds ContextBlocks from RawSegments."""

    def __init__(self):
        self.metadata_extractor = MetadataExtractor()

    def build_block(
        self,
        segment: RawSegment,
        source_type: SourceType | None = None,
    ) -> ContextBlock:
        """Build a ContextBlock from a RawSegment.

        Args:
            segment: Raw segment to convert
            source_type: Optional source type override

        Returns:
            ContextBlock
        """
        # Detect source type if not provided
        if source_type is None:
            source_type = self._detect_source_type(segment.source_path)

        # Compute ID
        block_id = compute_id(
            f"{segment.source_path}:{segment.page_number}:{segment.row_number}:{segment.text[:100]}",
            prefix="blk",
        )

        # Count tokens
        token_count = count_tokens(segment.text)

        # Extract metadata
        metadata = self.metadata_extractor.extract(segment)

        # Build block
        block = ContextBlock(
            id=block_id,
            content=segment.text,
            source_type=source_type,
            file_path=segment.source_path,
            page=segment.page_number,
            row=segment.row_number,
            language=segment.language,
            token_count=token_count,
            trust_score=metadata.get("trust_score", 0.5),
            freshness=metadata.get("freshness", 1.0),
            retrieval_score=metadata.get("retrieval_score", 0.0),
            privacy_score=metadata.get("privacy_score", 0.0),
            tags=metadata.get("tags", []),
            timestamp=datetime.utcnow(),
            metadata=segment.metadata,
        )

        return block

    def build_blocks(
        self,
        segments: list[RawSegment],
        source_type: SourceType | None = None,
    ) -> list[ContextBlock]:
        """Build multiple ContextBlocks from RawSegments.

        Args:
            segments: List of raw segments
            source_type: Optional source type override

        Returns:
            List of ContextBlocks
        """
        blocks = []
        for segment in segments:
            try:
                block = self.build_block(segment, source_type)
                blocks.append(block)
            except Exception as e:
                logger.error(f"Error building block: {e}")

        return blocks

    def _detect_source_type(self, file_path: str) -> SourceType:
        """Detect source type from file path.

        Args:
            file_path: Path to the file

        Returns:
            Detected source type
        """
        ext = Path(file_path).suffix.lower()

        if ext in TEXT_EXTENSIONS:
            return SourceType.TEXT
        elif ext in DOCUMENT_EXTENSIONS:
            return SourceType.DOCUMENT
        elif ext in STRUCTURED_EXTENSIONS:
            return SourceType.STRUCTURED
        elif ext in IMAGE_EXTENSIONS:
            return SourceType.IMAGE
        else:
            # Check if it's code
            from ..constants import CODE_EXTENSIONS
            if ext in CODE_EXTENSIONS:
                return SourceType.CODE
            return SourceType.TEXT  # Default

    def add_representations(
        self,
        block: ContextBlock,
        representations: dict[RepresentationType, str],
    ) -> ContextBlock:
        """Add alternative representations to a block.

        Args:
            block: Block to update
            representations: Dictionary of representation type to content

        Returns:
            Updated block
        """
        for rep_type, content in representations.items():
            block.representations[rep_type] = content
            block.representation_tokens[rep_type] = count_tokens(content)

        return block

    def merge_blocks(
        self,
        blocks: list[ContextBlock],
        max_tokens: int = 500,
    ) -> list[ContextBlock]:
        """Merge small blocks to reduce fragmentation.

        Args:
            blocks: List of blocks to merge
            max_tokens: Maximum tokens per merged block

        Returns:
            List of merged blocks
        """
        if not blocks:
            return []

        merged = []
        current_content = []
        current_tokens = 0
        current_metadata: dict[str, Any] = {
            "source_paths": [],
            "pages": [],
        }

        for block in blocks:
            if current_tokens + block.token_count > max_tokens and current_content:
                # Save current merged block
                merged_text = "\n\n".join(current_content)
                merged_block = ContextBlock(
                    id=compute_id(merged_text, prefix="merged"),
                    content=merged_text,
                    source_type=blocks[0].source_type,
                    file_path=blocks[0].file_path,
                    token_count=count_tokens(merged_text),
                    metadata=current_metadata,
                )
                merged.append(merged_block)

                # Reset
                current_content = []
                current_tokens = 0
                current_metadata = {"source_paths": [], "pages": []}

            current_content.append(block.content)
            current_tokens += block.token_count
            current_metadata["source_paths"].append(block.file_path)
            if block.page:
                current_metadata["pages"].append(block.page)

        # Don't forget the last group
        if current_content:
            merged_text = "\n\n".join(current_content)
            merged_block = ContextBlock(
                id=compute_id(merged_text, prefix="merged"),
                content=merged_text,
                source_type=blocks[0].source_type,
                file_path=blocks[0].file_path,
                token_count=count_tokens(merged_text),
                metadata=current_metadata,
            )
            merged.append(merged_block)

        return merged
