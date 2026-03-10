#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Demo: Multiformat ingestion with ContextFusion."""

import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from context_portfolio_optimizer.ingestion.dispatcher import IngestionDispatcher
from context_portfolio_optimizer.normalization.block_builder import BlockBuilder

console = Console()


def create_sample_files(temp_dir: Path) -> list[Path]:
    """Create sample files for demo."""
    files = []

    # Text file
    text_file = temp_dir / "sample.txt"
    text_file.write_text("""This is a sample text file.

It contains multiple paragraphs.

Each paragraph will be extracted as a separate segment.

This demonstrates the text loader functionality.
""")
    files.append(text_file)

    # Markdown file
    md_file = temp_dir / "sample.md"
    md_file.write_text("""# Sample Markdown Document

## Introduction

This is a sample markdown file.

## Features

- Feature one
- Feature two
- Feature three

## Conclusion

This demonstrates the markdown loader.
""")
    files.append(md_file)

    # JSON file
    json_file = temp_dir / "sample.json"
    json_file.write_text("""{
  "name": "Sample Project",
  "version": "1.0.0",
  "description": "A sample project for demo purposes",
  "author": "Demo User",
  "dependencies": {
    "python": ">=3.11",
    "numpy": ">=1.26.0"
  }
}""")
    files.append(json_file)

    # CSV file
    csv_file = temp_dir / "sample.csv"
    csv_file.write_text("""id,name,role,department
1,Alice,Engineer,Engineering
2,Bob,Designer,Design
3,Charlie,Manager,Product
4,Diana,Analyst,Data
""")
    files.append(csv_file)

    # Python code file
    py_file = temp_dir / "sample.py"
    py_file.write_text('''"""Sample Python module for demo."""


def greet(name: str) -> str:
    """Greet a person.

    Args:
        name: Name of the person

    Returns:
        Greeting message
    """
    return f"Hello, {name}!"


class Calculator:
    """Simple calculator class."""

    def add(self, a: float, b: float) -> float:
        """Add two numbers."""
        return a + b

    def subtract(self, a: float, b: float) -> float:
        """Subtract two numbers."""
        return a - b


if __name__ == "__main__":
    print(greet("World"))
    calc = Calculator()
    print(calc.add(1, 2))
''')
    files.append(py_file)

    return files


def main():
    """Run the demo."""
    console.print("[bold blue]ContextFusion Multiformat Ingestion Demo[/bold blue]\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_path = Path(temp_dir)

        # Create sample files
        console.print("Creating sample files...")
        files = create_sample_files(temp_path)

        # Initialize dispatcher and block builder
        dispatcher = IngestionDispatcher()
        block_builder = BlockBuilder()

        # Process each file
        for file_path in files:
            console.print(f"\n[bold]{file_path.name}[/bold]")
            console.print("-" * 40)

            # Load segments
            segments = dispatcher.load_file(str(file_path))

            # Build blocks
            blocks = block_builder.build_blocks(segments)

            # Display results
            table = Table()
            table.add_column("Block #", style="cyan")
            table.add_column("Type", style="green")
            table.add_column("Tokens", style="yellow")
            table.add_column("Preview", style="white")

            for i, block in enumerate(blocks[:5]):  # Show first 5 blocks
                preview = block.content[:50].replace("\n", " ")
                if len(block.content) > 50:
                    preview += "..."

                table.add_row(
                    str(i + 1),
                    block.source_type.name,
                    str(block.token_count),
                    preview,
                )

            console.print(table)
            console.print(f"Total blocks: {len(blocks)}")

    console.print("\n[green]Demo complete![/green]")


if __name__ == "__main__":
    main()
