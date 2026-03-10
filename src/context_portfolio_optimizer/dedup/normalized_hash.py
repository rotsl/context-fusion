# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Normalized text hashing helpers."""

from __future__ import annotations

import re

from .hashing import sha256_text

_PUNCT_RE = re.compile(r"[^\w\s]")
_WS_RE = re.compile(r"\s+")


def normalize_text(text: str) -> str:
    """Normalize punctuation and whitespace for stable hash comparison."""
    lowered = text.lower().strip()
    without_punct = _PUNCT_RE.sub(" ", lowered)
    normalized = _WS_RE.sub(" ", without_punct).strip()
    return normalized


def normalized_text_hash(text: str) -> str:
    """Return normalized text hash."""
    return sha256_text(normalize_text(text))
