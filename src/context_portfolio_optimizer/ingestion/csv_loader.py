# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""CSV/TSV file loader for ContextFusion."""

import pandas as pd

from ..types import RawSegment
from .base_loader import BaseLoader


class CSVLoader(BaseLoader):
    """Loader for CSV and TSV files."""

    SUPPORTED_EXTENSIONS = {".csv", ".tsv"}

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is CSV or TSV
        """
        return self._get_extension(file_path) in self.SUPPORTED_EXTENSIONS

    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from a CSV/TSV file.

        Args:
            file_path: Path to the CSV/TSV file

        Returns:
            List of raw segments (one per row, plus table summary)
        """
        ext = self._get_extension(file_path)
        separator = "\t" if ext == ".tsv" else ","

        segments = []

        try:
            df = pd.read_csv(file_path, sep=separator)

            # Create table summary segment
            summary = f"Table with {len(df)} rows and {len(df.columns)} columns. "
            summary += f"Columns: {', '.join(df.columns)}"

            segments.append(RawSegment(
                text=summary,
                metadata={
                    "is_summary": True,
                    "row_count": len(df),
                    "column_count": len(df.columns),
                    "columns": list(df.columns),
                },
                source_path=file_path,
            ))

            # Create segment for each row
            for idx, row in df.iterrows():
                row_text = " ".join([f"{col}={val}" for col, val in row.items()])
                segment = RawSegment(
                    text=row_text,
                    metadata={"row_index": idx},
                    source_path=file_path,
                    row_number=int(idx) if hasattr(idx, "__int__") else idx,
                )
                segments.append(segment)

        except Exception as e:
            # Fallback: read as text
            text = self._read_text(file_path)
            segments.append(RawSegment(
                text=text,
                source_path=file_path,
                metadata={"parse_error": str(e)},
            ))

        return segments
