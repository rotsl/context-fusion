# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Memory store for ContextFusion."""

import json
from datetime import datetime
from pathlib import Path
from typing import Any

from ..logging_utils import get_logger
from ..settings import get_settings
from ..utils.hashing import compute_id

logger = get_logger("memory_store")


class MemoryStore:
    """JSONL-based memory store for context entries."""

    def __init__(self, memory_dir: str | Path | None = None):
        """Initialize memory store.

        Args:
            memory_dir: Directory for memory files
        """
        if memory_dir is None:
            settings = get_settings()
            memory_dir = settings.memory_path

        self.memory_dir = Path(memory_dir)
        self.memory_dir.mkdir(parents=True, exist_ok=True)

        self.memory_file = self.memory_dir / "memory.jsonl"

    def append(
        self,
        content: str,
        metadata: dict[str, Any] | None = None,
        entry_type: str = "general",
    ) -> str:
        """Append an entry to memory.

        Args:
            content: Content to store
            metadata: Optional metadata
            entry_type: Type of memory entry

        Returns:
            Entry ID
        """
        entry_id = compute_id(content, prefix="mem")

        entry = {
            "id": entry_id,
            "timestamp": datetime.utcnow().isoformat(),
            "type": entry_type,
            "content": content,
            "metadata": metadata or {},
        }

        # Append to file
        with open(self.memory_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        logger.debug(f"Appended memory entry: {entry_id}")

        return entry_id

    def search(
        self,
        query: str | None = None,
        entry_type: str | None = None,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search memory entries.

        Args:
            query: Optional text query
            entry_type: Optional entry type filter
            limit: Maximum results

        Returns:
            List of matching entries
        """
        if not self.memory_file.exists():
            return []

        results = []

        with open(self.memory_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)

                    # Filter by type
                    if entry_type and entry.get("type") != entry_type:
                        continue

                    # Filter by query
                    if query:
                        query_lower = query.lower()
                        content = entry.get("content", "").lower()
                        if query_lower not in content:
                            continue

                    results.append(entry)

                    if len(results) >= limit:
                        break

                except json.JSONDecodeError:
                    continue

        return results

    def get_all(self) -> list[dict[str, Any]]:
        """Get all memory entries.

        Returns:
            List of all entries
        """
        if not self.memory_file.exists():
            return []

        entries = []

        with open(self.memory_file, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue

                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue

        return entries

    def get_by_id(self, entry_id: str) -> dict[str, Any] | None:
        """Get a specific entry by ID.

        Args:
            entry_id: Entry ID

        Returns:
            Entry or None if not found
        """
        for entry in self.get_all():
            if entry.get("id") == entry_id:
                return entry
        return None

    def clear(self) -> None:
        """Clear all memory entries."""
        if self.memory_file.exists():
            self.memory_file.unlink()
        logger.info("Memory store cleared")

    def compact(self, keep_entries: list[dict[str, Any]]) -> int:
        """Compact memory by keeping only specified entries.

        Args:
            keep_entries: Entries to keep

        Returns:
            Number of entries removed
        """
        if not self.memory_file.exists():
            return 0

        keep_ids = {e.get("id") for e in keep_entries}

        # Read all entries
        all_entries = self.get_all()

        # Filter to keep only specified entries
        new_entries = [e for e in all_entries if e.get("id") in keep_ids]

        # Write back
        with open(self.memory_file, "w", encoding="utf-8") as f:
            for entry in new_entries:
                f.write(json.dumps(entry, ensure_ascii=False) + "\n")

        removed = len(all_entries) - len(new_entries)
        logger.info(f"Compacted memory: removed {removed} entries")

        return removed

    def get_stats(self) -> dict[str, Any]:
        """Get memory statistics.

        Returns:
            Statistics dictionary
        """
        entries = self.get_all()

        if not entries:
            return {
                "total_entries": 0,
                "total_size_bytes": 0,
                "types": {},
            }

        # Count by type
        types: dict[str, int] = {}
        for entry in entries:
            entry_type = entry.get("type", "unknown")
            types[entry_type] = types.get(entry_type, 0) + 1

        # Get file size
        size_bytes = self.memory_file.stat().st_size if self.memory_file.exists() else 0

        return {
            "total_entries": len(entries),
            "total_size_bytes": size_bytes,
            "types": types,
        }
