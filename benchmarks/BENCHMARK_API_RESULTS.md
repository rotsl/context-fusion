# API Benchmark Results

Anthropic-only comparison across context modes.

- Generated at: `2026-03-10 16:39:43Z`
- Dataset: `benchmarks/datasets/tiny_tasks.jsonl`
- ContextFusion budget: `120` tokens
- Anthropic model: `claude-sonnet-4-6`
- Max answer tokens: `64`
- Small example mode: `False`
- Trials per case: `2`

## Per-run Results

| Model | Mode | Task | Success | Context Tokens | Answer Tokens | Context Latency (ms) | Model Latency (ms) | Total Latency (ms) | Error |
|---|---|---|---:|---:|---:|---:|---:|---:|---|
| claude-sonnet-4-6 | without_contextfusion | tiny_001 | ✓ | 946 | 2 | 0.0 | 2454.4 | 2454.4 |  |
| claude-sonnet-4-6 | with_contextfusion | tiny_001 | ✓ | 13 | 1 | 136.4 | 2153.4 | 2289.9 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_002 | ✓ | 947 | 3 | 0.0 | 12641.5 | 12641.5 |  |
| claude-sonnet-4-6 | with_contextfusion | tiny_002 | ✓ | 4 | 3 | 6.1 | 10152.2 | 10158.4 |  |
| claude-sonnet-4-6 | without_contextfusion | tiny_003 | ✓ | 948 | 2 | 0.1 | 10732.7 | 10732.8 |  |
| claude-sonnet-4-6 | with_contextfusion | tiny_003 | ✓ | 14 | 1 | 63.5 | 10778.3 | 10841.8 |  |

## Summary

| Mode | Runs | Success Rate | Avg Context Tokens | Avg Answer Tokens | Avg Context Latency (ms) | Avg Model Latency (ms) | Avg Total Latency (ms) | Errors |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| with_contextfusion | 3 | 100.0% | 10.3 | 1.7 | 68.7 | 7694.6 | 7763.3 | 0 |
| without_contextfusion | 3 | 100.0% | 947.0 | 2.3 | 0.0 | 8609.5 | 8609.6 | 0 |

## Notes

- Success means `expected_answer` appears in model output (case-insensitive).
- `with_contextfusion` uses pipeline-selected context under benchmark budget.
- `without_contextfusion` concatenates all candidate context directly.
