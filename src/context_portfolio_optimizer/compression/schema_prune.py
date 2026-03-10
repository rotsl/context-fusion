# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Schema pruning helpers for structured payload compression."""

from __future__ import annotations

import json

DEFAULT_FIELD_ALIASES = {
    "answer": "a",
    "citations": "c",
    "confidence": "r",
    "reasoning": "x",
    "metadata": "m",
}


def prune_json_schema(text: str, aliases: dict[str, str] | None = None) -> str:
    """Prune JSON object field names to short aliases."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text

    alias_map = aliases or DEFAULT_FIELD_ALIASES
    if isinstance(payload, dict):
        compact = {alias_map.get(key, key): value for key, value in payload.items()}
        return json.dumps(compact, ensure_ascii=False, separators=(",", ":"))
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
