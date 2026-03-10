# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Provider-aware packet compiler and backward-compatible wrappers."""

from __future__ import annotations

from typing import Any

from context_portfolio_optimizer.compression import (
    apply_citation_map,
    build_citation_id_map,
    minify_json_text,
    prune_json_schema,
    resolve_compression_policy,
)
from context_portfolio_optimizer.ir import ContextPacket

from .agent_packer import pack_agent
from .chat_packer import pack_chat
from .code_packer import pack_code
from .provider_formatters import (
    format_for_anthropic,
    format_for_ollama,
    format_for_openai,
    format_for_openai_compatible,
)
from .qa_packer import pack_qa


def compile_packet(
    packet: ContextPacket,
    provider: str,
    model: str,
    mode: str,
    compression: str = "none",
    **kwargs: Any,
) -> dict[str, Any]:
    """Compile packet into provider request-ready payload."""
    messages = _pack_by_mode(packet, mode)
    messages = _apply_compression(messages, packet, compression)

    provider_key = provider.lower()
    if provider_key == "openai":
        request = format_for_openai(messages, model=model, **kwargs)
    elif provider_key == "anthropic":
        request = format_for_anthropic(messages, model=model, **kwargs)
    elif provider_key == "ollama":
        request = format_for_ollama(messages, model=model, **kwargs)
    elif provider_key in {"openai_compatible", "grok", "kimi", "deepseek", "together", "groq"}:
        request = format_for_openai_compatible(messages, model=model, **kwargs)
    else:
        request = {"model": model, "messages": messages, **kwargs}

    return {
        "provider": provider,
        "model": model,
        "mode": mode,
        "messages": messages,
        "request": request,
        "metadata": {
            "budget": packet.budget,
            "citations": packet.citations,
            "provider_hint": packet.provider_hint,
            "model_hint": packet.model_hint,
            "compression": compression,
        },
    }


def compile_for_chat(packet: ContextPacket) -> list[dict[str, str]]:
    """Backward-compatible chat message compilation."""
    return pack_chat(packet)


def compile_plain_text(packet: ContextPacket) -> str:
    """Backward-compatible plain text compilation."""
    body = "\n\n---\n\n".join(block.text for block in packet.selected_blocks)
    citations = "\n".join(f"- {citation}" for citation in packet.citations)
    if citations:
        return f"{body}\n\nCitations:\n{citations}" if body else f"Citations:\n{citations}"
    return body


def compile_for_provider(packet: ContextPacket, provider_name: str) -> dict[str, Any]:
    """Backward-compatible provider payload compilation."""
    mode = packet.task_type if packet.task_type else "chat"
    compiled = compile_packet(
        packet,
        provider=provider_name,
        model=packet.model_hint or "gpt-4o-mini",
        mode=mode,
    )
    return {
        "messages": compiled["messages"],
        "metadata": compiled["metadata"],
    }


def _pack_by_mode(packet: ContextPacket, mode: str) -> list[dict[str, str]]:
    normalized = mode.lower().strip()
    if normalized == "qa":
        return pack_qa(packet)
    if normalized == "code":
        return pack_code(packet)
    if normalized == "agent":
        return pack_agent(packet)
    return pack_chat(packet)


def _apply_compression(
    messages: list[dict[str, str]],
    packet: ContextPacket,
    compression_level: str,
) -> list[dict[str, str]]:
    policy = resolve_compression_policy(compression_level)
    if policy.level == "none":
        return messages

    citation_map = build_citation_id_map(packet.citations) if policy.compact_citations else {}

    compressed: list[dict[str, str]] = []
    for message in messages:
        content = message["content"]
        is_citation_map = content.startswith("Citation map:")

        if policy.compact_citations and citation_map and not is_citation_map:
            content = apply_citation_map(content, citation_map)
        if policy.minify_json:
            content = minify_json_text(content)
        if policy.prune_schema:
            content = prune_json_schema(content)

        compressed.append({"role": message["role"], "content": content})

    if policy.compact_citations and citation_map:
        compact_map = "\n".join(f"[{idx}] {source}" for source, idx in citation_map.items())
        compressed.append({"role": "system", "content": f"CitationMap\n{compact_map}"})

    return compressed
