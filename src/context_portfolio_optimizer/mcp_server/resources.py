# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""MCP-like resource descriptors."""

from __future__ import annotations


def list_resources() -> list[dict[str, str]]:
    """Return static list of MCP resources."""
    return [
        {"id": "context.search", "description": "Search memory/context entries"},
        {"id": "context.compile", "description": "Compile optimized context packet"},
        {"id": "context.plan", "description": "Generate budgeted execution plan"},
        {"id": "context.memory", "description": "Read memory entries"},
        {"id": "context.ablate", "description": "Run ablation analysis"},
    ]
