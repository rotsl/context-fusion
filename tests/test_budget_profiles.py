# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tests for budget profile configuration."""

from context_portfolio_optimizer.config.budget_profiles import (
    get_budget_profile,
    list_budget_profiles,
)


def test_profile_lookup() -> None:
    profile = get_budget_profile("openai_agent")
    assert profile["name"] == "openai_agent"
    assert "retrieval_share" in profile
    assert "compression" in profile


def test_profile_list_contains_expected_entries() -> None:
    names = list_budget_profiles()
    assert "openai_chat" in names
    assert "qa_cited" in names
