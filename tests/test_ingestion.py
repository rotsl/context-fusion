# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Tests for ingestion system."""

import tempfile
from pathlib import Path

import pytest

from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.ingestion.text_loader import TextLoader


class TestTextLoader:
    """Tests for TextLoader."""

    def test_supports_txt(self):
        loader = TextLoader()
        assert loader.supports("test.txt")
        assert loader.supports("test.log")
        assert not loader.supports("test.pdf")

    def test_load_txt(self):
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Line 1\n\nLine 2\n\nLine 3")
            temp_path = f.name

        try:
            loader = TextLoader()
            segments = loader.load(temp_path)

            assert len(segments) == 3
            assert segments[0].text == "Line 1"
            assert segments[1].text == "Line 2"
            assert segments[2].text == "Line 3"
        finally:
            Path(temp_path).unlink()


class TestIngestionDispatcher:
    """Tests for IngestionDispatcher."""

    def test_get_loader_for_txt(self):
        dispatcher = IngestionDispatcher()
        with tempfile.NamedTemporaryFile(suffix=".txt", delete=False) as f:
            temp_path = f.name

        try:
            loader = dispatcher.get_loader(temp_path)
            assert loader is not None
            assert isinstance(loader, TextLoader)
        finally:
            Path(temp_path).unlink()

    def test_load_file(self):
        dispatcher = IngestionDispatcher()

        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("Test content")
            temp_path = f.name

        try:
            segments = dispatcher.load_file(temp_path)
            assert len(segments) == 1
            assert segments[0].text == "Test content"
        finally:
            Path(temp_path).unlink()
