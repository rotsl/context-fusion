#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

set -e

echo "========================================="
echo "ContextFusion Bootstrap Script"
echo "========================================="

# Check Python version
PYTHON_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
echo "Found Python version: $PYTHON_VERSION"

REQUIRED_VERSION="3.11"
if ! python3 -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)" 2>/dev/null; then
    echo "Error: Python 3.11 or higher is required"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "Upgrading pip..."
pip install --upgrade pip

# Install package with all dependencies
echo "Installing ContextFusion with all dependencies..."
pip install -e ".[all,dev]"

# Install pre-commit hooks
echo "Installing pre-commit hooks..."
pre-commit install

# Create necessary directories
echo "Creating project directories..."
mkdir -p .cpo_cache
mkdir -p .cpo_memory
mkdir -p .cpo_telemetry
mkdir -p examples/output

echo ""
echo "========================================="
echo "Bootstrap complete!"
echo "========================================="
echo ""
echo "To activate the environment:"
echo "  source venv/bin/activate"
echo ""
echo "To run tests:"
echo "  make test"
echo ""
echo "To see available commands:"
echo "  cpo --help"
echo ""
