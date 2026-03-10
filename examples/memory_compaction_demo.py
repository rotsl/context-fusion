#!/usr/bin/env python3
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Demo: Memory compaction with ContextFusion."""

import tempfile
from pathlib import Path

from rich.console import Console
from rich.table import Table

from context_portfolio_optimizer.memory.compaction import MemoryCompactor
from context_portfolio_optimizer.memory.store import MemoryStore

console = Console()


def main():
    """Run the demo."""
    console.print("[bold blue]ContextFusion Memory Compaction Demo[/bold blue]\n")

    with tempfile.TemporaryDirectory() as temp_dir:
        # Create memory store
        store = MemoryStore(temp_dir)

        console.print("Adding memory entries...")

        # Add some entries
        entries = [
            ("User asked about Python dictionaries", {"topic": "python", "type": "question"}),
            ("User asked about Python lists", {"topic": "python", "type": "question"}),
            ("User asked about Python tuples", {"topic": "python", "type": "question"}),
            ("Explained dictionary methods: get(), keys(), values()", {"topic": "python", "type": "explanation"}),
            ("Explained list methods: append(), extend(), pop()", {"topic": "python", "type": "explanation"}),
            ("User preference: prefers code examples", {"topic": "preferences", "type": "preference"}),
            ("User preference: likes detailed explanations", {"topic": "preferences", "type": "preference"}),
        ]

        for content, metadata in entries:
            entry_id = store.append(content, metadata, entry_type=metadata.get("type", "general"))
            console.print(f"  Added: {content[:40]}... [{entry_id[:8]}]")

        # Show stats before compaction
        console.print("\n[bold]Before Compaction:[/bold]")
        stats_before = store.get_stats()
        console.print(f"  Total entries: {stats_before['total_entries']}")

        # Search for entries
        console.print("\nSearching for 'Python':")
        results = store.search(query="Python", limit=5)
        for entry in results:
            console.print(f"  - {entry['content']}")

        # Compact memory
        console.print("\n[bold]Compacting memory...[/bold]")
        compactor = MemoryCompactor(store)
        compact_stats = compactor.compact(similarity_threshold=0.8)

        console.print(f"  Removed: {compact_stats['removed']} entries")
        console.print(f"  Kept: {compact_stats['kept']} entries")

        # Show stats after compaction
        console.print("\n[bold]After Compaction:[/bold]")
        stats_after = store.get_stats()
        console.print(f"  Total entries: {stats_after['total_entries']}")

        # Show remaining entries
        console.print("\nRemaining entries:")
        all_entries = store.get_all()
        table = Table()
        table.add_column("ID", style="cyan")
        table.add_column("Type", style="green")
        table.add_column("Content", style="white")

        for entry in all_entries:
            table.add_row(
                entry['id'][:8],
                entry.get('type', 'unknown'),
                entry['content'][:50],
            )

        console.print(table)

    console.print("\n[green]Demo complete![/green]")


if __name__ == "__main__":
    main()
