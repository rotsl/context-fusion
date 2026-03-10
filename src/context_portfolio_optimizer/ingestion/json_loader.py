# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""JSON file loader for ContextFusion."""

import json
from typing import Any

from ..types import RawSegment
from .base_loader import BaseLoader


class JSONLoader(BaseLoader):
    """Loader for JSON and JSONL files."""

    SUPPORTED_EXTENSIONS = {".json", ".jsonl"}

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is JSON
        """
        return self._get_extension(file_path) in self.SUPPORTED_EXTENSIONS

    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from a JSON file.

        Args:
            file_path: Path to the JSON file

        Returns:
            List of raw segments
        """
        ext = self._get_extension(file_path)

        if ext == ".jsonl":
            return self._load_jsonl(file_path)
        else:
            return self._load_json(file_path)

    def _load_json(self, file_path: str) -> list[RawSegment]:
        """Load a standard JSON file."""
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        segments = []
        flattened = self._flatten_json(data)

        for key, value in flattened.items():
            segment = RawSegment(
                text=f"{key}={value}",
                metadata={"key": key, "value": value},
                source_path=file_path,
            )
            segments.append(segment)

        # Also add full JSON as a segment
        segments.append(RawSegment(
            text=json.dumps(data, indent=2),
            metadata={"is_full_json": True},
            source_path=file_path,
        ))

        return segments

    def _load_jsonl(self, file_path: str) -> list[RawSegment]:
        """Load a JSON Lines file."""
        segments = []

        with open(file_path, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue

                try:
                    data = json.loads(line)
                    flattened = self._flatten_json(data)

                    for key, value in flattened.items():
                        segment = RawSegment(
                            text=f"{key}={value}",
                            metadata={
                                "line_number": line_num,
                                "key": key,
                                "value": value,
                            },
                            source_path=file_path,
                            row_number=line_num,
                        )
                        segments.append(segment)
                except json.JSONDecodeError:
                    continue

        return segments

    def _flatten_json(
        self,
        data: Any,
        parent_key: str = "",
        sep: str = ".",
    ) -> dict[str, Any]:
        """Flatten nested JSON structure.

        Args:
            data: JSON data
            parent_key: Parent key for recursion
            sep: Separator for nested keys

        Returns:
            Flattened dictionary
        """
        items: dict[str, Any] = {}

        if isinstance(data, dict):
            for key, value in data.items():
                new_key = f"{parent_key}{sep}{key}" if parent_key else key
                items.update(self._flatten_json(value, new_key, sep))
        elif isinstance(data, list):
            for i, value in enumerate(data):
                new_key = f"{parent_key}{sep}[{i}]" if parent_key else f"[{i}]"
                items.update(self._flatten_json(value, new_key, sep))
        else:
            items[parent_key] = data

        return items
