#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Tiny evaluation runner for ContextFusion.

Compares:
1. With ContextFusion (pipeline selection under budget)
2. Without ContextFusion (all candidate context concatenated)
"""

from __future__ import annotations

import json
import tempfile
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter

from rich.console import Console
from rich.table import Table

from context_portfolio_optimizer import PipelineRunner
from context_portfolio_optimizer.utils.tokenization import count_tokens

console = Console()

BENCHMARK_BUDGET = 120
REPORT_PATH = Path(__file__).parent.parent / "BENCHMARK_RESULTS.md"


def load_tasks(dataset_path: str) -> list[dict]:
    """Load tasks from JSONL file."""
    tasks = []
    with open(dataset_path) as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def build_candidate_documents(task: dict) -> list[tuple[str, str]]:
    """Build deterministic relevant + distractor context for a task."""
    task_id = task["task_id"]
    expected = task["expected_answer"]
    query = task["query"]

    context_files = task.get("context_files") or [f"{task_id}_relevant.txt"]
    relevant_name = context_files[0]
    relevant_content = (
        f"Answer: {expected}. "
        f"Question: {query}. "
        f"Detailed context for {task_id}: this source explains why the answer is {expected} "
        "and includes extra narrative. "
        "Additional background text is intentionally verbose to emulate larger source documents "
        "and create a realistic token load. "
        "The key fact remains stable and unambiguous in this relevant source."
    )

    distractor_1 = "Deployment checklist for unrelated web services and CI workflows."
    distractor_2 = "Incident response notes for logging systems and dashboards."
    distractor_3 = "Unrelated glossary for networking, metrics, and release tagging."

    return [
        (relevant_name, relevant_content),
        (f"{task_id}_distractor_1.txt", distractor_1),
        (f"{task_id}_distractor_2.txt", distractor_2),
        (f"{task_id}_distractor_3.txt", distractor_3),
    ]


def evaluate_without_contextfusion(task: dict, documents: list[tuple[str, str]]) -> dict:
    """Baseline: use all context documents without selection."""
    start = perf_counter()
    full_context = "\n\n".join(content for _, content in documents)
    latency_ms = (perf_counter() - start) * 1000
    expected = task["expected_answer"].lower()
    success = expected in full_context.lower()
    tokens_used = count_tokens(full_context)
    return {
        "success": success,
        "tokens_used": tokens_used,
        "latency_ms": latency_ms,
        "context": full_context,
    }


def evaluate_with_contextfusion(task: dict, documents: list[tuple[str, str]]) -> dict:
    """Run ContextFusion pipeline over candidate documents."""
    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)
        file_paths: list[str] = []

        for name, content in documents:
            file_path = temp_path / name
            file_path.write_text(content, encoding="utf-8")
            file_paths.append(str(file_path))

        runner = PipelineRunner()
        start = perf_counter()
        result = runner.run(file_paths=file_paths, budget=BENCHMARK_BUDGET)
        latency_ms = (perf_counter() - start) * 1000

        context = result["context"]
        expected = task["expected_answer"].lower()
        success = expected in context.lower()
        tokens_used = result["stats"]["total_tokens"]

        return {
            "success": success,
            "tokens_used": tokens_used,
            "latency_ms": latency_ms,
            "context": context,
            "stats": result["stats"],
        }


def write_markdown_report(task_results: list[dict], summary: dict, report_path: Path) -> None:
    """Write markdown benchmark report."""
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%SZ")

    lines = [
        "# Benchmark Results",
        "",
        "Comparison: **ContextFusion** vs **Without ContextFusion**",
        "",
        f"- Generated at: `{generated_at}`",
        f"- Budget used (ContextFusion): `{BENCHMARK_BUDGET}` tokens",
        "- Dataset: `benchmarks/datasets/tiny_tasks.jsonl`",
        "",
        "## Per-task Results",
        "",
        "| Task | With CF Success | With CF Tokens | Without CF Success | Without CF Tokens | Token Reduction |",
        "|---|---:|---:|---:|---:|---:|",
    ]

    for result in task_results:
        token_reduction = (
            (result["without"]["tokens_used"] - result["with"]["tokens_used"])
            / max(1, result["without"]["tokens_used"])
            * 100
        )
        lines.append(
            f"| {result['task_id']} "
            f"| {'✓' if result['with']['success'] else '✗'} "
            f"| {result['with']['tokens_used']} "
            f"| {'✓' if result['without']['success'] else '✗'} "
            f"| {result['without']['tokens_used']} "
            f"| {token_reduction:.1f}% |"
        )

    lines.extend(
        [
            "",
            "## Summary",
            "",
            f"- With ContextFusion success rate: **{summary['with_success_rate']:.1%}**",
            f"- Without ContextFusion success rate: **{summary['without_success_rate']:.1%}**",
            f"- Avg tokens with ContextFusion: **{summary['with_avg_tokens']:.1f}**",
            f"- Avg tokens without ContextFusion: **{summary['without_avg_tokens']:.1f}**",
            f"- Avg token reduction: **{summary['avg_token_reduction_pct']:.1f}%**",
            f"- Avg latency with ContextFusion: **{summary['with_avg_latency_ms']:.1f} ms**",
            f"- Avg latency without ContextFusion: **{summary['without_avg_latency_ms']:.3f} ms**",
            "",
            "## Notes",
            "",
            "- This tiny benchmark is deterministic and local-only.",
            "- It measures context-selection efficiency and expected-answer retention in context.",
            "- It does not call external LLM APIs.",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    """Run tiny evaluation."""
    console.print("[bold blue]ContextFusion Tiny Evaluation[/bold blue]\n")

    dataset_path = Path(__file__).parent.parent / "datasets" / "tiny_tasks.jsonl"
    if not dataset_path.exists():
        console.print(f"[red]Dataset not found: {dataset_path}[/red]")
        return

    tasks = load_tasks(str(dataset_path))
    console.print(f"Loaded {len(tasks)} tasks")
    console.print(f"Benchmark budget (ContextFusion): {BENCHMARK_BUDGET} tokens\n")

    task_results: list[dict] = []
    for task in tasks:
        console.print(f"Evaluating {task['task_id']}...")
        docs = build_candidate_documents(task)
        with_cf = evaluate_with_contextfusion(task, docs)
        without_cf = evaluate_without_contextfusion(task, docs)
        task_results.append(
            {
                "task_id": task["task_id"],
                "with": with_cf,
                "without": without_cf,
            }
        )

    table = Table(title="ContextFusion vs Without ContextFusion")
    table.add_column("Task", style="cyan")
    table.add_column("With CF", style="green")
    table.add_column("With Tokens", style="yellow")
    table.add_column("Without CF", style="green")
    table.add_column("Without Tokens", style="yellow")
    table.add_column("Token Reduction", style="blue")

    for result in task_results:
        token_reduction = (
            (result["without"]["tokens_used"] - result["with"]["tokens_used"])
            / max(1, result["without"]["tokens_used"])
            * 100
        )
        table.add_row(
            result["task_id"],
            "✓" if result["with"]["success"] else "✗",
            str(result["with"]["tokens_used"]),
            "✓" if result["without"]["success"] else "✗",
            str(result["without"]["tokens_used"]),
            f"{token_reduction:.1f}%",
        )

    console.print("")
    console.print(table)

    with_success_rate = sum(1 for r in task_results if r["with"]["success"]) / len(task_results)
    without_success_rate = sum(1 for r in task_results if r["without"]["success"]) / len(
        task_results
    )
    with_avg_tokens = sum(r["with"]["tokens_used"] for r in task_results) / len(task_results)
    without_avg_tokens = sum(r["without"]["tokens_used"] for r in task_results) / len(task_results)
    avg_token_reduction_pct = (
        (without_avg_tokens - with_avg_tokens) / max(1, without_avg_tokens) * 100
    )
    with_avg_latency_ms = sum(r["with"]["latency_ms"] for r in task_results) / len(task_results)
    without_avg_latency_ms = sum(r["without"]["latency_ms"] for r in task_results) / len(
        task_results
    )

    summary = {
        "with_success_rate": with_success_rate,
        "without_success_rate": without_success_rate,
        "with_avg_tokens": with_avg_tokens,
        "without_avg_tokens": without_avg_tokens,
        "avg_token_reduction_pct": avg_token_reduction_pct,
        "with_avg_latency_ms": with_avg_latency_ms,
        "without_avg_latency_ms": without_avg_latency_ms,
    }

    console.print("\n[bold]Summary:[/bold]")
    console.print(f"  With CF success: {with_success_rate:.1%}")
    console.print(f"  Without CF success: {without_success_rate:.1%}")
    console.print(f"  With CF avg tokens: {with_avg_tokens:.1f}")
    console.print(f"  Without CF avg tokens: {without_avg_tokens:.1f}")
    console.print(f"  Avg token reduction: {avg_token_reduction_pct:.1f}%")

    write_markdown_report(task_results, summary, REPORT_PATH)
    console.print(f"\n[green]Wrote benchmark report: {REPORT_PATH}[/green]")


if __name__ == "__main__":
    main()
