# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Risk scoring model for ContextFusion."""

from ..constants import DEFAULT_RISK_WEIGHTS
from ..settings import get_settings
from ..types import ContextBlock, FeatureVector


class RiskModel:
    """Computes risk scores for context blocks."""

    def __init__(self, weights: dict[str, float] | None = None):
        """Initialize risk model.

        Args:
            weights: Optional custom weights
        """
        if weights is None:
            settings = get_settings()
            weights = settings.scoring.risk_weights

        self.weights = {**DEFAULT_RISK_WEIGHTS, **weights}

    def score(self, features: FeatureVector) -> float:
        """Compute risk score from features.

        Args:
            features: Feature vector

        Returns:
            Risk score (0-1, higher is riskier)
        """
        # Hallucination proxy: based on low trust and high redundancy
        hallucination_proxy = (1 - features.trust) * 0.5 + features.redundancy * 0.5

        # Staleness: inverse of freshness
        staleness = 1 - features.freshness

        # Privacy: already in features
        privacy = features.privacy_risk

        score = (
            self.weights["hallucination_proxy"] * hallucination_proxy
            + self.weights["staleness"] * staleness
            + self.weights["privacy"] * privacy
        )

        return min(1.0, max(0.0, score))

    def score_block(
        self,
        block: ContextBlock,
        features: FeatureVector | None = None,
        feature_extractor=None,
    ) -> float:
        """Compute risk score for a block.

        Args:
            block: Context block
            features: Optional pre-computed features
            feature_extractor: Optional feature extractor

        Returns:
            Risk score
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
        """Compute risk scores for multiple blocks.

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

    def is_high_risk(self, features: FeatureVector, threshold: float = 0.7) -> bool:
        """Check if features indicate high risk.

        Args:
            features: Feature vector
            threshold: Risk threshold

        Returns:
            True if high risk
        """
        return self.score(features) >= threshold

    def update_weights(self, weights: dict[str, float]) -> None:
        """Update model weights.

        Args:
            weights: New weights dictionary
        """
        self.weights.update(weights)
