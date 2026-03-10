# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Integration tests for the full pipeline."""

import tempfile
from pathlib import Path

import pytest

from context_portfolio_optimizer.orchestration.runner import PipelineRunner

pytestmark = pytest.mark.integration


class TestPipeline:
    """Integration tests for the full pipeline."""

    def test_run_single_file(self):
        runner = PipelineRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("This is test content for the pipeline.")
            temp_path = f.name

        try:
            result = runner.run([temp_path], budget=500)

            assert "context" in result
            assert "stats" in result
            assert result["stats"]["files_ingested"] == 1
            assert result["stats"]["blocks_created"] > 0
        finally:
            Path(temp_path).unlink()

    def test_run_directory(self):
        runner = PipelineRunner()

        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test files
            (Path(temp_dir) / "file1.txt").write_text("Content 1")
            (Path(temp_dir) / "file2.txt").write_text("Content 2")
            (Path(temp_dir) / "file3.md").write_text("# Markdown\nContent 3")

            result = runner.run_on_directory(temp_dir, budget=1000)

            assert "context" in result
            assert "stats" in result
            assert result["stats"]["files_ingested"] == 3
            assert result["stats"]["blocks_created"] > 0

    def test_context_not_empty(self):
        runner = PipelineRunner()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Important information that should be in context.")
            temp_path = f.name

        try:
            result = runner.run([temp_path], budget=500)

            assert len(result["context"]) > 0
            assert "Important" in result["context"]
        finally:
            Path(temp_path).unlink()
