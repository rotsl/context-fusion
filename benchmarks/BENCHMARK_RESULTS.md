# Benchmark Results

Comparison: **ContextFusion** vs **Without ContextFusion**

- Generated at: `2026-03-10 13:54:58Z`
- Budget used (ContextFusion): `120` tokens
- Dataset: `benchmarks/datasets/tiny_tasks.jsonl`

## Per-task Results

| Task | With CF Success | With CF Tokens | Without CF Success | Without CF Tokens | Token Reduction |
|---|---:|---:|---:|---:|---:|
| tiny_001 | ✓ | 40 | ✓ | 98 | 59.2% |
| tiny_002 | ✓ | 48 | ✓ | 99 | 51.5% |
| tiny_003 | ✓ | 41 | ✓ | 100 | 59.0% |

## Summary

- With ContextFusion success rate: **100.0%**
- Without ContextFusion success rate: **100.0%**
- Avg tokens with ContextFusion: **43.0**
- Avg tokens without ContextFusion: **99.0**
- Avg token reduction: **56.6%**
- Avg latency with ContextFusion: **34.1 ms**
- Avg latency without ContextFusion: **0.003 ms**

## Notes

- This tiny benchmark is deterministic and local-only.
- It measures context-selection efficiency and expected-answer retention in context.
- It does not call external LLM APIs.
