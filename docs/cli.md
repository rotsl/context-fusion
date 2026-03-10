# CLI Reference

## Installation

```bash
pip install context-portfolio-optimizer
```

For local development:

```bash
make install-dev
```

Optional `.env` for provider keys:

```bash
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
OPENAI_COMPAT_BASE_URL=...
OPENAI_COMPAT_API_KEY=...
```

## Commands

### ingest

Ingest files and display extracted content.

```bash
cpo ingest ./data
```

Options:
- `--recursive/--no-recursive`: Process directories recursively (default: true)
- `--config, -c`: Config file path
- `--verbose, -v`: Verbose output

### plan

Plan context optimization for a task.

```bash
cpo plan "Summarize these documents"
```

Options:
- `--budget, -b`: Token budget (default: 8000)
- `--config, -c`: Config file path

### run

Run full context optimization pipeline.

```bash
cpo run ./data --budget 3000 --query "Summarize architecture" --output context.txt
```

Options:
- `--budget, -b`: Token budget (default: 3000)
- `--query, -q`: Optional retrieval query for two-stage retrieval
- `--output, -o`: Output file
- `--config, -c`: Config file path
- `--verbose, -v`: Verbose output

### compile

Compile a provider-ready payload from optimized context.

```bash
cpo compile ./data --provider anthropic --model claude-sonnet-4-6 --budget 4000 --task "Summarize architecture"
```

Options:
- `--provider`: Provider name (`openai`, `anthropic`, `ollama`, `openai_compatible`)
- `--model`: Target model name
- `--budget, -b`: Token budget
- `--task`: Task/query string used for retrieval + compilation
- `--output, -o`: Optional output JSON file

### precompute

Precompute summaries, token counts, hashes, and embeddings.

```bash
cpo precompute ./data --pattern "*.md" --recursive
```

Options:
- `--pattern`: File glob pattern (default `*`)
- `--recursive/--no-recursive`: Recursive traversal flag

### benchmark

Run benchmark suite.

```bash
cpo benchmark --dataset tiny
cpo benchmark --dataset rag
```

Options:
- `--dataset, -d`: Dataset to use (tiny, rag)
- `--output, -o`: Output directory

Makefile equivalents:

```bash
make benchmark
make benchmark-rag
make benchmark-api
```

### serve-mcp

Run the MCP-style server exposing context tools/resources.

```bash
cpo serve-mcp --host 127.0.0.1 --port 8765
```

### benchmark-latency

Benchmark pipeline latency on file/directory input.

```bash
cpo benchmark-latency ./data --budget 3000 --iterations 5
```

### memory-compact

Compact memory store.

```bash
cpo memory-compact --max-age 90 --similarity 0.9
```

Options:
- `--max-age`: Maximum age in days (default: 90)
- `--similarity`: Similarity threshold (default: 0.9)
- `--config, -c`: Config file path

### memory-stats

Show memory statistics.

```bash
cpo memory-stats
```

Options:
- `--config, -c`: Config file path

### ablate

Run ablation study.

```bash
cpo ablate ./data --budget 3000
```

Options:
- `--budget, -b`: Token budget (default: 3000)
- `--config, -c`: Config file path

### version

Show version information.

```bash
cpo version
```

### ui

Run local web UI visualization server.

```bash
cpo ui --host 127.0.0.1 --port 8080
```

Options:
- `--host`: Host interface to bind (default: 127.0.0.1)
- `--port`: Port to bind (default: 8080)

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `OPENAI_COMPAT_BASE_URL`: Base URL for OpenAI-compatible providers
- `OPENAI_COMPAT_API_KEY`: API key for OpenAI-compatible providers
- `CPO_CONFIG_PATH`: Default config file path
- `CPO_CACHE_DIR`: Cache directory
- `CPO_MEMORY_DIR`: Memory directory
- `CPO_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR)
