# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for precompute pipeline."""

from pathlib import Path

from context_portfolio_optimizer.precompute import PrecomputeRunner, PrecomputeStore


def test_precompute_stores_entries(tmp_path: Path):
    data_dir = tmp_path / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    (data_dir / "one.txt").write_text("Alpha context block", encoding="utf-8")

    store = PrecomputeStore(store_dir=tmp_path / "precompute")
    runner = PrecomputeRunner(store=store)

    stats = runner.run_on_directory(str(data_dir))
    assert stats["files_processed"] == 1
    assert stats["entries_stored"] >= 1

    entries = store.list_blocks()
    assert entries
    assert store.get_fingerprint(entries[0].block_id)
