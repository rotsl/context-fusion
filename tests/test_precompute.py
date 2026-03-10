# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for precompute pipeline."""

from pathlib import Path

from context_portfolio_optimizer.memory.store import MemoryStore
from context_portfolio_optimizer.precompute.runner import PrecomputeRunner


def test_precompute_stores_entries(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "one.txt").write_text("Alpha context block", encoding="utf-8")

    store = MemoryStore(memory_dir=tmp_path / "memory")
    runner = PrecomputeRunner(memory_store=store)

    stats = runner.run_on_directory(str(data_dir))
    assert stats["files_processed"] == 1
    assert stats["entries_stored"] >= 1

    entries = store.search(entry_type="precompute", limit=10)
    assert entries
