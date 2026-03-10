# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Retention policy for memory management."""

from datetime import datetime, timedelta
from typing import Any

from .store import MemoryStore


class RetentionPolicy:
    """Defines retention rules for memory entries."""

    def __init__(
        self,
        max_entries: int | None = None,
        max_age_days: int | None = 90,
        max_size_mb: float | None = None,
    ):
        """Initialize retention policy.

        Args:
            max_entries: Maximum number of entries to keep
            max_age_days: Maximum age of entries in days
            max_size_mb: Maximum size of memory file in MB
        """
        self.max_entries = max_entries
        self.max_age_days = max_age_days
        self.max_size_mb = max_size_mb

    def apply(self, store: MemoryStore) -> dict[str, Any]:
        """Apply retention policy to memory store.

        Args:
            store: Memory store

        Returns:
            Statistics about applied policy
        """
        entries = store.get_all()
        original_count = len(entries)

        if original_count == 0:
            return {"removed": 0, "kept": 0}

        # Apply age filter
        if self.max_age_days is not None:
            cutoff = datetime.utcnow() - timedelta(days=self.max_age_days)
            entries = [
                e for e in entries
                if self._parse_timestamp(e.get("timestamp", "")) > cutoff
            ]

        # Sort by importance (for now, just by recency)
        entries.sort(
            key=lambda e: e.get("timestamp", ""),
            reverse=True,
        )

        # Apply entry limit
        if self.max_entries is not None and len(entries) > self.max_entries:
            entries = entries[:self.max_entries]

        # Compact store
        store.compact(entries)

        return {
            "removed": original_count - len(entries),
            "kept": len(entries),
            "original": original_count,
        }

    def _parse_timestamp(self, timestamp: str) -> datetime:
        """Parse timestamp string."""
        try:
            return datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
        except (ValueError, AttributeError):
            return datetime.utcnow()

    def should_retain(self, entry: dict[str, Any]) -> bool:
        """Check if an entry should be retained.

        Args:
            entry: Memory entry

        Returns:
            True if entry should be retained
        """
        # Check age
        if self.max_age_days is not None:
            timestamp = entry.get("timestamp", "")
            entry_date = self._parse_timestamp(timestamp)
            cutoff = datetime.utcnow() - timedelta(days=self.max_age_days)
            if entry_date < cutoff:
                return False

        return True
