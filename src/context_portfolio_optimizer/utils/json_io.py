# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""JSON I/O utilities for ContextFusion."""

import json
from pathlib import Path
from typing import Any


def load_json(path: str | Path) -> Any:
    """Load JSON from file.

    Args:
        path: Path to JSON file

    Returns:
        Parsed JSON data
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path: str | Path, data: Any, indent: int = 2) -> None:
    """Save data to JSON file.

    Args:
        path: Path to output file
        data: Data to save
        indent: Indentation level
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=indent, ensure_ascii=False, default=str)


def load_jsonl(path: str | Path) -> list[dict]:
    """Load JSON Lines file.

    Args:
        path: Path to JSONL file

    Returns:
        List of JSON objects
    """
    path = Path(path)
    records = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                records.append(json.loads(line))
    return records


def save_jsonl(path: str | Path, records: list[dict]) -> None:
    """Save records to JSON Lines file.

    Args:
        path: Path to output file
        records: List of records to save
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        for record in records:
            f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")


def append_jsonl(path: str | Path, record: dict) -> None:
    """Append a record to JSON Lines file.

    Args:
        path: Path to JSONL file
        record: Record to append
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False, default=str) + "\n")
