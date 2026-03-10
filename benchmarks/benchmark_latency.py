# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Latency benchmark for ContextFusion assembly pipeline."""

from __future__ import annotations

import statistics
import tempfile
from pathlib import Path
from time import perf_counter

from context_portfolio_optimizer.orchestration.runner import PipelineRunner


def run_latency_benchmark(iterations: int = 20) -> dict[str, float]:
    runner = PipelineRunner()

    with tempfile.TemporaryDirectory() as temp_dir:
        data_dir = Path(temp_dir)
        (data_dir / "a.txt").write_text("Latency benchmark sample text A", encoding="utf-8")
        (data_dir / "b.txt").write_text("Latency benchmark sample text B", encoding="utf-8")

        latencies_ms: list[float] = []
        for _ in range(iterations):
            started = perf_counter()
            runner.run_on_directory(str(data_dir), budget=1200, query="Summarize")
            latencies_ms.append((perf_counter() - started) * 1000.0)

    return {
        "p50_ms": statistics.median(latencies_ms),
        "p95_ms": sorted(latencies_ms)[max(0, int(len(latencies_ms) * 0.95) - 1)],
        "avg_ms": statistics.mean(latencies_ms),
    }


if __name__ == "__main__":
    metrics = run_latency_benchmark()
    print(metrics)
