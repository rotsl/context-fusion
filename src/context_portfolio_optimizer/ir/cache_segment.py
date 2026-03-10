# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Cache-aware segment type for packet assembly."""

from dataclasses import dataclass


@dataclass
class CacheSegment:
    """A packet segment that may be stable and cacheable across requests."""

    name: str
    text: str
    stable: bool
    cache_key: str | None = None
    tokens_est: int = 0
