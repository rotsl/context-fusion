#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""API benchmark runner for ContextFusion (Anthropic-only)."""

from __future__ import annotations

import argparse
import json
import os
import tempfile
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from time import perf_counter
from typing import Any

from rich.console import Console
from rich.table import Table

from context_portfolio_optimizer import PipelineRunner
from context_portfolio_optimizer.utils.tokenization import count_tokens

console = Console()

BENCHMARK_BUDGET = 120
REPORT_PATH = Path(__file__).parent.parent / "BENCHMARK_API_RESULTS.md"
DATASET_PATH = Path(__file__).parent.parent / "datasets" / "tiny_tasks.jsonl"
DEFAULT_ANTHROPIC_MODEL = "claude-sonnet-4-6"
SMALL_EXAMPLE_TASK = {
    "task_id": "small_001",
    "query": "What is 2+2?",
    "expected_answer": "4",
    "context_files": ["math.txt"],
}


@dataclass
class APIRunResult:
    """One API run result."""

    model: str
    mode: str
    task_id: str
    success: bool
    context_tokens: int
    answer_tokens: int
    context_latency_ms: float
    model_latency_ms: float
    total_latency_ms: float
    answer: str
    error: str | None = None


def load_tasks(dataset_path: str) -> list[dict]:
    """Load tasks from JSONL file."""
    tasks = []
    with open(dataset_path, encoding="utf-8") as file:
        for line in file:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def build_candidate_documents(task: dict[str, Any]) -> list[tuple[str, str]]:
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


def build_small_candidate_documents(task: dict[str, Any]) -> list[tuple[str, str]]:
    """Build an ultra-small context set for quota-safe API smoke benchmarks."""
    task_id = task["task_id"]
    expected = task["expected_answer"]
    context_files = task.get("context_files") or [f"{task_id}_relevant.txt"]
    relevant_name = context_files[0]
    return [
        (relevant_name, f"Answer: {expected}."),
        (f"{task_id}_distractor_1.txt", "Unrelated note."),
    ]


def evaluate_without_contextfusion(task: dict[str, Any], documents: list[tuple[str, str]]) -> dict:
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


def evaluate_with_contextfusion(task: dict[str, Any], documents: list[tuple[str, str]]) -> dict:
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


def load_env_file(path: Path) -> None:
    """Load KEY=VALUE lines from .env into process env."""
    if not path.exists():
        return

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.strip()
        value = value.strip().strip("'").strip('"')
        if key and key not in os.environ:
            os.environ[key] = value


def build_prompt(query: str, context: str) -> str:
    """Build a deterministic QA prompt."""
    return (
        "You are answering a short factual question using only the given context.\n"
        "Return a concise answer only.\n\n"
        f"Question: {query}\n\n"
        "Context:\n"
        f"{context}\n"
    )


def call_anthropic(prompt: str, model: str, api_key: str, max_tokens: int) -> str:
    """Call Anthropic Messages API."""
    from anthropic import Anthropic

    client = Anthropic(api_key=api_key)
    response = client.messages.create(
        model=model,
        max_tokens=max_tokens,
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
    )
    parts = []
    for content_block in response.content:
        text = getattr(content_block, "text", "")
        if text:
            parts.append(text)
    return "\n".join(parts).strip()


def run_one_case(
    *,
    model: str,
    api_key: str,
    task: dict[str, Any],
    mode: str,
    context: str,
    context_tokens: int,
    context_latency_ms: float,
    max_answer_tokens: int,
) -> APIRunResult:
    """Run one Anthropic mode/task benchmark case."""
    prompt = build_prompt(task["query"], context)

    model_start = perf_counter()
    error: str | None = None
    answer = ""
    try:
        answer = call_anthropic(prompt, model, api_key, max_answer_tokens)
    except Exception as exc:
        error = str(exc).replace("\n", " ")
        if len(error) > 220:
            error = error[:220] + "..."
    model_latency_ms = (perf_counter() - model_start) * 1000

    expected = task["expected_answer"].lower()
    success = expected in answer.lower()
    answer_tokens = count_tokens(answer)

    return APIRunResult(
        model=model,
        mode=mode,
        task_id=task["task_id"],
        success=success,
        context_tokens=context_tokens,
        answer_tokens=answer_tokens,
        context_latency_ms=context_latency_ms,
        model_latency_ms=model_latency_ms,
        total_latency_ms=context_latency_ms + model_latency_ms,
        answer=answer,
        error=error,
    )


def summarize(results: list[APIRunResult]) -> dict[str, dict[str, float]]:
    """Summarize metrics grouped by mode."""
    grouped: dict[str, list[APIRunResult]] = {}
    for result in results:
        grouped.setdefault(result.mode, []).append(result)

    summary: dict[str, dict[str, float]] = {}
    for mode, rows in grouped.items():
        count = len(rows)
        success_count = sum(1 for row in rows if row.success and row.error is None)
        avg_context_tokens = sum(row.context_tokens for row in rows) / max(1, count)
        avg_answer_tokens = sum(row.answer_tokens for row in rows) / max(1, count)
        avg_total_latency_ms = sum(row.total_latency_ms for row in rows) / max(1, count)
        error_count = sum(1 for row in rows if row.error is not None)
        summary[mode] = {
            "runs": float(count),
            "success_rate": success_count / max(1, count),
            "avg_context_tokens": avg_context_tokens,
            "avg_answer_tokens": avg_answer_tokens,
            "avg_total_latency_ms": avg_total_latency_ms,
            "errors": float(error_count),
        }
    return summary


def write_report(
    *,
    report_path: Path,
    results: list[APIRunResult],
    summary: dict[str, dict[str, float]],
    anthropic_model: str,
    max_answer_tokens: int,
    small_example: bool,
) -> None:
    """Write markdown API benchmark report."""
    generated_at = datetime.now(UTC).strftime("%Y-%m-%d %H:%M:%SZ")

    lines = [
        "# API Benchmark Results",
        "",
        "Anthropic-only comparison across context modes.",
        "",
        f"- Generated at: `{generated_at}`",
        "- Dataset: `benchmarks/datasets/tiny_tasks.jsonl`",
        f"- ContextFusion budget: `{BENCHMARK_BUDGET}` tokens",
        f"- Anthropic model: `{anthropic_model}`",
        f"- Max answer tokens: `{max_answer_tokens}`",
        f"- Small example mode: `{small_example}`",
        "",
        "## Per-run Results",
        "",
        "| Model | Mode | Task | Success | Context Tokens | Answer Tokens | Total Latency (ms) | Error |",
        "|---|---|---|---:|---:|---:|---:|---|",
    ]

    lines.extend(
        [
            (
                f"| {row.model} | {row.mode} | {row.task_id} | "
                f"{'✓' if row.success else '✗'} | {row.context_tokens} | {row.answer_tokens} | "
                f"{row.total_latency_ms:.1f} | {row.error or ''} |"
            )
            for row in results
        ]
    )

    lines.extend(["", "## Summary", ""])
    lines.append(
        "| Mode | Runs | Success Rate | Avg Context Tokens | Avg Answer Tokens | Avg Total Latency (ms) | Errors |"
    )
    lines.append("|---|---:|---:|---:|---:|---:|---:|")

    for mode, metrics in sorted(summary.items()):
        lines.append(
            f"| {mode} | {int(metrics['runs'])} | {metrics['success_rate']:.1%} | "
            f"{metrics['avg_context_tokens']:.1f} | {metrics['avg_answer_tokens']:.1f} | "
            f"{metrics['avg_total_latency_ms']:.1f} | {int(metrics['errors'])} |"
        )

    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- Success means `expected_answer` appears in model output (case-insensitive).",
            "- `with_contextfusion` uses pipeline-selected context under benchmark budget.",
            "- `without_contextfusion` concatenates all candidate context directly.",
            "",
        ]
    )

    report_path.write_text("\n".join(lines), encoding="utf-8")


def parse_args() -> argparse.Namespace:
    """Parse CLI args."""
    parser = argparse.ArgumentParser(description="Run API benchmark (Anthropic only).")
    parser.add_argument(
        "--anthropic-model",
        default=os.getenv("CPO_ANTHROPIC_BENCHMARK_MODEL", DEFAULT_ANTHROPIC_MODEL),
        help="Anthropic model for benchmark calls.",
    )
    parser.add_argument(
        "--max-tasks",
        type=int,
        default=0,
        help="Limit number of tasks (0 means all).",
    )
    parser.add_argument(
        "--max-answer-tokens",
        type=int,
        default=64,
        help="Maximum output tokens per API response.",
    )
    parser.add_argument(
        "--small-example",
        action="store_true",
        help="Run one ultra-small task/context pair for smoke benchmarks.",
    )
    parser.add_argument(
        "--report-path",
        default=str(REPORT_PATH),
        help="Output markdown report path.",
    )
    return parser.parse_args()


def main() -> None:
    """Run API benchmark."""
    args = parse_args()
    load_env_file(Path(".env"))

    anthropic_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not anthropic_key:
        console.print("[red]ANTHROPIC_API_KEY is missing.[/red]")
        return

    if args.small_example:
        tasks = [SMALL_EXAMPLE_TASK]
    else:
        if not DATASET_PATH.exists():
            console.print(f"[red]Dataset not found: {DATASET_PATH}[/red]")
            return
        all_tasks = load_tasks(str(DATASET_PATH))
        tasks = all_tasks[: args.max_tasks] if args.max_tasks > 0 else all_tasks

    console.print("[bold blue]ContextFusion API Benchmark (Anthropic)[/bold blue]\n")
    console.print(f"Tasks: {len(tasks)}")
    console.print(f"Budget: {BENCHMARK_BUDGET} tokens\n")

    results: list[APIRunResult] = []
    for task in tasks:
        docs = (
            build_small_candidate_documents(task)
            if args.small_example
            else build_candidate_documents(task)
        )
        with_cf = evaluate_with_contextfusion(task, docs)
        without_cf = evaluate_without_contextfusion(task, docs)

        contexts = {
            "with_contextfusion": (
                with_cf["context"],
                int(with_cf["tokens_used"]),
                float(with_cf["latency_ms"]),
            ),
            "without_contextfusion": (
                without_cf["context"],
                int(without_cf["tokens_used"]),
                float(without_cf["latency_ms"]),
            ),
        }

        for mode, (context, context_tokens, context_latency_ms) in contexts.items():
            console.print(f"Running anthropic | {mode} | {task['task_id']}...")
            result = run_one_case(
                model=args.anthropic_model,
                api_key=anthropic_key,
                task=task,
                mode=mode,
                context=context,
                context_tokens=context_tokens,
                context_latency_ms=context_latency_ms,
                max_answer_tokens=args.max_answer_tokens,
            )
            results.append(result)

    table = Table(title="Anthropic API Benchmark Results")
    table.add_column("Mode", style="magenta")
    table.add_column("Task", style="white")
    table.add_column("Success", style="green")
    table.add_column("Ctx Tokens", style="yellow")
    table.add_column("Latency (ms)", style="blue")
    table.add_column("Error", style="red")

    for row in results:
        table.add_row(
            row.mode,
            row.task_id,
            "✓" if row.success else "✗",
            str(row.context_tokens),
            f"{row.total_latency_ms:.1f}",
            row.error or "",
        )
    console.print("")
    console.print(table)

    summary = summarize(results)
    report_path = Path(args.report_path)
    write_report(
        report_path=report_path,
        results=results,
        summary=summary,
        anthropic_model=args.anthropic_model,
        max_answer_tokens=args.max_answer_tokens,
        small_example=args.small_example,
    )

    console.print(f"\n[green]Wrote API benchmark report: {report_path}[/green]")


if __name__ == "__main__":
    main()
