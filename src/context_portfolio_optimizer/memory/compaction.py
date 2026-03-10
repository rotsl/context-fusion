# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Memory compaction for ContextFusion."""

from datetime import datetime, timedelta
from typing import Any

from ..utils.similarity import text_similarity
from .store import MemoryStore


class MemoryCompactor:
    """Compacts memory by removing duplicates and old entries."""

    def __init__(self, store: MemoryStore | None = None):
        """Initialize memory compactor.

        Args:
            store: Memory store to compact
        """
        self.store = store or MemoryStore()

    def compact(
        self,
        similarity_threshold: float = 0.9,
        max_age_days: int | None = None,
    ) -> dict[str, Any]:
        """Compact memory store.

        Args:
            similarity_threshold: Threshold for considering entries duplicates
            max_age_days: Maximum age for entries (None for no limit)

        Returns:
            Statistics about compaction
        """
        entries = self.store.get_all()

        if not entries:
            return {"removed": 0, "kept": 0, "reason": "empty_store"}

        # Filter by age
        if max_age_days is not None:
            cutoff = datetime.utcnow() - timedelta(days=max_age_days)
            entries = [
                e for e in entries
                if self._parse_timestamp(e.get("timestamp", "")) > cutoff
            ]

        # Remove duplicates based on similarity
        unique_entries = self._remove_duplicates(entries, similarity_threshold)

        # Compact the store
        removed = self.store.compact(unique_entries)

        return {
            "removed": removed,
            "kept": len(unique_entries),
            "original": len(self.store.get_all()) + removed,
        }

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse timestamp string.

        Args:
            timestamp: ISO format timestamp

        Returns:
            Datetime object
        """
        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime.utcnow()

    def _remove_duplicates(
        self,
        entries: list[dict[str, Any]],
        threshold: float,
    ) -> list[dict[str, Any]]:
        """Remove duplicate entries based on content similarity.

        Args:
            entries: List of entries
            threshold: Similarity threshold

        Returns:
            List of unique entries
        """
        if not entries:
            return []

        # Sort by timestamp (newest first)
        sorted_entries = sorted(
            entries,
            key=lambda e: e.get("timestamp", ""),
            reverse=True,
        )

        unique = []

        for entry in sorted_entries:
            content = entry.get("content", "")
            is_duplicate = False

            for kept in unique:
                kept_content = kept.get("content", "")
                similarity = text_similarity(content, kept_content)

                if similarity >= threshold:
                    is_duplicate = True
                    break

            if not is_duplicate:
                unique.append(entry)

        return unique

    def merge_similar(
        self,
        similarity_threshold: float = 0.8,
    ) -> list[dict[str, Any]]:
        """Merge similar entries into combined entries.

        Args:
            similarity_threshold: Threshold for merging

        Returns:
            List of merged entries
        """
        entries = self.store.get_all()

        if not entries:
            return []

        # Group similar entries
        groups: list[list[dict[str, Any]]] = []

        for entry in entries:
            content = entry.get("content", "")
            added = False

            for group in groups:
                group_content = group[0].get("content", "")
                similarity = text_similarity(content, group_content)

                if similarity >= similarity_threshold:
                    group.append(entry)
                    added = True
                    break

            if not added:
                groups.append([entry])

        # Merge each group
        merged = []
        for group in groups:
            if len(group) == 1:
                merged.append(group[0])
            else:
                merged_entry = self._merge_group(group)
                merged.append(merged_entry)

        return merged

    def _merge_group(self, entries: list[dict[str, Any]]) -> dict[str, Any]:
        """Merge a group of similar entries.

        Args:
            entries: Group of entries to merge

        Returns:
            Merged entry
        """
        # Use the newest entry as base
        base = max(entries, key=lambda e: e.get("timestamp", ""))

        # Combine content
        contents = [e.get("content", "") for e in entries]
        combined_content = "\n\n".join(contents)

        merged = {
            "id": base.get("id"),
            "timestamp": base.get("timestamp"),
            "type": base.get("type"),
            "content": combined_content,
            "metadata": {
                **base.get("metadata", {}),
                "merged_from": [e.get("id") for e in entries if e != base],
                "merge_count": len(entries),
            },
        }

        return merged
