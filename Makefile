# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

.PHONY: help install install-dev test test-cov lint format type-check clean build docs demo benchmark benchmark-api precompute serve-mcp benchmark-latency ui

PYTHON := python3
PIP := $(PYTHON) -m pip
PACKAGE_NAME := context_portfolio_optimizer

help:
	@echo "ContextFusion - Context Portfolio Optimizer"
	@echo ""
	@echo "Available targets:"
	@echo "  install      Install the package"
	@echo "  install-dev  Install with all development dependencies"
	@echo "  test         Run the test suite"
	@echo "  test-cov     Run tests with coverage"
	@echo "  lint         Run linting checks (ruff)"
	@echo "  format       Format code (ruff format)"
	@echo "  type-check   Run type checking (mypy)"
	@echo "  clean        Clean build artifacts"
	@echo "  build        Build package distribution"
	@echo "  docs         Build documentation"
	@echo "  demo         Run demo script"
	@echo "  benchmark    Run benchmark suite"
	@echo "  benchmark-api Run API benchmark suite (Anthropic)"
	@echo "  precompute   Precompute context artifacts for a directory"
	@echo "  serve-mcp    Run MCP-style server"
	@echo "  benchmark-latency Benchmark pipeline latency"
	@echo "  ui           Run local Web UI"

install:
	$(PIP) install -e ".[all]"

install-dev:
	$(PIP) install -e ".[all,dev]"
	pre-commit install

test:
	$(PYTHON) -m pytest tests/ -v

test-cov:
	$(PYTHON) -m pytest tests/ -v --cov=$(PACKAGE_NAME) --cov-report=term-missing

test-integration:
	$(PYTHON) -m pytest tests/integration/ -v -m integration

lint:
	ruff check src/ tests/

lint-fix:
	ruff check --fix src/ tests/

format:
	ruff format src/ tests/

type-check:
	mypy src/$(PACKAGE_NAME)

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info/
	rm -rf .pytest_cache/
	rm -rf .mypy_cache/
	rm -rf htmlcov/
	rm -rf .coverage
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete

build: clean
	$(PYTHON) -m build

docs:
	mkdocs build

docs-serve:
	mkdocs serve

demo:
	$(PYTHON) examples/multiformat_ingestion_demo.py

benchmark:
	$(PYTHON) benchmarks/runners/run_tiny_eval.py

benchmark-rag:
	$(PYTHON) benchmarks/runners/run_rag_eval.py

benchmark-api:
	$(PYTHON) benchmarks/runners/run_api_eval.py

precompute:
	$(PYTHON) -m $(PACKAGE_NAME) precompute ./data

serve-mcp:
	$(PYTHON) -m $(PACKAGE_NAME) serve-mcp --host 127.0.0.1 --port 8765

benchmark-latency:
	$(PYTHON) -m $(PACKAGE_NAME) benchmark-latency ./data --iterations 5

ui:
	$(PYTHON) -m $(PACKAGE_NAME) ui --host 127.0.0.1 --port 8080

cli-help:
	$(PYTHON) -m $(PACKAGE_NAME) --help

docker-build:
	docker build -t context-fusion:latest .

docker-run:
	docker run --rm -it context-fusion:latest

bootstrap:
	bash scripts/bootstrap.sh

all-checks: format lint type-check test
	@echo "All checks passed!"
