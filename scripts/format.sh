#!/bin/bash
# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

set -e

echo "Running code formatters..."

# Format with ruff
echo "Formatting with ruff..."
ruff format src/ tests/

echo "Formatting complete!"
