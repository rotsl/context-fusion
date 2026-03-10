#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

set -e

echo "Running linters..."

# Run ruff
echo "Running ruff..."
ruff check src/ tests/

# Run mypy
echo "Running mypy..."
mypy src/context_portfolio_optimizer

echo "Linting complete!"
