# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Provider/use-case budget profile definitions."""

from __future__ import annotations

from copy import deepcopy

from .defaults import DEFAULT_PROFILE

_PROFILES = {
    "openai_chat": {
        "retrieval_share": 0.55,
        "compression": "light",
        "citation_mode": "compact",
        "delta_fusion": False,
    },
    "openai_agent": {
        "retrieval_share": 0.45,
        "compression": "medium",
        "cache_preference": "high",
        "delta_fusion": True,
    },
    "anthropic_chat": {
        "retrieval_share": 0.6,
        "compression": "light",
        "citation_mode": "compact",
    },
    "anthropic_agent": {
        "retrieval_share": 0.48,
        "compression": "medium",
        "delta_fusion": True,
        "cache_preference": "high",
    },
    "ollama_small_local": {
        "retrieval_share": 0.4,
        "compression": "aggressive",
        "representation_aggressiveness": "high",
        "cache_preference": "high",
    },
    "openai_compatible_fast": {
        "retrieval_share": 0.5,
        "compression": "medium",
        "representation_aggressiveness": "high",
    },
    "code_debug": {
        "retrieval_share": 0.65,
        "compression": "light",
        "citation_mode": "compact",
        "delta_fusion": True,
    },
    "qa_cited": {
        "retrieval_share": 0.6,
        "compression": "light",
        "citation_mode": "compact",
        "delta_fusion": False,
    },
}


def get_budget_profile(name: str) -> dict:
    """Get merged budget profile by name with defaults."""
    profile = deepcopy(DEFAULT_PROFILE)
    profile.update(_PROFILES.get(name, {}))
    profile["name"] = name
    return profile


def list_budget_profiles() -> list[str]:
    """List available budget profile names."""
    return sorted(_PROFILES)
