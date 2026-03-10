# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Utility scoring model for ContextFusion."""

from ..constants import DEFAULT_UTILITY_WEIGHTS
from ..settings import get_settings
from ..types import ContextBlock, FeatureVector


class UtilityModel:
    """Computes utility scores for context blocks."""

    def __init__(self, weights: dict[str, float] | None = None):
        """Initialize utility model.

        Args:
            weights: Optional custom weights
        """
        if weights is None:
            # Try to load from settings
            settings = get_settings()
            weights = settings.scoring.utility_weights

        self.weights = {**DEFAULT_UTILITY_WEIGHTS, **weights}

    def score(self, features: FeatureVector) -> float:
        """Compute utility score from features.

        Args:
            features: Feature vector

        Returns:
            Utility score (can be negative)
        """
        score = (
            self.weights["retrieval"] * features.retrieval
            + self.weights["trust"] * features.trust
            + self.weights["freshness"] * features.freshness
            + self.weights["structure"] * features.structure_score
            + self.weights["diversity"] * features.diversity
            + self.weights["token_cost"] * features.token_count
        )

        return score

    def score_block(
        self,
        block: ContextBlock,
        features: FeatureVector | None = None,
        feature_extractor=None,
    ) -> float:
        """Compute utility score for a block.

        Args:
            block: Context block
            features: Optional pre-computed features
            feature_extractor: Optional feature extractor

        Returns:
            Utility score
        """
        if features is None:
            if feature_extractor is None:
                from .features import FeatureExtractor
                feature_extractor = FeatureExtractor()
            features = feature_extractor.extract(block)

        return self.score(features)

    def score_blocks(
        self,
        blocks: list[ContextBlock],
        feature_extractor=None,
    ) -> dict[str, float]:
        """Compute utility scores for multiple blocks.

        Args:
            blocks: List of context blocks
            feature_extractor: Optional feature extractor

        Returns:
            Dictionary mapping block IDs to scores
        """
        if feature_extractor is None:
            from .features import FeatureExtractor
            feature_extractor = FeatureExtractor()

        features_list = feature_extractor.extract_batch(blocks)

        scores = {}
        for block, features in zip(blocks, features_list):
            scores[block.id] = self.score(features)

        return scores

    def get_utility_per_token(self, features: FeatureVector) -> float:
        """Compute utility per token (efficiency metric).

        Args:
            features: Feature vector

        Returns:
            Utility per token
        """
        utility = self.score(features)
        tokens = max(1, features.token_count)
        return utility / tokens

    def update_weights(self, weights: dict[str, float]) -> None:
        """Update model weights.

        Args:
            weights: New weights dictionary
        """
        self.weights.update(weights)
