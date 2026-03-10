# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""OpenAI provider for ContextFusion."""

import os

from ..logging_utils import get_logger
from ..utils.tokenization import count_tokens
from .base_provider import BaseProvider

logger = get_logger("openai_provider")


class OpenAIProvider(BaseProvider):
    """OpenAI LLM provider."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-3.5-turbo",
        base_url: str | None = None,
    ):
        """Initialize OpenAI provider.

        Args:
            api_key: OpenAI API key
            model: Model name
            base_url: Optional base URL
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model
        self.base_url = base_url
        self._client = None

    def _get_client(self):
        """Get or create OpenAI client."""
        if self._client is None:
            try:
                from openai import OpenAI

                kwargs = {"api_key": self.api_key}
                if self.base_url:
                    kwargs["base_url"] = self.base_url

                self._client = OpenAI(**kwargs)
            except ImportError:
                raise ImportError("openai package required for OpenAIProvider")

        return self._client

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate text using OpenAI.

        Args:
            prompt: Input prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature

        Returns:
            Generated text
        """
        if not self.api_key:
            raise ValueError("OpenAI API key required")

        client = self._get_client()

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=max_tokens,
                temperature=temperature,
            )
            return response.choices[0].message.content or ""
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise

    def count_tokens(self, text: str) -> int:
        """Count tokens.

        Args:
            text: Input text

        Returns:
            Token count
        """
        return count_tokens(text)

    def is_available(self) -> bool:
        """Check if provider is available."""
        try:
            self._get_client()
            return bool(self.api_key)
        except Exception:
            return False
