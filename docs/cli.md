# CLI Reference

## Installation

```bash
pip install context-portfolio-optimizer
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
cpo run ./data --budget 3000 --output context.txt
```

Options:
- `--budget, -b`: Token budget (default: 3000)
- `--output, -o`: Output file
- `--config, -c`: Config file path
- `--verbose, -v`: Verbose output

### benchmark

Run benchmark suite.

```bash
cpo benchmark --dataset tiny
cpo benchmark --dataset rag
```

Options:
- `--dataset, -d`: Dataset to use (tiny, rag)
- `--output, -o`: Output directory

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

## Environment Variables

- `OPENAI_API_KEY`: OpenAI API key
- `ANTHROPIC_API_KEY`: Anthropic API key
- `CPO_CONFIG_PATH`: Default config file path
- `CPO_CACHE_DIR`: Cache directory
- `CPO_MEMORY_DIR`: Memory directory
- `CPO_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR)
