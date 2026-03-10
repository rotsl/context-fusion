# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Token efficiency benchmark for ContextFusion modes."""

from __future__ import annotations

import tempfile
from pathlib import Path

from context_portfolio_optimizer.assembly.compiler import compile_packet
from context_portfolio_optimizer.orchestration.runner import PipelineRunner
from context_portfolio_optimizer.utils.tokenization import count_tokens


def run_token_benchmark() -> dict[str, int]:
    runner = PipelineRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir)
        content = """
            ContextFusion compiles compact context packets for QA and agent workloads.
            It uses retrieval, reranking, deduplication, and budget-aware planning.
            The same policy and architecture description appears repeatedly.
            The same policy and architecture description appears repeatedly.
            The same policy and architecture description appears repeatedly.
            The same policy and architecture description appears repeatedly.
            """
        (data_dir / "doc.txt").write_text(content, encoding="utf-8")
        (data_dir / "doc2.txt").write_text(content, encoding="utf-8")

        result = runner.run_on_directory(str(data_dir), budget=220, query="Answer with citations")
        packet = result["context_packet"]

        baseline_context = content * 2
        qa_compiled = compile_packet(
            packet,
            provider="openai",
            model="gpt-5-mini",
            mode="qa",
            compression="aggressive",
        )
        chat_compiled = compile_packet(
            packet,
            provider="openai",
            model="gpt-5-mini",
            mode="chat",
            compression="light",
        )

        baseline_tokens = count_tokens(baseline_context)
        qa_tokens = count_tokens(
            "\n".join(message["content"] for message in qa_compiled["messages"])
        )
        chat_tokens = count_tokens(
            "\n".join(message["content"] for message in chat_compiled["messages"])
        )

    return {
        "baseline_tokens": baseline_tokens,
        "chat_tokens": chat_tokens,
        "qa_tokens": qa_tokens,
        "qa_savings": baseline_tokens - qa_tokens,
    }


if __name__ == "__main__":
    metrics = run_token_benchmark()
    print(metrics)
