# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for ContextPacket output from pipeline runner."""

from pathlib import Path

from context_portfolio_optimizer import PipelineRunner


def test_pipeline_returns_context_packet(tmp_path: Path):
    sample_file = tmp_path / "sample.txt"
    sample_file.write_text("ContextFusion packet test content.", encoding="utf-8")

    runner = PipelineRunner()
    result = runner.run([str(sample_file)], budget=300)

    assert "context_packet" in result
    packet = result["context_packet"]
    assert packet.task_type == "retrieval"
    assert isinstance(packet.selected_blocks, list)
    if packet.selected_blocks:
        assert packet.selected_blocks[0].block_id
        assert packet.selected_blocks[0].tokens_est >= 0
