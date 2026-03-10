# API Benchmark Results

Anthropic-only comparison across context modes.

- Generated at: `2026-03-10 14:16:30Z`
- Dataset: `benchmarks/datasets/tiny_tasks.jsonl`
- ContextFusion budget: `120` tokens
- Anthropic model: `claude-sonnet-4-6`
- Max answer tokens: `64`
- Small example mode: `False`

## Per-run Results

| Model | Mode | Task | Success | Context Tokens | Answer Tokens | Total Latency (ms) | Error |
|---|---|---|---:|---:|---:|---:|---|
| claude-sonnet-4-6 | with_contextfusion | tiny_001 | ✓ | 40 | 2 | 4279.4 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_001 | ✓ | 98 | 3 | 2698.6 |  |
| claude-sonnet-4-6 | with_contextfusion | tiny_002 | ✓ | 48 | 15 | 2233.4 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_002 | ✓ | 99 | 21 | 2444.6 |  |
| claude-sonnet-4-6 | with_contextfusion | tiny_003 | ✓ | 41 | 1 | 2785.1 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_003 | ✓ | 100 | 1 | 1434.2 |  |

## Summary

| Mode | Runs | Success Rate | Avg Context Tokens | Avg Answer Tokens | Avg Total Latency (ms) | Errors |
|---|---:|---:|---:|---:|---:|---:|
| with_contextfusion | 3 | 100.0% | 43.0 | 6.0 | 3099.3 | 0 |
| without_contextfusion | 3 | 100.0% | 99.0 | 8.3 | 2192.4 | 0 |

## Notes

- Success means `expected_answer` appears in model output (case-insensitive).
- `with_contextfusion` uses pipeline-selected context under benchmark budget.
- `without_contextfusion` concatenates all candidate context directly.
