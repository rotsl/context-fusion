# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Custom exceptions for ContextFusion."""


class ContextFusionError(Exception):
    """Base exception for all ContextFusion errors."""

    pass


class IngestionError(ContextFusionError):
    """Error during data ingestion."""

    pass


class LoaderNotFoundError(IngestionError):
    """No loader found for file type."""

    pass


class LoadError(IngestionError):
    """Error loading a specific file."""

    pass


class NormalizationError(ContextFusionError):
    """Error during block normalization."""

    pass


class RepresentationError(ContextFusionError):
    """Error during representation generation."""

    pass


class ScoringError(ContextFusionError):
    """Error during scoring."""

    pass


class AllocationError(ContextFusionError):
    """Error during budget allocation."""

    pass


class KnapsackError(AllocationError):
    """Error in knapsack optimization."""

    pass


class BudgetExceededError(AllocationError):
    """Token budget exceeded."""

    pass


class MemoryError(ContextFusionError):
    """Error in memory operations."""

    pass


class ProviderError(ContextFusionError):
    """Error from LLM provider."""

    pass


class ConfigurationError(ContextFusionError):
    """Error in configuration."""

    pass


class ValidationError(ContextFusionError):
    """Error in data validation."""

    pass


class EvaluationError(ContextFusionError):
    """Error during evaluation."""

    pass


class AblationError(ContextFusionError):
    """Error during ablation study."""

    pass
