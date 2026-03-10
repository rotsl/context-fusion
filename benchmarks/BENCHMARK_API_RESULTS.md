# API Benchmark Results

Anthropic-only comparison across context modes.

- Generated at: `2026-03-10 16:11:25Z`
- Dataset: `benchmarks/datasets/tiny_tasks.jsonl`
- ContextFusion budget: `120` tokens
- Anthropic model: `claude-sonnet-4-6`
- Max answer tokens: `64`
- Small example mode: `False`

## Per-run Results

| Model | Mode | Task | Success | Context Tokens | Answer Tokens | Total Latency (ms) | Error |
|---|---|---|---:|---:|---:|---:|---|
| claude-sonnet-4-6 | with_contextfusion | tiny_001 | ✓ | 34 | 1 | 4272.6 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_001 | ✓ | 98 | 1 | 2412.4 |  |
| claude-sonnet-4-6 | with_contextfusion | tiny_002 | ✗ | 35 | 24 | 2581.9 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_002 | ✓ | 99 | 17 | 2008.5 |  |
| claude-sonnet-4-6 | with_contextfusion | tiny_003 | ✓ | 35 | 1 | 2759.8 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_003 | ✓ | 100 | 1 | 2134.7 |  |

## Summary

| Mode | Runs | Success Rate | Avg Context Tokens | Avg Answer Tokens | Avg Total Latency (ms) | Errors |
|---|---:|---:|---:|---:|---:|---:|
| with_contextfusion | 3 | 66.7% | 34.7 | 8.7 | 3204.8 | 0 |
| without_contextfusion | 3 | 100.0% | 99.0 | 6.3 | 2185.2 | 0 |

## Notes

- Success means `expected_answer` appears in model output (case-insensitive).
- `with_contextfusion` uses pipeline-selected context under benchmark budget.
- `without_contextfusion` concatenates all candidate context directly.
