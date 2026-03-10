# ContextFusion

[![CI](https://github.com/rotsl/context-fusion/actions/workflows/ci.yml/badge.svg)](https://github.com/rotsl/context-fusion/actions)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Visitors](https://visitor-badge.laobi.icu/badge?page_id=rotsl.context-fusion)](https://github.com/rotsl/context-fusion)
[![Claude API CF Success](https://img.shields.io/badge/Claude_API_with_CF-100%25-brightgreen.svg)](benchmarks/BENCHMARK_API_RESULTS.md)
[![API Context Tokens](https://img.shields.io/badge/API_context_tokens-10.3_vs_947.0-blue.svg)](benchmarks/BENCHMARK_API_RESULTS.md)
[![Modes](https://img.shields.io/badge/modes-chat%20%7C%20qa%20%7C%20code%20%7C%20agent-orange.svg)](#usage-flowcharts)

ContextFusion keeps answer quality stable while cutting prompt payload size for chat and agent loops.
I built it to solve recurring token bloat and latency spikes in real multi-provider LLM workflows.

ContextFusion is a provider-neutral context compiler and optimization layer for LLMs and agents.
It ingests heterogeneous sources, precomputes compact representations, and assembles cache-aware,
budget-constrained context packets across OpenAI, Anthropic, Ollama, and OpenAI-compatible runtimes.

## Features

- **Multiformat Ingestion**: Process text, PDFs, DOCX, CSV, JSON, images (OCR), and code
- **Intelligent Normalization**: Convert all sources to uniform `ContextBlock` objects
- **Task-Specific Compact Representations**: QA, code, agent, and universal compact variants
- **Utility & Risk Scoring**: Evaluate blocks on relevance, trust, freshness, and risk factors
- **Latency-Aware Multi-Objective Planner**: Value density + token + latency + cacheability planning
- **Canonical IR + Delta Fusion**: Emit `ContextPacket` and incremental `ContextDelta`
- **Dedup + Fingerprinting**: Exact + near-duplicate collapse with provenance retention
- **Multi-Provider Adapters**: OpenAI, Anthropic, Ollama, and OpenAI-compatible APIs
- **Provider-Aware Compilation**: `chat`, `qa`, `code`, `agent` packers and provider formatters
- **Chat + Agent Support**: Cache-aware assembly and incremental agent-loop updates
- **MCP Server**: Expose ContextFusion tools/resources over an MCP-style server
- **Framework Integrations**: Retriever wrappers for LangChain and LlamaIndex
- **Precompute Pipeline**: Store fingerprints, summaries, token stats, compact variants, and features
- **Compression Pipeline**: JSON minify, schema prune, citation compaction policies
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
OPENAI_COMPAT_BASE_URL=
OPENAI_COMPAT_API_KEY=
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

# Run optimization pipeline (backward compatible)
cpo run ./data --budget 3000 --query "Summarize architecture" --output context.txt \
  --provider openai --model gpt-5-mini --mode chat --profile openai_chat

# Plan for a specific task
cpo plan "Summarize these documents" --budget 5000

# Compile provider-ready packet (qa/code/agent/chat modes)
cpo compile ./data \
  --task "Answer with citations" \
  --provider openai \
  --model gpt-5-mini \
  --mode qa \
  --budget 4000 \
  --compression light \
  --delta

# Precompute artifacts for latency reduction
cpo precompute ./data --store-dir .cpo_cache/precompute --semantic-dedup

# Run MCP-style server
cpo serve-mcp --host <host> --port 8765

# Benchmark latency
cpo benchmark-latency ./data --iterations 5

# Inspect cache + precompute store
cpo inspect-cache

# Run ablation study
cpo ablate ./data --budget 3000

# Launch local visualization UI
cpo ui --host <host> --port 8080
```

## What Most Users Need

If you only want to use ContextFusion (not develop it), you mainly need:

1. `README.md` for setup and commands
2. `.env` for provider API keys
3. `configs/` for provider and budget config overrides (optional)
4. `examples/gui_input/` for quick GUI test input
5. `cpo` CLI commands (`run`, `compile`, `ui`, `serve-mcp`)

Provider/client mapping:

- ChatGPT / OpenAI API: use `--provider openai` with `OPENAI_API_KEY`
- Claude AI / Claude API / Claude Code: use `--provider anthropic` with `ANTHROPIC_API_KEY`
- Codex and OpenAI-based tooling: use `--provider openai`
- Local models with Ollama: use `--provider ollama` (no cloud key required)
- Other MCP clients: run `cpo serve-mcp --host <host> --port <port>` and connect to ContextFusion MCP endpoints

## Docker Usage

Build image:

```bash
docker build -t context-fusion:latest .
```

Run interactive CLI container:

```bash
docker run --rm -it -v "$(pwd)":/app context-fusion:latest --help
```

Run GUI with Docker Compose:

```bash
docker compose up cpo-ui
```

Then open `http://localhost:8080`.

Run MCP server with Docker Compose:

```bash
docker compose up cpo-mcp
```

MCP endpoint is available at `http://localhost:8765`.

Useful Make targets:

```bash
make docker-ui
make docker-mcp
make docker-stop
```

## Usage Flowcharts

### Normal User Path (Chat + Agent)

```mermaid
flowchart TD
    A[Install ContextFusion] --> B[Add API keys in .env]
    B --> C{Pick workflow}
    C --> D[Chat workflow]
    C --> E[Agent workflow]
    D --> D1[Choose chat model: gpt-5-mini or claude-sonnet-4-6 or local ollama]
    E --> E1[Choose agentic model: claude-sonnet-4-6 or gpt-5-mini or local tool-using model]
    D1 --> F[Run cpo compile or cpo run]
    E1 --> F
    F --> G[Provider adapter builds request]
    G --> H[Model response + citations + context stats]
```

### Developer Path (Build + Evaluate + Deploy)

```mermaid
flowchart TD
    A[Prepare corpus] --> B[Run cpo precompute]
    B --> C[Run benchmarks and tests]
    C --> D{Serve path}
    D --> E[CLI and app integration]
    D --> F[Web UI]
    E --> G{Runtime mode}
    F --> G
    G --> H[Chat or QA packer]
    G --> I[Agent packer + delta fusion]
    H --> J[Provider adapter]
    I --> J
    J --> K[OpenAI or Anthropic or Ollama or OpenAI-compatible]
    K --> L[Track token, latency, and cache metrics]
```

## Architecture

ContextFusion uses a middleware pipeline architecture:

```
Ingest -> Normalize -> Canonical IR -> Precompute -> Dedup/Fingerprint
-> Query Classify -> Candidate Retrieval -> Fast Rerank -> Budget Planner
-> Context Compression -> Delta Fusion -> Provider Adapter -> Cache-Aware Assemble
```

1. **Ingest**: Extract content from multiple file formats
2. **Normalize**: Convert to uniform `ContextBlock` objects
3. **Represent**: Generate alternative compact representations
4. **Precompute**: Persist compact variants, token stats, retrieval features, and fingerprints
5. **Retrieve**: Query classify + top-100 lexical retrieval + top-20/25 rerank
6. **Plan**: Multi-objective latency-aware representation selection
7. **Assemble**: Build cache segments and canonical `ContextPacket`
8. **Fuse**: Compute `ContextDelta` for repeated agent turns
9. **Compile**: Build provider-specific request-ready payloads

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
  name: anthropic
  model: claude-sonnet-4-6
```

You can also configure:
- `provider.name: openai`
- `provider.name: ollama`
- `provider.name: openai_compatible` (with `OPENAI_COMPAT_BASE_URL` and API key)

## Algorithm

ContextFusion preserves the knapsack foundation and extends it with a configurable multi-objective planner:

```
maximize Σ(
    w_u * utility_i
  - w_r * risk_i
  - w_t * token_cost_i
  - w_l * latency_cost_i
  + w_c * cacheability_i
  + w_d * diversity_i
) * z_i

subject to:
    Σ(token_i * z_i) <= token_budget
    z_i ∈ {0, 1}
```

Where:
- `utility_i`: Based on retrieval, trust, freshness, structure, diversity
- `risk_i`: Based on hallucination proxy, staleness, privacy
- `token_i`: Token count for block i

The planner ranks compact representation variants per block and chooses one best variant per parent block.

## Precompute Workflow

1. Run `cpo precompute ./data`.
2. Store fingerprints, summaries, compact variants, and retrieval features in `.cpo_cache/precompute`.
3. Use `--precomputed-only` in `run`/`compile` to avoid regeneration on cache hits.

## Chat Mode vs Agent Mode

- `chat`: concise context for standard conversation prompts
- `qa`: extractive evidence + citation-first packing
- `code`: signatures, changed regions, and dependency-focused packing
- `agent`: working-memory and constraint deltas with optional incremental fusion

## Compression Pipeline

Compression levels (`none`, `light`, `medium`, `aggressive`) apply:
- citation map compaction (`Source URI` -> `[id]`)
- JSON minification
- schema field pruning where structured payloads are present

## Delta Fusion

Use `--delta` with `run` or `compile` to compute incremental packet changes:
- added blocks
- updated blocks
- removed blocks
- unchanged block IDs

## Cache-Aware Assembly

Each packet is segmented into stable and dynamic segments:
- stable: task/system instructions, citation maps, cacheable blocks
- dynamic: non-cacheable or volatile blocks

This allows reuse across repeated chat/agent turns and lowers effective prompt churn.

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

The UI is a local browser app to run the pipeline and inspect:
- run stats (`files_ingested`, `blocks_selected`, `total_tokens`, etc.)
- representation usage
- selected source types
- selected CF blocks (source, representation, score, token estimate)
- context preview
- model answer (optional CF -> provider/model call)

Run the built-in local UI:

```bash
cpo ui --host <host> --port 8080
```

Then open `http://<host>:8080` in your browser and follow these exact steps:

1. Choose `Input Mode`:
   - `Directory` to process a folder
   - `File list` to process explicit files
2. Choose `Task Mode` (`chat`, `qa`, `code`, `agent`) and enter `Query / Task`.
3. Set `Budget` (token budget).
4. Provide input path(s):
   - `Directory Path` accepts folder or single file (relative or absolute path), example:
     - `./examples/gui_input`
     - `./examples/gui_input/random.csv`
     - `/absolute/path/to/your/data`
   - or `File Paths` (one file per line)
   - repository placeholder file for quick UI checks: `./examples/gui_input/REPO_TRACE_PLACEHOLDER.md`
5. Pick `Provider` and `Model`.
   - For this repo default, use `Provider = anthropic`, `Model = claude-sonnet-4-6`
   - Keep `Call model after CF pipeline` enabled to run CF as middleware between query and model.
6. Click `Run Pipeline`.
7. Review `Run Stats`, `Representation Usage`, `Selected Source Types`, `Selected Blocks`, `Context Preview`, and `Model Answer`.

Notes:
- Set your keys in `.env` (`ANTHROPIC_API_KEY`, `OPENAI_API_KEY`, etc.) before using model-call mode.
- For image inputs, OCR extraction may return `[Image: No text detected]`; model answers will reflect available extracted context.

The server auto-stops when browser clients disconnect (port is released automatically).

You can also use:

```bash
make ui
```

Docker Compose:

```bash
docker compose up cpo-ui
```

## Benchmarks

Run the tiny benchmark comparison:

```bash
make benchmark
```

Output:
- terminal comparison (`ContextFusion` vs `Without ContextFusion`)
- markdown report: `benchmarks/BENCHMARK_RESULTS.md`

Latest tiny benchmark run (`2026-03-10`, local deterministic):
- with ContextFusion success: `100.0%`
- without ContextFusion success: `100.0%`
- avg tokens with ContextFusion: `34.7`
- avg tokens without ContextFusion: `99.0`
- avg token reduction: `65.0%`

For full per-task details, see `benchmarks/BENCHMARK_RESULTS.md`.

Run provider API benchmark:

```bash
make benchmark-api
```

This writes `benchmarks/BENCHMARK_API_RESULTS.md`.

Latest Claude API benchmark run (`2026-03-10`, `claude-sonnet-4-6`):
- with ContextFusion success: `100.0%`
- without ContextFusion success: `100.0%`
- avg context tokens with ContextFusion: `10.3`
- avg context tokens without ContextFusion: `947.0`
- avg total latency with ContextFusion: `7763.3 ms`
- avg total latency without ContextFusion: `8609.6 ms`

### Benchmark Snapshot (Graphical)

`Tiny Benchmark` context tokens (lower is better)

```text
With ContextFusion    34.7  | ████████
Without ContextFusion 99.0  | ████████████████████████
```

`Claude API Benchmark` context tokens (lower is better)

```text
With ContextFusion    10.3  | █
Without ContextFusion 947.0 | ████████████████████████████████████████
```

`Claude API Benchmark` average total latency (lower is better)

```text
With ContextFusion    7763.3 ms | ████████████████████████████████████
Without ContextFusion 8609.6 ms | ███████████████████████████████████████
```

Derived deltas from latest API run:
- context-token reduction with ContextFusion: `98.9%`
- average total-latency improvement with ContextFusion: `9.8%`

See `benchmarks/BENCHMARK_API_RESULTS.md` for per-task latency and answer token details.

For more stable API comparisons under network jitter, run:

```bash
python benchmarks/runners/run_api_eval.py --trials-per-case 2
```

Optional RAG benchmark runner:

```bash
make benchmark-rag
```

Additional benchmark scripts:

```bash
python benchmarks/benchmark_latency.py
python benchmarks/benchmark_tokens.py
python benchmarks/benchmark_agent_loops.py
```

See `benchmarks/BENCHMARK_RESULTS.md` for the required comparison matrix:
1. baseline full-context assembly
2. current ContextFusion
3. ContextFusion + precompute
4. ContextFusion + compression
5. ContextFusion + delta fusion
6. ContextFusion + cache-aware assembly

## Testing

```bash
# Run all tests
make test

# Run with coverage
make test-cov

# Run integration tests
make test-integration
```

Latest local test run (`2026-03-10`):
- command: `contextfusionvenv/bin/pytest tests/ -v`
- result: `49 passed, 0 failed`
- report: `tests/TEST_RESULTS.md`

## Validation Snapshot

Latest local smoke checks (`2026-03-10`):
- pipeline: `python -m context_portfolio_optimizer.cli run ./docs --budget 600 --query "Summarize key architecture points"` completed successfully
- GUI: `cpo ui --host <host> --port 8081` served HTML and `/api/run` responded with JSON
- browser launch: `open http://<host>:8081` executed during verification

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

# Run MCP-style server
make serve-mcp

# Precompute artifacts
make precompute

# Run all checks
make all-checks
```

## Project Structure

```
context-fusion/
├── README.md
├── CITATION.cff
├── GUI_USAGE.md
├── pyproject.toml
├── Dockerfile
├── docker-compose.yml
├── src/context_portfolio_optimizer/
│   ├── ingestion/          # File loaders
│   ├── normalization/      # Block building
│   ├── representations/    # Alternative representations
│   ├── retrieval/          # Two-stage retrieval components
│   ├── scoring/            # Utility and risk models
│   ├── allocation/         # Budget + knapsack/multi-objective planning
│   ├── dedup/              # Fingerprinting + duplicate collapse
│   ├── compression/        # JSON/citation/schema compression policies
│   ├── caching/            # Cache segment and packet cache utilities
│   ├── fusion/             # Context delta computation
│   ├── assembly/           # Provider-aware packet compiler
│   ├── ir/                 # Canonical ContextPacket IR
│   ├── providers/          # Provider adapters + registry
│   ├── config/             # Budget profiles and defaults
│   ├── agents/             # Agent loop support
│   ├── integrations/       # LangChain/LlamaIndex wrappers
│   ├── memory/             # Memory storage
│   ├── mcp_server/         # MCP-style server
│   ├── precompute/         # Offline precompute pipeline
│   ├── orchestration/      # Pipeline runner
│   ├── web_ui.py           # Local visualization server
│   └── cli.py              # Command-line interface
├── configs/                # Provider and runtime configs
├── docs/                   # Documentation
├── benchmarks/             # Benchmark runners + reports
├── examples/               # Demo scripts + GUI inputs
└── tests/                  # Test suite
```

This tree intentionally excludes local-only artifacts in `.gitignore` (for example: `.env`, virtualenvs, caches, and coverage outputs).

## Citation

If ContextFusion supports your research or product, please cite it using [CITATION.cff](CITATION.cff).

```bibtex
@software{r2026contextfusion,
  author       = {Rohan R},
  title        = {ContextFusion},
  year         = {2026},
  url          = {https://github.com/rotsl/context-fusion},
  version      = {0.1.0},
  orcid        = {0009-0005-9225-1775}
}
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

<p align="center">
  <marquee behavior="alternate" direction="up" height="70" scrollamount="2">
    <code>With CF | # | 10.3</code><br />
    <code>Without CF | ######################################## | 947.0</code>
  </marquee>
</p>

<p align="center"><strong>🚀ContextFusion</strong> - Fuse less context, keep more signal, ship faster answers.</p>
