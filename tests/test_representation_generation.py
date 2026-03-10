# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Tests for representation generation."""

from context_portfolio_optimizer.representations.base_representation import (
    RepresentationGenerator,
)
from context_portfolio_optimizer.representations.bullet_summary import (
    BulletSummaryRepresentation,
)
from context_portfolio_optimizer.representations.citation_pointer import (
    CitationPointerRepresentation,
)
from context_portfolio_optimizer.representations.full_text import FullTextRepresentation
from context_portfolio_optimizer.types import ContextBlock, RepresentationType, SourceType


class TestFullTextRepresentation:
    """Tests for FullTextRepresentation."""

    def test_generate(self):
        rep = FullTextRepresentation()
        block = ContextBlock(
            id="test",
            content="Hello world",
            source_type=SourceType.TEXT,
        )

        result = rep.generate(block)
        assert result == "Hello world"

    def test_representation_type(self):
        rep = FullTextRepresentation()
        assert rep.representation_type == RepresentationType.FULL_TEXT


class TestBulletSummaryRepresentation:
    """Tests for BulletSummaryRepresentation."""

    def test_generate(self):
        rep = BulletSummaryRepresentation()
        block = ContextBlock(
            id="test",
            content="First sentence. Second sentence. Third sentence.",
            source_type=SourceType.TEXT,
        )

        result = rep.generate(block)
        assert "- " in result
        assert "First" in result or "Second" in result or "Third" in result


class TestCitationPointerRepresentation:
    """Tests for CitationPointerRepresentation."""

    def test_generate(self):
        rep = CitationPointerRepresentation()
        block = ContextBlock(
            id="test123",
            content="Important information here",
            source_type=SourceType.TEXT,
            file_path="/path/to/doc.txt",
        )

        result = rep.generate(block)
        assert "doc.txt" in result
        assert "test123" in result or "test12" in result


class TestRepresentationGenerator:
    """Tests for RepresentationGenerator."""

    def test_generate_for_block(self):
        generator = RepresentationGenerator()
        block = ContextBlock(
            id="test",
            content="This is a test. It has multiple sentences for testing.",
            source_type=SourceType.TEXT,
            file_path="test.txt",
        )

        representations = generator.generate_for_block(block)

        assert RepresentationType.FULL_TEXT in representations
        assert RepresentationType.CITATION_POINTER in representations
        assert len(representations) >= 2
