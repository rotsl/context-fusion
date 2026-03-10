# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""File-backed precompute store for low-latency query-time access."""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class PrecomputedBlock:
    """Serialized precompute record per block."""

    block_id: str
    source_uri: str
    content: str
    token_count: int
    fingerprint: str
    representations: dict[str, str] = field(default_factory=dict)
    retrieval_features: dict[str, Any] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)


class PrecomputeStore:
    """JSONL-backed store with deterministic ID indexing."""

    def __init__(self, store_dir: str | Path = ".cpo_cache/precompute"):
        self.store_dir = Path(store_dir)
        self.store_dir.mkdir(parents=True, exist_ok=True)
        self.store_file = self.store_dir / "blocks.jsonl"
        self._index: dict[str, PrecomputedBlock] | None = None

    def put_block(self, block: PrecomputedBlock) -> None:
        """Persist or update a precomputed block record."""
        records = self._load_all()
        records[block.block_id] = block
        with open(self.store_file, "w", encoding="utf-8") as file:
            for block_id in sorted(records):
                file.write(json.dumps(asdict(records[block_id]), ensure_ascii=False) + "\n")
        self._index = records

    def get_block(self, block_id: str) -> PrecomputedBlock | None:
        """Fetch a precomputed block by ID."""
        return self._load_all().get(block_id)

    def get_representations(self, block_id: str) -> dict[str, str]:
        """Return precomputed representation variants for a block."""
        block = self.get_block(block_id)
        if block is None:
            return {}
        return dict(block.representations)

    def get_fingerprint(self, block_id: str) -> str | None:
        """Return fingerprint for a block."""
        block = self.get_block(block_id)
        if block is None:
            return None
        return block.fingerprint

    def list_blocks(self) -> list[PrecomputedBlock]:
        """List all precomputed blocks in deterministic order."""
        records = self._load_all()
        return [records[block_id] for block_id in sorted(records)]

    def inspect(self) -> dict[str, Any]:
        """Return summary stats for CLI inspection."""
        records = self._load_all()
        return {
            "entries": len(records),
            "store_file": str(self.store_file),
            "bytes": self.store_file.stat().st_size if self.store_file.exists() else 0,
        }

    def _load_all(self) -> dict[str, PrecomputedBlock]:
        if self._index is not None:
            return dict(self._index)

        records: dict[str, PrecomputedBlock] = {}
        if self.store_file.exists():
            with open(self.store_file, encoding="utf-8") as file:
                for line in file:
                    line = line.strip()
                    if not line:
                        continue
                    payload = json.loads(line)
                    record = PrecomputedBlock(**payload)
                    records[record.block_id] = record

        self._index = records
        return dict(records)
