# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""JSON minification helpers."""

from __future__ import annotations

import json


def minify_json_text(text: str) -> str:
    """Minify a JSON text payload if possible, else return unchanged text."""
    try:
        payload = json.loads(text)
    except json.JSONDecodeError:
        return text
    return json.dumps(payload, ensure_ascii=False, separators=(",", ":"))
