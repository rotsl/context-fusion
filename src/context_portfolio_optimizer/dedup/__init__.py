# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Deduplication and fingerprint utilities."""

from .ast_hash import code_aware_hash, table_signature_hash
from .hashing import sha256_text
from .normalized_hash import normalize_text, normalized_text_hash
from .semantic_dedup import deduplicate_blocks

__all__ = [
    "code_aware_hash",
    "deduplicate_blocks",
    "normalize_text",
    "normalized_text_hash",
    "sha256_text",
    "table_signature_hash",
]
