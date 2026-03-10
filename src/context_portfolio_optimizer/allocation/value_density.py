# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Value-density helpers for token-budget planning."""


def compute_value_density(utility: float, risk: float, tokens: int) -> float:
    """Compute utility-minus-risk value per token."""
    return (utility - risk) / max(tokens, 1)
