#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

set -e

echo "Running tests..."

# Run pytest with coverage
python -m pytest tests/ -v \
    --cov=context_portfolio_optimizer \
    --cov-report=term-missing \
    --cov-report=html:htmlcov

echo "Tests complete!"
echo "Coverage report: htmlcov/index.html"
