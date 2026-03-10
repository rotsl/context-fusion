# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Mock provider for testing ContextFusion."""

from ..utils.tokenization import count_tokens
from .base_provider import BaseProvider


class MockProvider(BaseProvider):
    """Mock LLM provider for testing."""

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate mock response.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens
            temperature: Temperature (ignored)

        Returns:
            Mock response
        """
        prompt_tokens = self.count_tokens(prompt)
        return f"[Mock response for prompt with {prompt_tokens} tokens]"

    def count_tokens(self, text: str) -> int:
        """Count tokens.

        Args:
            text: Input text

        Returns:
            Token count
        """
        return count_tokens(text)

    def is_available(self) -> bool:
        """Always available."""
        return True
