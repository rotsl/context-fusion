# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Simple local packet cache for repeated chat/agent turns."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any


class PacketCache:
    """JSON-backed packet cache keyed by packet hash."""

    def __init__(self, cache_dir: str | Path = ".cpo_cache/packets"):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

    def put(self, packet_hash: str, payload: dict[str, Any]) -> None:
        """Store payload by packet hash."""
        cache_file = self.cache_dir / f"{packet_hash}.json"
        with open(cache_file, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2, default=str)

    def get(self, packet_hash: str) -> dict[str, Any] | None:
        """Load payload by packet hash."""
        cache_file = self.cache_dir / f"{packet_hash}.json"
        if not cache_file.exists():
            return None
        with open(cache_file, encoding="utf-8") as file:
            return json.load(file)

    def inspect(self) -> dict[str, Any]:
        """Return cache stats for CLI inspection."""
        files = sorted(self.cache_dir.glob("*.json"))
        total_bytes = sum(file.stat().st_size for file in files)
        return {
            "entries": len(files),
            "bytes": total_bytes,
            "cache_dir": str(self.cache_dir),
        }
