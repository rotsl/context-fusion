#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

set -e

echo "Running ContextFusion demos..."

echo ""
echo "1. Multiformat Ingestion Demo"
echo "=============================="
python examples/multiformat_ingestion_demo.py

echo ""
echo "2. RAG Context Optimizer Demo"
echo "=============================="
python examples/rag_context_optimizer.py

echo ""
echo "3. Memory Compaction Demo"
echo "=============================="
python examples/memory_compaction_demo.py

echo ""
echo "All demos complete!"
