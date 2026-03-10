# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for compact representation families."""

from context_portfolio_optimizer.representations.registry import RepresentationRegistry
from context_portfolio_optimizer.types import ContextBlock, SourceType


def _code_block() -> ContextBlock:
    content = '''
import os

def add(a, b):
    """Add two numbers"""
    return a + b
'''
    return ContextBlock(
        id="code-1",
        content=content,
        source_type=SourceType.CODE,
        file_path="sample.py",
        token_count=30,
    )


def test_registry_generates_compact_and_code_variants() -> None:
    registry = RepresentationRegistry()
    variants = registry.generate_all(_code_block(), task_type="code")

    rep_types = {variant.representation_type for variant in variants}
    assert "minified_text" in rep_types
    assert "signature_only" in rep_types
    assert any(variant.token_estimate > 0 for variant in variants)
