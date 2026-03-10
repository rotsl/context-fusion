# Benchmark Results

Comparison: **ContextFusion** vs **Without ContextFusion**

- Generated at: `2026-03-10 16:10:19Z`
- Budget used (ContextFusion): `120` tokens
- Dataset: `benchmarks/datasets/tiny_tasks.jsonl`

## Per-task Results

| Task | With CF Success | With CF Tokens | Without CF Success | Without CF Tokens | Token Reduction |
|---|---:|---:|---:|---:|---:|
| tiny_001 | ✓ | 34 | ✓ | 98 | 65.3% |
| tiny_002 | ✓ | 35 | ✓ | 99 | 64.6% |
| tiny_003 | ✓ | 35 | ✓ | 100 | 65.0% |

## Summary

- With ContextFusion success rate: **100.0%**
- Without ContextFusion success rate: **100.0%**
- Avg tokens with ContextFusion: **34.7**
- Avg tokens without ContextFusion: **99.0**
- Avg token reduction: **65.0%**
- Avg latency with ContextFusion: **86.5 ms**
- Avg latency without ContextFusion: **0.017 ms**

## Notes

- This tiny benchmark is deterministic and local-only.
- It measures context-selection efficiency and expected-answer retention in context.
- It does not call external LLM APIs.
