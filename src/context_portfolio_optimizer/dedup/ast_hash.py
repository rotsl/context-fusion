# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Code-aware and table-aware hash helpers."""

from __future__ import annotations

import csv
import io
import json
import re
from pathlib import Path

from .hashing import sha256_text
from .normalized_hash import normalize_text

_LINE_COMMENT_RE = re.compile(r"(^\s*#.*?$)|(^\s*//.*?$)", re.MULTILINE)
_BLOCK_COMMENT_RE = re.compile(r"/\*.*?\*/", re.DOTALL)


def code_aware_hash(text: str) -> str:
    """Hash code after stripping comments and normalizing whitespace."""
    no_block = _BLOCK_COMMENT_RE.sub("", text)
    no_line = _LINE_COMMENT_RE.sub("", no_block)
    normalized = normalize_text(no_line)
    return sha256_text(normalized)


def table_signature_hash(text: str, source_path: str = "") -> str:
    """Hash a table-like payload using normalized row signatures."""
    suffix = Path(source_path).suffix.lower()
    rows: list[str] = []

    if suffix in {".csv", ".tsv"}:
        delimiter = "\t" if suffix == ".tsv" else ","
        reader = csv.reader(io.StringIO(text), delimiter=delimiter)
        rows = ["|".join(normalize_text(cell) for cell in row) for row in reader]
    elif suffix in {".json", ".jsonl"}:
        try:
            data = json.loads(text)
            if isinstance(data, list):
                rows = [normalize_text(json.dumps(item, sort_keys=True)) for item in data]
            elif isinstance(data, dict):
                rows = [normalize_text(json.dumps(data, sort_keys=True))]
        except json.JSONDecodeError:
            rows = [normalize_text(line) for line in text.splitlines() if line.strip()]
    else:
        rows = [normalize_text(line) for line in text.splitlines() if line.strip()]

    signature = "\n".join(sorted(row for row in rows if row))
    return sha256_text(signature)
