# Algorithm

## Context Optimization as Knapsack Problem

ContextFusion treats context selection as a constrained optimization problem:

### Objective

```
maximize Σ((utility_i − risk_i) * z_i)

subject to:
    Σ(token_i * z_i) ≤ token_budget
    z_i ∈ {0, 1}
```

Where:
- `utility_i`: Utility score of block i
- `risk_i`: Risk score of block i
- `token_i`: Token count of block i
- `z_i`: Binary selection variable

### Utility Score

```
utility = w₁·retrieval + w₂·trust + w₃·freshness + w₄·structure + w₅·diversity − w₆·token_cost
```

Default weights:
- `w₁ = 0.25` (retrieval)
- `w₂ = 0.20` (trust)
- `w₃ = 0.15` (freshness)
- `w₄ = 0.15` (structure)
- `w₅ = 0.15` (diversity)
- `w₆ = 0.10` (token cost, negative)

### Risk Score

```
risk = r₁·hallucination_proxy + r₂·staleness + r₃·privacy
```

Default weights:
- `r₁ = 0.40` (hallucination proxy)
- `r₂ = 0.35` (staleness)
- `r₃ = 0.25` (privacy)

### Representation Selection

Each block may have multiple representations. The optimizer selects:
1. Which blocks to include
2. Which representation to use for each selected block

The representation with highest utility per token is preferred.

## Knapsack Solvers

### Greedy Algorithm

Sorts items by value density (value/tokens) and selects until budget exhausted.

**Time complexity**: O(n log n)

### Dynamic Programming

Builds DP table for optimal solution.

**Time complexity**: O(n × budget)

**Space complexity**: O(budget)

Used when n ≤ 100 and budget ≤ 10000.

## Reward Function

For evaluation:

```
reward = α·quality − β·cost − γ·latency − δ·risk
```

Default weights:
- `α = 1.0` (quality)
- `β = 0.1` (cost)
- `γ = 0.01` (latency)
- `δ = 0.5` (risk)
