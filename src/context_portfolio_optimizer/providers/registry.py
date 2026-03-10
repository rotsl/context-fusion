# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Provider registry for adapter-based provider lookup."""

from __future__ import annotations

import os
from collections.abc import Callable
from typing import Any, ClassVar

from .anthropic import AnthropicProvider
from .ollama import OllamaProvider
from .openai import OpenAIProvider
from .openai_compatible import OpenAICompatibleProvider

ProviderFactory = Callable[..., Any]


class ProviderRegistry:
    """Simple provider factory registry."""

    _providers: ClassVar[dict[str, ProviderFactory]] = {}

    @classmethod
    def register(cls, name: str, provider: ProviderFactory) -> None:
        """Register provider factory by name."""
        cls._providers[name] = provider

    @classmethod
    def get(cls, name: str, **kwargs: Any) -> Any:
        """Create a provider instance by name."""
        if name not in cls._providers:
            available = ", ".join(sorted(cls._providers))
            raise KeyError(f"Unknown provider '{name}'. Available: {available}")
        return cls._providers[name](**kwargs)

    @classmethod
    def available(cls) -> list[str]:
        """Return sorted available provider names."""
        return sorted(cls._providers)


def _register_defaults() -> None:
    ProviderRegistry.register("openai", OpenAIProvider)
    ProviderRegistry.register("anthropic", AnthropicProvider)
    ProviderRegistry.register("ollama", OllamaProvider)

    def _openai_compat_factory(**kwargs: Any) -> OpenAICompatibleProvider:
        base_url = kwargs.get("base_url") or os.getenv("OPENAI_COMPAT_BASE_URL")
        api_key = kwargs.get("api_key") or os.getenv("OPENAI_COMPAT_API_KEY")
        if not base_url or not api_key:
            raise ValueError("openai_compatible requires base_url and api_key")
        return OpenAICompatibleProvider(base_url=base_url, api_key=api_key)

    ProviderRegistry.register("openai_compatible", _openai_compat_factory)
    ProviderRegistry.register("grok", _openai_compat_factory)
    ProviderRegistry.register("kimi", _openai_compat_factory)
    ProviderRegistry.register("deepseek", _openai_compat_factory)
    ProviderRegistry.register("together", _openai_compat_factory)
    ProviderRegistry.register("groq", _openai_compat_factory)


_register_defaults()
