#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Demo: Ablation studies with ContextFusion."""

import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from context_portfolio_optimizer.ablations.runner import AblationRunner
from context_portfolio_optimizer.allocation.portfolio import PortfolioSelector
from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.normalization.block_builder import BlockBuilder
from context_portfolio_optimizer.representations.base_representation import (
    RepresentationGenerator,
)

console = Console()


def create_test_documents(temp_dir: Path) -> Path:
    """Create test documents for ablation demo."""
    doc_dir = temp_dir / "docs"
    doc_dir.mkdir()

    # Core document - very important
    (doc_dir / "core_concepts.txt").write_text("""
Core Concepts of ContextFusion

ContextFusion is built on several key principles:

1. Token Budget Optimization: Treat context selection as a constrained optimization problem.

2. Utility Scoring: Each context block is scored based on relevance, trust, freshness, and diversity.

3. Risk Assessment: Potential risks like hallucination, staleness, and privacy are evaluated.

4. Knapsack Selection: The 0/1 knapsack algorithm selects the optimal subset of blocks.

5. Multiple Representations: Each block can have multiple compact representations.

These concepts work together to provide efficient context management.
""")

    # Secondary documents
    (doc_dir / "installation.txt").write_text("""
Installation Guide

To install ContextFusion:

pip install context-portfolio-optimizer

For development:
pip install -e ".[all,dev]"

Requirements:
- Python 3.11+
- Optional: pdfminer.six, python-docx, pytesseract
""")

    (doc_dir / "configuration.txt").write_text("""
Configuration Options

ContextFusion can be configured via YAML files:

- Budget allocation across categories
- Utility and risk scoring weights
- Provider settings (OpenAI, Anthropic, local)
- Feature toggles

Environment variables are also supported.
""")

    (doc_dir / "examples.txt").write_text("""
Usage Examples

Basic usage:
from context_portfolio_optimizer import PipelineRunner

runner = PipelineRunner()
result = runner.run(["file.txt"], budget=3000)

Advanced usage with custom configuration:
from context_portfolio_optimizer import Settings, BudgetManager

settings = Settings.from_yaml("config.yaml")
budget_manager = BudgetManager(settings.budget)
""")

    return doc_dir


def main():
    """Run the demo."""
    console.print("[bold blue]ContextFusion Ablation Demo[/bold blue]\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create documents
        console.print("Creating test documents...")
        doc_dir = create_test_documents(Path(temp_dir))

        # Initialize components
        dispatcher = IngestionDispatcher()
        block_builder = BlockBuilder()
        rep_generator = RepresentationGenerator()
        selector = PortfolioSelector()
        ablation_runner = AblationRunner()

        # Ingest documents
        console.print("\nIngesting documents...")
        results = dispatcher.load_directory(str(doc_dir))

        all_segments = []
        for path, segments in results.items():
            all_segments.extend(segments)

        blocks = block_builder.build_blocks(all_segments)

        # Generate representations
        console.print("Generating representations...")
        for block in blocks:
            representations = rep_generator.generate_for_block(block)
            for rep_type, content in representations.items():
                block.representations[rep_type] = content
                from context_portfolio_optimizer.utils.tokenization import count_tokens
                block.representation_tokens[rep_type] = count_tokens(content)

        # Select baseline portfolio
        budget = 1500
        console.print(f"\nSelecting baseline portfolio (budget: {budget} tokens)...")
        portfolio = selector.select(blocks, budget=budget)

        console.print(f"Baseline: {len(portfolio.blocks)} blocks, "
                     f"{portfolio.total_tokens} tokens, "
                     f"utility={portfolio.expected_utility:.3f}")

        # Run leave-one-out ablation
        console.print("\n[bold]Running Leave-One-Out Ablation...[/bold]")
        ablation_results = ablation_runner.run_leave_one_out(blocks, budget)

        # Display results
        table = Table(title="Block Importance (Leave-One-Out)")
        table.add_column("Rank", style="cyan")
        table.add_column("Block ID", style="blue")
        table.add_column("Content Preview", style="white")
        table.add_column("Delta", style="green")
        table.add_column("Importance", style="yellow")

        for i, result in enumerate(ablation_results):
            # Find block content
            block = next((b for b in blocks if b.id == result.block_id), None)
            preview = ""
            if block:
                preview = block.content[:40].replace("\n", " ")
                if len(block.content) > 40:
                    preview += "..."

            if result.delta > 0.1:
                importance = "[red]Critical[/red]"
            elif result.delta > 0.05:
                importance = "[yellow]High[/yellow]"
            elif result.delta > 0.01:
                importance = "Medium"
            else:
                importance = "Low"

            table.add_row(
                str(i + 1),
                result.block_id[:12],
                preview,
                f"{result.delta:.4f}",
                importance,
            )

        console.print(table)

        # Analysis
        analysis = ablation_runner.analyze_importance(ablation_results)
        console.print("\n[bold]Analysis:[/bold]")
        console.print(f"  Most important block: {analysis['most_important'][:16]}")
        console.print(f"  Least important block: {analysis['least_important'][:16]}")
        console.print(f"  Mean delta: {analysis['mean_delta']:.4f}")

        # Run representation swap ablation
        console.print("\n[bold]Running Representation Swap Ablation...[/bold]")
        rep_results = ablation_runner.run_representation_swap(portfolio)

        rep_table = Table(title="Representation Comparison")
        rep_table.add_column("Representation", style="cyan")
        rep_table.add_column("Blocks", style="green")
        rep_table.add_column("Tokens", style="yellow")
        rep_table.add_column("Reward", style="blue")

        for rep_type, data in rep_results.items():
            rep_table.add_row(
                rep_type,
                str(data['blocks']),
                str(data['tokens']),
                f"{data['reward']:.4f}",
            )

        console.print(rep_table)

    console.print("\n[green]Demo complete![/green]")


if __name__ == "__main__":
    main()
