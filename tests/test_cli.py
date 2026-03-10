# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Tests for CLI."""

import tempfile
from pathlib import Path

from typer.testing import CliRunner

from context_portfolio_optimizer.cli import app

runner = CliRunner()


class TestCLI:
    """Tests for CLI commands."""

    def test_version(self):
        result = runner.invoke(app, ["version"])
        assert result.exit_code == 0
        assert "ContextFusion" in result.output

    def test_ingest_file(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            result = runner.invoke(app, ["ingest", temp_path])
            assert result.exit_code == 0
            assert "blocks" in result.output.lower() or "Extracted" in result.output
        finally:
            Path(temp_path).unlink()

    def test_plan(self):
        result = runner.invoke(app, ["plan", "Summarize documents"])
        assert result.exit_code == 0
        assert "Execution Plan" in result.output
        assert "Budget Allocation" in result.output

    def test_memory_stats_empty(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            result = runner.invoke(app, ["memory-stats", "--config", f"{temp_dir}/nonexistent.yaml"])
            # Should not crash even with no memory
            assert result.exit_code == 0
