# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Command-line interface for ContextFusion."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

from . import version
from .allocation.budget import BudgetManager
from .allocation.portfolio import PortfolioSelector
from .ingestion.dispatcher import IngestionDispatcher
from .logging_utils import setup_logging
from .memory.store import MemoryStore
from .normalization.block_builder import BlockBuilder
from .orchestration.runner import PipelineRunner
from .representations.base_representation import RepresentationGenerator
from .settings import Settings

app = typer.Typer(
    name="cpo",
    help="ContextFusion - Context Portfolio Optimizer for LLMs",
    no_args_is_help=True,
)
console = Console()


def get_settings(config: Optional[str] = None) -> Settings:
    """Load settings from config file."""
    if config:
        return Settings.from_yaml(config)
    return Settings.load()


@app.command()
def ingest(
    path: str = typer.Argument(..., help="Path to file or directory"),
    recursive: bool = typer.Option(True, "--recursive/--no-recursive", help="Process directories recursively"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
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
            console.print(f"\n[bold]Block {i+1}:[/bold]")
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
        for file_path, segments in results.items():
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
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Plan context optimization for a task."""
    settings = get_settings(config)
    budget_manager = BudgetManager.from_total(budget)

    from .orchestration.planner import Planner

    planner = Planner(budget_manager)
    plan_result = planner.plan(task)

    console.print("[bold]Execution Plan:[/bold]")
    console.print(f"Task: {plan_result['task']}")
    console.print(f"\nBudget Allocation:")
    for category, tokens in plan_result['budget_allocation'].items():
        console.print(f"  {category}: {tokens} tokens")

    console.print(f"\nPhases:")
    for phase in plan_result['phases']:
        console.print(f"  - {phase['name']}: {phase['description']}")

    cost = planner.estimate_cost(plan_result)
    console.print(f"\nEstimated Cost: ${cost['estimated_cost_usd']:.4f}")


@app.command()
def run(
    path: str = typer.Argument(..., help="Path to file or directory"),
    budget: int = typer.Option(3000, "--budget", "-b", help="Token budget for retrieval"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Verbose output"),
):
    """Run full context optimization pipeline."""
    setup_logging(level="DEBUG" if verbose else "INFO")

    runner = PipelineRunner()
    path_obj = Path(path)

    if path_obj.is_file():
        result = runner.run([str(path_obj)], budget)
    elif path_obj.is_dir():
        result = runner.run_on_directory(str(path_obj), budget=budget)
    else:
        console.print(f"[red]Path not found: {path}[/red]")
        raise typer.Exit(1)

    # Display results
    console.print("[bold green]Pipeline Complete![/bold green]")
    console.print(f"\nStats:")
    for key, value in result['stats'].items():
        console.print(f"  {key}: {value}")

    # Display context preview
    context = result['context']
    console.print(f"\n[bold]Context Preview:[/bold]")
    console.print(context[:500] + "..." if len(context) > 500 else context)

    # Save to file if requested
    if output:
        with open(output, "w", encoding="utf-8") as f:
            f.write(context)
        console.print(f"\n[green]Context saved to {output}[/green]")


@app.command()
def benchmark(
    dataset: str = typer.Option("tiny", "--dataset", "-d", help="Dataset to use (tiny, rag)"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output directory"),
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
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
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
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
):
    """Show memory statistics."""
    settings = get_settings(config)
    store = MemoryStore(settings.memory_path)

    stats = store.get_stats()

    console.print("[bold]Memory Statistics:[/bold]")
    console.print(f"  Total entries: {stats['total_entries']}")
    console.print(f"  Size: {stats['total_size_bytes'] / 1024:.2f} KB")

    if stats['types']:
        console.print(f"\n  Entry types:")
        for entry_type, count in stats['types'].items():
            console.print(f"    {entry_type}: {count}")


@app.command()
def ablate(
    path: str = typer.Argument(..., help="Path to file or directory"),
    budget: int = typer.Option(3000, "--budget", "-b", help="Token budget"),
    config: Optional[str] = typer.Option(None, "--config", "-c", help="Config file path"),
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

    portfolio = result['portfolio']

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


@app.command()
def version_cmd():
    """Show version information."""
    console.print(f"ContextFusion version {version.VERSION}")


def main():
    """Main entry point."""
    app()


if __name__ == "__main__":
    main()
