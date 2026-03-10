# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""ContextPacket compiler into provider-facing prompt structures."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from context_portfolio_optimizer.ir import ContextPacket


def compile_for_chat(packet: ContextPacket) -> list[dict[str, str]]:
    """Compile packet into chat messages.

    Each selected block is emitted as a system message.
    """
    messages: list[dict[str, str]] = []
    messages.append(
        {
            "role": "system",
            "content": f"Task: {packet.task}\nTask type: {packet.task_type}",
        }
    )

    messages.extend([{"role": "system", "content": block.text} for block in packet.selected_blocks])

    return messages


def compile_plain_text(packet: ContextPacket) -> str:
    """Compile packet into a plain text context string."""
    body = "\n\n---\n\n".join(block.text for block in packet.selected_blocks)
    citations = "\n".join(f"- {citation}" for citation in packet.citations)
    if citations:
        return f"{body}\n\nCitations:\n{citations}" if body else f"Citations:\n{citations}"
    return body


def compile_for_provider(packet: ContextPacket, provider_name: str) -> dict[str, Any]:
    """Compile packet into provider-specific payload envelope."""
    provider = provider_name.lower()
    if provider in {"openai", "anthropic", "ollama", "openai_compatible"}:
        return {
            "messages": compile_for_chat(packet),
            "metadata": {
                "budget": packet.budget,
                "citations": packet.citations,
            },
        }

    return {
        "prompt": compile_plain_text(packet),
        "metadata": {
            "budget": packet.budget,
            "citations": packet.citations,
        },
    }
