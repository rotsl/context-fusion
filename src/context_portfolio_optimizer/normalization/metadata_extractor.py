# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Metadata extraction for context blocks."""

import re
from datetime import datetime
from pathlib import Path
from typing import Any

from ..constants import SECONDS_PER_DAY
from ..types import RawSegment


class MetadataExtractor:
    """Extracts metadata from raw segments."""

    # Patterns that might indicate sensitive content
    PRIVACY_PATTERNS = [
        r"\b\d{3}-\d{2}-\d{4}\b",  # SSN
        r"\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b",  # Credit card
        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",  # Email
        r"password\s*[=:]\s*\S+",  # Password
        r"api[_-]?key\s*[=:]\s*\S+",  # API key
        r"secret\s*[=:]\s*\S+",  # Secret
        r"token\s*[=:]\s*\S+",  # Token
    ]

    # Patterns that indicate high-quality content
    QUALITY_INDICATORS = [
        r"^#{1,6}\s+",  # Markdown headings
        r"```",  # Code blocks
        r"\|.+\|",  # Tables
        r"\[.+\]\(.+\)",  # Links
        r"^\s*[-*+]\s+",  # Lists
    ]

    def extract(self, segment: RawSegment) -> dict[str, Any]:
        """Extract metadata from a segment.

        Args:
            segment: Raw segment

        Returns:
            Dictionary of metadata
        """
        metadata: dict[str, Any] = {}

        # Trust score based on structure
        metadata["trust_score"] = self._compute_trust_score(segment)

        # Freshness (default to now if not specified)
        metadata["freshness"] = self._compute_freshness(segment)

        # Retrieval score (placeholder for actual retrieval)
        metadata["retrieval_score"] = segment.metadata.get("retrieval_score", 0.0)

        # Privacy risk
        metadata["privacy_score"] = self._compute_privacy_score(segment)

        # Structure score
        metadata["structure_score"] = self._compute_structure_score(segment)

        # Tags
        metadata["tags"] = self._extract_tags(segment)

        return metadata

    def _compute_trust_score(self, segment: RawSegment) -> float:
        """Compute trust score for a segment.

        Args:
            segment: Raw segment

        Returns:
            Trust score between 0 and 1
        """
        score = 0.5  # Default neutral score

        # Boost for structured content
        if segment.metadata.get("is_heading"):
            score += 0.1
        if segment.metadata.get("is_table"):
            score += 0.1

        # Boost for code with docstrings
        if segment.metadata.get("type") == "function":
            score += 0.15
        if segment.metadata.get("type") == "class":
            score += 0.15

        # Penalty for very short content
        if len(segment.text) < 50:
            score -= 0.1

        return max(0.0, min(1.0, score))

    def _compute_freshness(self, segment: RawSegment) -> float:
        """Compute freshness score for a segment.

        Args:
            segment: Raw segment

        Returns:
            Freshness score between 0 and 1
        """
        # Check if timestamp is in metadata
        timestamp = segment.metadata.get("timestamp")
        if timestamp is None:
            return 1.0  # Assume fresh if no timestamp

        try:
            if isinstance(timestamp, (int, float)):
                # Assume Unix timestamp
                age_seconds = datetime.utcnow().timestamp() - timestamp
            elif isinstance(timestamp, str):
                # Try to parse
                dt = datetime.fromisoformat(timestamp.replace("Z", "+00:00"))
                age_seconds = (datetime.utcnow() - dt.replace(tzinfo=None)).total_seconds()
            elif isinstance(timestamp, datetime):
                age_seconds = (datetime.utcnow() - timestamp).total_seconds()
            else:
                return 1.0

            # Compute freshness with exponential decay
            age_days = age_seconds / SECONDS_PER_DAY
            freshness = 2 ** (-age_days / 30)  # Half-life of 30 days

            return max(0.0, min(1.0, freshness))
        except Exception:
            return 1.0

    def _compute_privacy_score(self, segment: RawSegment) -> float:
        """Compute privacy risk score for a segment.

        Args:
            segment: Raw segment

        Returns:
            Privacy risk score between 0 and 1
        """
        text = segment.text
        risk_count = 0

        for pattern in self.PRIVACY_PATTERNS:
            if re.search(pattern, text, re.IGNORECASE):
                risk_count += 1

        # Normalize to 0-1 range
        return min(1.0, risk_count / 3)

    def _compute_structure_score(self, segment: RawSegment) -> float:
        """Compute structure quality score.

        Args:
            segment: Raw segment

        Returns:
            Structure score between 0 and 1
        """
        text = segment.text
        score = 0.0

        for pattern in self.QUALITY_INDICATORS:
            if re.search(pattern, text, re.MULTILINE):
                score += 0.2

        return min(1.0, score)

    def _extract_tags(self, segment: RawSegment) -> list[str]:
        """Extract tags from segment.

        Args:
            segment: Raw segment

        Returns:
            List of tags
        """
        tags = []

        # Add type-based tags
        if segment.metadata.get("is_heading"):
            tags.append("heading")
        if segment.metadata.get("is_table"):
            tags.append("table")
        if segment.metadata.get("type"):
            tags.append(segment.metadata["type"])

        # Add language tag
        if segment.language:
            tags.append(f"lang:{segment.language}")

        # Add source-based tags
        ext = Path(segment.source_path).suffix.lower()
        if ext:
            tags.append(f"ext:{ext[1:]}")

        return list(set(tags))  # Remove duplicates
