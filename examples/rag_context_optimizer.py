#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Demo: RAG context optimization with ContextFusion."""

import tempfile
from pathlib import Path

from rich.console import Console
from rich.panel import Panel

from context_portfolio_optimizer.allocation.portfolio import PortfolioSelector
from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.normalization.block_builder import BlockBuilder
from context_portfolio_optimizer.orchestration.context_builder import ContextBuilder
from context_portfolio_optimizer.representations.base_representation import (
    RepresentationGenerator,
)

console = Console()


def create_knowledge_base(temp_dir: Path) -> Path:
    """Create a sample knowledge base."""
    kb_dir = temp_dir / "knowledge_base"
    kb_dir.mkdir()

    # Document 1: Product info
    (kb_dir / "product.txt").write_text("""Product: ContextFusion
Version: 1.0.0

ContextFusion is a framework for optimizing LLM context usage.

Key Features:
- Multiformat ingestion (PDF, DOCX, CSV, JSON, code, images)
- Intelligent context block normalization
- Multiple representation generation
- Utility and risk scoring
- Knapsack-based token budget allocation
- Ablation studies for learning

Benefits:
- Reduce token costs by up to 40%
- Improve response quality
- Support for heterogeneous data sources
- Production-ready with comprehensive testing
""")

    # Document 2: API reference
    (kb_dir / "api.md").write_text("""# API Reference

## Core Classes

### IngestionDispatcher

The `IngestionDispatcher` routes files to appropriate loaders.

```python
from context_portfolio_optimizer import IngestionDispatcher

dispatcher = IngestionDispatcher()
segments = dispatcher.load_file("document.pdf")
```

### BlockBuilder

The `BlockBuilder` normalizes segments to context blocks.

```python
from context_portfolio_optimizer import BlockBuilder

builder = BlockBuilder()
blocks = builder.build_blocks(segments)
```

### PortfolioSelector

The `PortfolioSelector` optimizes context selection.

```python
from context_portfolio_optimizer import PortfolioSelector

selector = PortfolioSelector()
portfolio = selector.select(blocks, budget=3000)
```
""")

    # Document 3: Configuration
    (kb_dir / "config.json").write_text("""{
  "optimization": {
    "algorithm": "knapsack",
    "objective": "maximize_utility",
    "constraints": ["token_budget", "risk_tolerance"]
  },
  "representations": [
    "full_text",
    "bullet_summary",
    "structured_json",
    "citation_pointer"
  ],
  "scoring": {
    "utility_weights": {
      "retrieval": 0.25,
      "trust": 0.20,
      "freshness": 0.15
    }
  }
}""")

    return kb_dir


def main():
    """Run the demo."""
    console.print("[bold blue]ContextFusion RAG Context Optimizer Demo[/bold blue]\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create knowledge base
        console.print("Creating sample knowledge base...")
        kb_dir = create_knowledge_base(Path(temp_dir))

        # Initialize components
        dispatcher = IngestionDispatcher()
        block_builder = BlockBuilder()
        rep_generator = RepresentationGenerator()
        selector = PortfolioSelector()
        context_builder = ContextBuilder()

        # Ingest all documents
        console.print("\nIngesting documents...")
        results = dispatcher.load_directory(str(kb_dir))

        all_segments = []
        for path, segments in results.items():
            all_segments.extend(segments)
            console.print(f"  Loaded {len(segments)} segments from {Path(path).name}")

        # Normalize to blocks
        console.print("\nNormalizing to context blocks...")
        blocks = block_builder.build_blocks(all_segments)
        console.print(f"  Created {len(blocks)} blocks")

        # Generate representations
        console.print("\nGenerating alternative representations...")
        for block in blocks:
            representations = rep_generator.generate_for_block(block)
            for rep_type, content in representations.items():
                block.representations[rep_type] = content
                from context_portfolio_optimizer.utils.tokenization import count_tokens
                block.representation_tokens[rep_type] = count_tokens(content)

        # Select optimal portfolio
        budget = 800
        console.print(f"\nSelecting optimal portfolio (budget: {budget} tokens)...")
        portfolio = selector.select(blocks, budget=budget)

        console.print(f"  Selected {len(portfolio.blocks)} blocks")
        console.print(f"  Total tokens: {portfolio.total_tokens}")
        console.print(f"  Expected utility: {portfolio.expected_utility:.3f}")
        console.print(f"  Total risk: {portfolio.total_risk:.3f}")

        # Build final context
        console.print("\nBuilding optimized context...")
        context = context_builder.build(portfolio)

        # Display result
        console.print(Panel(
            context[:800] + "..." if len(context) > 800 else context,
            title="Optimized Context",
            border_style="green",
        ))

        # Show representation usage
        console.print("\n[bold]Representation Usage:[/bold]")
        from collections import Counter
        rep_counts = Counter(portfolio.representations_used.values())
        for rep_type, count in rep_counts.most_common():
            console.print(f"  {rep_type.value}: {count} blocks")

    console.print("\n[green]Demo complete![/green]")


if __name__ == "__main__":
    main()
