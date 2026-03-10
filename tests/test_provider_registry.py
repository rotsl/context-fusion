# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for provider registry."""

import pytest

from context_portfolio_optimizer.providers.registry import ProviderRegistry


def test_provider_registry_lists_defaults():
    names = ProviderRegistry.available()
    assert "anthropic" in names
    assert "grok" in names
    assert "kimi" in names
    assert "ollama" in names
    assert "openai" in names
    assert "openai_compatible" in names


def test_provider_registry_gets_provider_instances():
    ollama = ProviderRegistry.get("ollama")
    assert ollama.name() == "ollama"

    compat = ProviderRegistry.get(
        "openai_compatible",
        base_url="https://example.invalid/v1",
        api_key="test",
    )
    assert compat.name() == "openai_compatible"


def test_provider_registry_unknown_name():
    with pytest.raises(KeyError):
        ProviderRegistry.get("unknown_provider")
