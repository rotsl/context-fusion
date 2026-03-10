# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Deterministic lightweight summary helpers used during precompute."""

from __future__ import annotations


def summarize_sentences(text: str, max_sentences: int = 3) -> str:
    """Return first N sentence-like chunks as a deterministic summary."""
    segments: list[str] = []
    for candidate in text.replace("\n", " ").split("."):
        chunk = candidate.strip()
        if not chunk:
            continue
        segments.append(chunk)
        if len(segments) >= max_sentences:
            break
    return ". ".join(segments) + ("." if segments else "")


def outline_summary(text: str, max_lines: int = 5) -> str:
    """Return compact bullet-like outline from first non-empty lines."""
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    selected = lines[:max_lines]
    return "\n".join(f"- {line}" for line in selected)
