# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Deterministic hash helpers for deduplication."""

from __future__ import annotations

import hashlib


def sha256_text(text: str) -> str:
    """Return SHA-256 hash for raw text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()
