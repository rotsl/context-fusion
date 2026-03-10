# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Provider request formatter functions."""

from __future__ import annotations

from typing import Any


def format_for_openai(messages: list[dict[str, str]], model: str, **kwargs: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "messages": messages}
    payload.update(kwargs)
    return payload


def format_for_anthropic(
    messages: list[dict[str, str]], model: str, **kwargs: Any
) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "messages": messages}
    payload.update(kwargs)
    return payload


def format_for_ollama(messages: list[dict[str, str]], model: str, **kwargs: Any) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "messages": messages, "stream": False}
    payload.update(kwargs)
    return payload


def format_for_openai_compatible(
    messages: list[dict[str, str]],
    model: str,
    **kwargs: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {"model": model, "messages": messages}
    payload.update(kwargs)
    return payload
