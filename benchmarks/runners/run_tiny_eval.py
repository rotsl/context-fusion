#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Tiny evaluation runner for ContextFusion."""

import json
from pathlib import Path

from rich.console import Console
from rich.table import Table

console = Console()


def load_tasks(dataset_path: str) -> list[dict]:
    """Load tasks from JSONL file."""
    tasks = []
    with open(dataset_path, "r") as f:
        for line in f:
            line = line.strip()
            if line:
                tasks.append(json.loads(line))
    return tasks


def evaluate_task(task: dict) -> dict:
    """Evaluate a single task."""
    # Placeholder evaluation
    return {
        "task_id": task["task_id"],
        "success": True,
        "tokens_used": 500,
        "latency_ms": 100.0,
    }


def main():
    """Run tiny evaluation."""
    console.print("[bold blue]ContextFusion Tiny Evaluation[/bold blue]\n")

    dataset_path = Path(__file__).parent.parent / "datasets" / "tiny_tasks.jsonl"

    if not dataset_path.exists():
        console.print(f"[red]Dataset not found: {dataset_path}[/red]")
        return

    tasks = load_tasks(str(dataset_path))
    console.print(f"Loaded {len(tasks)} tasks\n")

    results = []
    for task in tasks:
        console.print(f"Evaluating {task['task_id']}...")
        result = evaluate_task(task)
        results.append(result)

    # Display results
    table = Table(title="Results")
    table.add_column("Task ID", style="cyan")
    table.add_column("Success", style="green")
    table.add_column("Tokens", style="yellow")
    table.add_column("Latency (ms)", style="blue")

    for result in results:
        table.add_row(
            result["task_id"],
            "✓" if result["success"] else "✗",
            str(result["tokens_used"]),
            f"{result['latency_ms']:.1f}",
        )

    console.print(table)

    # Summary
    success_rate = sum(1 for r in results if r["success"]) / len(results)
    avg_tokens = sum(r["tokens_used"] for r in results) / len(results)
    avg_latency = sum(r["latency_ms"] for r in results) / len(results)

    console.print(f"\n[bold]Summary:[/bold]")
    console.print(f"  Success rate: {success_rate:.1%}")
    console.print(f"  Avg tokens: {avg_tokens:.0f}")
    console.print(f"  Avg latency: {avg_latency:.1f}ms")


if __name__ == "__main__":
    main()
