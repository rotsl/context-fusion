# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Feature extraction for context block scoring."""

from typing import Any

import numpy as np

from ..types import ContextBlock, FeatureVector
from ..utils.similarity import text_similarity


class FeatureExtractor:
    """Extracts features from context blocks for scoring."""

    def __init__(self):
        self._block_history: list[ContextBlock] = []

    def extract(
        self, block: ContextBlock, all_blocks: list[ContextBlock] | None = None
    ) -> FeatureVector:
        """Extract features from a context block.

        Args:
            block: Context block to extract features from
            all_blocks: Optional list of all blocks for computing diversity

        Returns:
            Feature vector
        """
        if all_blocks is None:
            all_blocks = []

        features = FeatureVector(
            token_count=float(block.token_count),
            source_type_score=self._source_type_score(block),
            structure_score=self._structure_score(block),
            freshness=block.freshness,
            trust=block.trust_score,
            retrieval=block.retrieval_score,
            diversity=self._diversity_score(block, all_blocks),
            redundancy=self._redundancy_score(block, all_blocks),
            privacy_risk=block.privacy_score,
        )

        return features

    def extract_batch(
        self,
        blocks: list[ContextBlock],
    ) -> list[FeatureVector]:
        """Extract features from multiple blocks.

        Args:
            blocks: List of context blocks

        Returns:
            List of feature vectors
        """
        return [self.extract(block, blocks) for block in blocks]

    def to_array(self, features: FeatureVector) -> np.ndarray:
        """Convert feature vector to numpy array.

        Args:
            features: Feature vector

        Returns:
            Numpy array
        """
        return np.array(
            [
                features.token_count,
                features.source_type_score,
                features.structure_score,
                features.freshness,
                features.trust,
                features.retrieval,
                features.diversity,
                features.redundancy,
                features.privacy_risk,
            ]
        )

    def _source_type_score(self, block: ContextBlock) -> float:
        """Compute source type quality score.

        Args:
            block: Context block

        Returns:
            Source type score (0-1)
        """
        # Prefer certain source types
        type_scores = {
            "CODE": 0.9,
            "DOCUMENT": 0.8,
            "STRUCTURED": 0.8,
            "TEXT": 0.7,
            "IMAGE": 0.6,
            "MEMORY": 0.7,
            "RETRIEVAL": 0.8,
            "TOOL_TRACE": 0.6,
            "EXAMPLE": 0.9,
        }
        return type_scores.get(block.source_type.name, 0.5)

    def _structure_score(self, block: ContextBlock) -> float:
        """Compute structure quality score.

        Args:
            block: Context block

        Returns:
            Structure score (0-1)
        """
        score = 0.5  # Base score

        # Boost for structured metadata
        if block.metadata:
            if block.metadata.get("is_heading"):
                score += 0.2
            if block.metadata.get("is_table"):
                score += 0.15
            if block.metadata.get("type") in ("function", "class"):
                score += 0.25

        # Boost for tags
        if block.tags:
            score += min(0.1, len(block.tags) * 0.02)

        return min(1.0, score)

    def _diversity_score(self, block: ContextBlock, all_blocks: list[ContextBlock]) -> float:
        """Compute diversity score (how different from other blocks).

        Args:
            block: Context block
            all_blocks: All blocks in the set

        Returns:
            Diversity score (0-1, higher is more diverse)
        """
        if not all_blocks or len(all_blocks) <= 1:
            return 1.0

        # Compute average similarity to other blocks
        similarities = []
        for other in all_blocks:
            if other.id != block.id:
                sim = text_similarity(block.content, other.content)
                similarities.append(sim)

        if not similarities:
            return 1.0

        avg_similarity = sum(similarities) / len(similarities)

        # Diversity is inverse of similarity
        return 1.0 - avg_similarity

    def _redundancy_score(self, block: ContextBlock, all_blocks: list[ContextBlock]) -> float:
        """Compute redundancy score (how much content is repeated).

        Args:
            block: Context block
            all_blocks: All blocks in the set

        Returns:
            Redundancy score (0-1, higher is more redundant)
        """
        if not all_blocks or len(all_blocks) <= 1:
            return 0.0

        # Find maximum similarity to any other block
        max_similarity = 0.0
        for other in all_blocks:
            if other.id != block.id:
                sim = text_similarity(block.content, other.content)
                max_similarity = max(max_similarity, sim)

        return max_similarity

    def normalize_features(self, features_list: list[FeatureVector]) -> list[FeatureVector]:
        """Normalize feature vectors.

        Args:
            features_list: List of feature vectors

        Returns:
            Normalized feature vectors
        """
        if not features_list:
            return []

        # Convert to arrays
        arrays = [self.to_array(f) for f in features_list]
        matrix = np.array(arrays)

        # Normalize each column
        for i in range(matrix.shape[1]):
            col = matrix[:, i]
            min_val = col.min()
            max_val = col.max()
            if max_val > min_val:
                matrix[:, i] = (col - min_val) / (max_val - min_val)

        # Convert back to FeatureVectors
        normalized = []
        for row in matrix:
            normalized.append(
                FeatureVector(
                    token_count=row[0],
                    source_type_score=row[1],
                    structure_score=row[2],
                    freshness=row[3],
                    trust=row[4],
                    retrieval=row[5],
                    diversity=row[6],
                    redundancy=row[7],
                    privacy_risk=row[8],
                )
            )

        return normalized
