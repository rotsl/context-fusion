# ContextFusion

[![CI](https://github.com/rotsl/context-fusion/actions/workflows/ci.yml/badge.svg)](https://github.com/rotsl/context-fusion/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)

A framework for optimizing LLM context usage across heterogeneous data sources.

## Features

- **Multiformat Ingestion**: Process text, PDFs, DOCX, CSV, JSON, images (OCR), and code
- **Intelligent Normalization**: Convert all sources to uniform `ContextBlock` objects
- **Multiple Representations**: Generate compact alternatives (bullet summaries, JSON, citations)
- **Utility & Risk Scoring**: Evaluate blocks on relevance, trust, freshness, and risk factors
- **Knapsack Optimization**: Solve token budget allocation as constrained optimization
- **Ablation Studies**: Learn which context contributes most to outcomes
- **Memory Management**: Persistent storage with compaction and retention policies
- **Web UI Visualization**: Run and inspect pipeline outputs in a local browser UI

## Quick Start

### Installation

```bash
pip install context-portfolio-optimizer
```

For development:

```bash
git clone https://github.com/rotsl/context-fusion.git
cd context-fusion
make install-dev
```

Create local environment file (kept out of Git):

```bash
cat > .env << 'EOF'
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
EOF
```

### Basic Usage

```python
from context_portfolio_optimizer import PipelineRunner

# Run the full pipeline
runner = PipelineRunner()
result = runner.run(["document.pdf", "code.py"], budget=3000)

print(result["context"])  # Optimized context string
print(result["stats"])    # Processing statistics
```

### CLI Usage

```bash
# Ingest and display content
cpo ingest ./data

# Run optimization pipeline
cpo run ./data --budget 3000 --output context.txt

# Plan for a specific task
cpo plan "Summarize these documents" --budget 5000

# Run ablation study
cpo ablate ./data --budget 3000

# Launch local visualization UI
cpo ui --host 127.0.0.1 --port 8080
```

## Architecture

ContextFusion uses a pipeline architecture:

```
Ingest → Normalize → Represent → Score → Optimize → Assemble
```

1. **Ingest**: Extract content from multiple file formats
2. **Normalize**: Convert to uniform `ContextBlock` objects
3. **Represent**: Generate alternative compact representations
4. **Score**: Compute utility and risk scores
5. **Optimize**: Solve knapsack problem for optimal selection
6. **Assemble**: Build final context string

## Supported Formats

| Format | Extensions | Dependencies |
|--------|------------|--------------|
| Text | `.txt`, `.log` | - |
| Documents | `.pdf` | pdfminer.six |
| | `.docx` | python-docx |
| Structured | `.csv`, `.tsv` | pandas |
| | `.json`, `.jsonl` | - |
| Images | `.png`, `.jpg`, `.tiff` | Pillow, pytesseract |
| Code | `.py`, `.js`, `.ts`, `.go`, `.rs`, etc. | tree-sitter (optional) |
| Markdown | `.md` | - |

## Configuration

Create a `config.yaml`:

```yaml
budget:
  instructions: 1000
  retrieval: 3000
  memory: 2000
  examples: 1500
  tool_trace: 1000
  output_reserve: 1000

scoring:
  utility_weights:
    retrieval: 0.25
    trust: 0.20
    freshness: 0.15
    structure: 0.15
    diversity: 0.15
    token_cost: -0.10

provider:
  name: openai
  model: gpt-4-turbo-preview
```

## Algorithm

ContextFusion treats context selection as a **0/1 Knapsack Problem**:

```
maximize Σ((utility_i − risk_i) * z_i)

subject to:
    Σ(token_i * z_i) ≤ token_budget
    z_i ∈ {0, 1}
```

Where:
- `utility_i`: Based on retrieval, trust, freshness, structure, diversity
- `risk_i`: Based on hallucination proxy, staleness, privacy
- `token_i`: Token count for block i

The optimizer also selects the best representation for each block (full text, bullet summary, citation pointer, etc.).

## Examples

See the `examples/` directory:

- `multiformat_ingestion_demo.py`: Ingest multiple file formats
- `rag_context_optimizer.py`: RAG-optimized context selection
- `memory_compaction_demo.py`: Memory management
- `ablation_demo.py`: Ablation studies

Run examples:

```bash
python examples/multiformat_ingestion_demo.py
```

## Web UI

Run the built-in local UI:

```bash
cpo ui --host 127.0.0.1 --port 8080
```

Then open `http://127.0.0.1:8080`.

You can also use:

```bash
make ui
```

Docker Compose:

```bash
docker compose up cpo-ui
```

## Benchmarks

Run minimal benchmark commands:

```bash
# Tiny benchmark (uses bundled tiny dataset)
make benchmark

# RAG benchmark runner (creates placeholder dataset if missing)
make benchmark-rag
```

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run integration tests
make test-integration
```

## Development

```bash
# Setup development environment
make bootstrap

# Run linting
make lint

# Run type checking
make type-check

# Format code
make format

# Run local Web UI
make ui

# Run all checks
make all-checks
```

## Project Structure

```
context-portfolio-optimizer/
├── src/context_portfolio_optimizer/
│   ├── ingestion/          # File loaders
│   ├── normalization/      # Block building
│   ├── representations/    # Alternative representations
│   ├── scoring/            # Utility and risk models
│   ├── allocation/         # Budget and knapsack optimization
│   ├── memory/             # Memory storage
│   ├── providers/          # LLM providers
│   ├── orchestration/      # Pipeline runner
│   ├── web_ui.py           # Local visualization server
│   └── cli.py              # Command-line interface
├── configs/                # Configuration files
├── examples/               # Usage examples
├── tests/                  # Test suite
└── docs/                   # Documentation
```

## License

Apache-2.0. See [LICENSE](LICENSE) for details.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Roadmap

- [ ] Additional file format support (EPUB, HTML)
- [ ] Learned utility models from feedback
- [ ] Distributed processing for large datasets
- [x] Web UI for visualization
- [ ] Integration with popular RAG frameworks

## Acknowledgments

ContextFusion builds on ideas from information retrieval, operations research, and LLM prompt engineering. The knapsack formulation for context optimization is inspired by classical resource allocation problems.
