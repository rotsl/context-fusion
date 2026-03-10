# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Cache key generation helpers."""

from __future__ import annotations

import hashlib


def stable_cache_key(name: str, text: str) -> str:
    """Build deterministic cache key from segment identity and text."""
    digest = hashlib.sha256(f"{name}::{text}".encode()).hexdigest()
    return f"seg:{digest}"
