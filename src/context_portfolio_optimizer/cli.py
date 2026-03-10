# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Command-line interface for ContextFusion."""

import json
from dataclasses import asdict
from pathlib import Path
from time import perf_counter

import typer
from rich.console import Console
from rich.table import Table

from . import version
from .allocation.budget import BudgetManager
from .assembly.compiler import compile_for_provider
from .exceptions import ConfigurationError
from .ingestion.dispatcher import IngestionDispatcher
from .logging_utils import setup_logging
from .mcp_server.server import run_mcp_server
from .memory.store import MemoryStore
from .normalization.block_builder import BlockBuilder
from .orchestration.runner import PipelineRunner
from .precompute.runner import PrecomputeRunner
from .settings import Settings

app = typer.Typer(
    name="cpo",
    help="ContextFusion - Context Portfolio Optimizer for LLMs",
    no_args_is_help=True,
)
console = Console()


def get_settings(config: str | None = None) -> Settings:
    """Load settings from config file."""
    if config:
        try:
            return Settings.from_yaml(config)
        except ConfigurationError:
            return Settings.load()
    return Settings.load()


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to file or directory"),
    recursive: bool = typer.Option(
        True, "--recursive/--no-recursive", help="Process directories recursively"
    ),
    config: str | None = typer.Option(None, "--config", "-c", help="Config file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Ingest files and display extracted content."""
    setup_logging(level="DEBUG" if verbose else "INFO")

    dispatcher = IngestionDispatcher()
    block_builder = BlockBuilder()

    path_obj = Path(path)

    if path_obj.is_file():
        segments = dispatcher.load_file(str(path_obj))
        blocks = block_builder.build_blocks(segments)

        console.print(f"[green]Extracted {len(blocks)} blocks from {path}[/green]")

        for i, block in enumerate(blocks[:5]):  # Show first 5
            console.print(f"\n[bold]Block {i + 1}:[/bold]")
            console.print(f"  ID: {block.id}")
            console.print(f"  Type: {block.source_type.name}")
            console.print(f"  Tokens: {block.token_count}")
            console.print(f"  Content preview: {block.content[:100]}...")

        if len(blocks) > 5:
            console.print(f"\n... and {len(blocks) - 5} more blocks")

    elif path_obj.is_dir():
        results = dispatcher.load_directory(str(path_obj), recursive=recursive)

        console.print(f"[green]Processed {len(results)} files from {path}[/green]")

        total_blocks = 0
        for segments in results.values():
            blocks = block_builder.build_blocks(segments)
            total_blocks += len(blocks)

        console.print(f"Total blocks extracted: {total_blocks}")

    else:
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)


@app.command()
def plan(
    task: str = typer.Argument(..., help="Task description"),
    budget: int = typer.Option(8000, "--budget", "-b", help="Token budget"),
    config: str | None = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Plan context optimization for a task."""
    get_settings(config)
    budget_manager = BudgetManager.from_total(budget)

    from .orchestration.planner import Planner

    planner = Planner(budget_manager)
    plan_result = planner.plan(task)

    console.print("[bold]Execution Plan:[/bold]")
    console.print(f"Task: {plan_result['task']}")
    console.print("\nBudget Allocation:")
    for category, tokens in plan_result["budget_allocation"].items():
        console.print(f"  {category}: {tokens} tokens")

    console.print("\nPhases:")
    for phase in plan_result["phases"]:
        console.print(f"  - {phase['name']}: {phase['description']}")

    cost = planner.estimate_cost(plan_result)
    console.print(f"\nEstimated Cost: ${cost['estimated_cost_usd']:.4f}")


@app.command()
def run(
    path: str = typer.Argument(..., help="Path to file or directory"),
    budget: int = typer.Option(3000, "--budget", "-b", help="Token budget for retrieval"),
    query: str | None = typer.Option(None, "--query", "-q", help="Optional query for retrieval"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file"),
    config: str | None = typer.Option(None, "--config", "-c", help="Config file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run full context optimization pipeline."""
    setup_logging(level="DEBUG" if verbose else "INFO")

    runner = PipelineRunner()
    path_obj = Path(path)

    if path_obj.is_file():
        result = runner.run([str(path_obj)], budget, query=query)
    elif path_obj.is_dir():
        result = runner.run_on_directory(str(path_obj), budget=budget, query=query)
    else:
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    # Display results
    console.print("[bold green]Pipeline Complete![/bold green]")
    console.print("\nStats:")
    for key, value in result["stats"].items():
        console.print(f"  {key}: {value}")

    # Display context preview
    context = result["context"]
    console.print("\n[bold]Context Preview:[/bold]")
    console.print(context[:500] + "..." if len(context) > 500 else context)

    # Save to file if requested
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(context)
        console.print(f"\n[green]Context saved to {output}[/green]")


@app.command()
def benchmark(
    dataset: str = typer.Option("tiny", "--dataset", "-d", help="Dataset to use (tiny, rag)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output directory"),
):
    """Run benchmark suite."""
    console.print(f"[bold]Running {dataset} benchmark...[/bold]")

    if dataset == "tiny":
        from benchmarks.runners.run_tiny_eval import main as run_tiny

        run_tiny()
    elif dataset == "rag":
        from benchmarks.runners.run_rag_eval import main as run_rag

        run_rag()
    else:
        console.print(f"[red]Unknown dataset: {dataset}[/red]")
        raise typer.Exit(1)


@app.command()
def memory_compact(
    max_age: int = typer.Option(90, "--max-age", help="Maximum age in days"),
    similarity: float = typer.Option(0.9, "--similarity", help="Similarity threshold"),
    config: str | None = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Compact memory store."""
    settings = get_settings(config)
    store = MemoryStore(settings.memory_path)

    from .memory.compaction import MemoryCompactor

    compactor = MemoryCompactor(store)
    stats = compactor.compact(similarity_threshold=similarity, max_age_days=max_age)

    console.print("[bold]Memory Compaction Results:[/bold]")
    console.print(f"  Removed: {stats['removed']} entries")
    console.print(f"  Kept: {stats['kept']} entries")


@app.command()
def memory_stats(
    config: str | None = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Show memory statistics."""
    settings = get_settings(config)
    store = MemoryStore(settings.memory_path)

    stats = store.get_stats()

    console.print("[bold]Memory Statistics:[/bold]")
    console.print(f"  Total entries: {stats['total_entries']}")
    console.print(f"  Size: {stats['total_size_bytes'] / 1024:.2f} KB")

    if stats["types"]:
        console.print("\n  Entry types:")
        for entry_type, count in stats["types"].items():
            console.print(f"    {entry_type}: {count}")


@app.command()
def ablate(
    path: str = typer.Argument(..., help="Path to file or directory"),
    budget: int = typer.Option(3000, "--budget", "-b", help="Token budget"),
    config: str | None = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Run ablation study on context selection."""
    setup_logging(level="INFO")

    # Run pipeline to get blocks
    runner = PipelineRunner()
    path_obj = Path(path)

    if path_obj.is_file():
        result = runner.run([str(path_obj)], budget)
    elif path_obj.is_dir():
        result = runner.run_on_directory(str(path_obj), budget=budget)
    else:
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    portfolio = result["portfolio"]

    # Run ablation
    from .ablations.runner import AblationRunner

    ablation_runner = AblationRunner()
    ablation_results = ablation_runner.run_leave_one_out(portfolio.blocks, budget)

    # Display results
    console.print("[bold]Ablation Results (Leave-One-Out):[/bold]")
    console.print(f"Baseline reward: {ablation_results[0].baseline_reward:.4f}\n")

    table = Table(title="Block Importance")
    table.add_column("Block ID", style="cyan")
    table.add_column("Delta", style="green")
    table.add_column("Importance", style="yellow")

    for result in ablation_results[:10]:  # Top 10
        importance = "High" if result.delta > 0.1 else "Medium" if result.delta > 0.05 else "Low"
        table.add_row(
            result.block_id[:16],
            f"{result.delta:.4f}",
            importance,
        )

    console.print(table)


@app.command("compile")
def compile_cmd(
    path: str = typer.Argument(..., help="Path to file or directory"),
    task: str = typer.Option("compile", "--task", help="Task description"),
    provider: str = typer.Option("openai", "--provider", help="Provider name"),
    model: str = typer.Option("gpt-4o-mini", "--model", help="Model name"),
    budget: int = typer.Option(4000, "--budget", "-b", help="Token budget"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output JSON file"),
):
    """Compile optimized context packet to provider-specific prompt payload."""
    runner = PipelineRunner()
    path_obj = Path(path)

    if path_obj.is_file():
        result = runner.run(
            [str(path_obj)],
            budget=budget,
            task=task,
            task_type="chat",
            query=task,
        )
    elif path_obj.is_dir():
        result = runner.run_on_directory(
            str(path_obj),
            budget=budget,
            task=task,
            task_type="chat",
            query=task,
        )
    else:
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    packet = result["context_packet"]
    compiled = compile_for_provider(packet, provider_name=provider)
    payload = {
        "provider": provider,
        "model": model,
        "packet": asdict(packet),
        "compiled": compiled,
        "stats": result["stats"],
    }

    if output:
        with open(output, "w", encoding="utf-8") as file:
            json.dump(payload, file, ensure_ascii=False, indent=2, default=str)
        console.print(f"[green]Compiled payload saved to {output}[/green]")
    else:
        preview = json.dumps(compiled, ensure_ascii=False, indent=2, default=str)
        console.print(preview[:1000] + "..." if len(preview) > 1000 else preview)


@app.command("precompute")
def precompute(
    path: str = typer.Argument(..., help="Directory path to precompute"),
    pattern: str = typer.Option("*", "--pattern", help="File glob pattern"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="Process recursively"),
):
    """Precompute summaries, token counts, hashes, and embeddings."""
    runner = PrecomputeRunner()
    stats = runner.run_on_directory(path, pattern=pattern, recursive=recursive)
    console.print("[bold]Precompute Complete:[/bold]")
    for key, value in stats.items():
        console.print(f"  {key}: {value}")


@app.command("serve-mcp")
def serve_mcp(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8765, "--port", help="Port to bind"),
):
    """Run MCP-style server exposing context tools."""
    run_mcp_server(host=host, port=port)


@app.command("benchmark-latency")
def benchmark_latency(
    path: str = typer.Argument(..., help="Path to file or directory"),
    budget: int = typer.Option(3000, "--budget", "-b", help="Token budget"),
    iterations: int = typer.Option(5, "--iterations", "-n", help="Number of runs"),
):
    """Benchmark end-to-end pipeline latency."""
    runner = PipelineRunner()
    path_obj = Path(path)
    if not path_obj.exists():
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    latencies_ms: list[float] = []
    for _ in range(iterations):
        start = perf_counter()
        if path_obj.is_file():
            runner.run([str(path_obj)], budget=budget)
        else:
            runner.run_on_directory(str(path_obj), budget=budget)
        latencies_ms.append((perf_counter() - start) * 1000)

    avg_ms = sum(latencies_ms) / len(latencies_ms)
    min_ms = min(latencies_ms)
    max_ms = max(latencies_ms)

    console.print("[bold]Latency Benchmark:[/bold]")
    console.print(f"  iterations: {iterations}")
    console.print(f"  avg_ms: {avg_ms:.2f}")
    console.print(f"  min_ms: {min_ms:.2f}")
    console.print(f"  max_ms: {max_ms:.2f}")


@app.command("version")
def version_cmd():
    """Show version information."""
    console.print(f"ContextFusion version {version.VERSION}")


@app.command("ui")
def ui(
    host: str = typer.Option("127.0.0.1", "--host", help="Host to bind"),
    port: int = typer.Option(8080, "--port", help="Port to bind"),
):
    """Run local web UI for pipeline visualization."""
    from .web_ui import run_web_ui

    run_web_ui(host=host, port=port)


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
