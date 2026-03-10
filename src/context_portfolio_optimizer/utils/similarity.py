# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Similarity computation utilities for ContextFusion."""

import math
from collections import Counter


def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
    """Compute cosine similarity between two vectors.

    Args:
        vec1: First vector
        vec2: Second vector

    Returns:
        Cosine similarity in range [-1, 1]
    """
    if len(vec1) != len(vec2):
        raise ValueError("Vectors must have same length")

    if not vec1:
        return 0.0

    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm1 = math.sqrt(sum(a * a for a in vec1))
    norm2 = math.sqrt(sum(b * b for b in vec2))

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


def jaccard_similarity(set1: set, set2: set) -> float:
    """Compute Jaccard similarity between two sets.

    Args:
        set1: First set
        set2: Second set

    Returns:
        Jaccard similarity in range [0, 1]
    """
    if not set1 and not set2:
        return 1.0

    intersection = len(set1 & set2)
    union = len(set1 | set2)

    if union == 0:
        return 0.0

    return intersection / union


def text_similarity(text1: str, text2: str) -> float:
    """Compute similarity between two texts using word overlap.

    Args:
        text1: First text
        text2: Second text

    Returns:
        Similarity in range [0, 1]
    """
    if not text1 or not text2:
        return 0.0

    # Tokenize
    words1 = set(text1.lower().split())
    words2 = set(text2.lower().split())

    return jaccard_similarity(words1, words2)


def ngram_similarity(text1: str, text2: str, n: int = 2) -> float:
    """Compute n-gram similarity between two texts.

    Args:
        text1: First text
        text2: Second text
        n: N-gram size

    Returns:
        Similarity in range [0, 1]
    """
    if not text1 or not text2:
        return 0.0

    def get_ngrams(text: str, n: int) -> set:
        text = text.lower().replace(" ", "")
        return set(text[i : i + n] for i in range(len(text) - n + 1))

    ngrams1 = get_ngrams(text1, n)
    ngrams2 = get_ngrams(text2, n)

    return jaccard_similarity(ngrams1, ngrams2)


def tfidf_similarity(
    text1: str,
    text2: str,
    idf: dict[str, float] | None = None,
) -> float:
    """Compute TF-IDF similarity between two texts.

    Args:
        text1: First text
        text2: Second text
        idf: Optional IDF weights

    Returns:
        Similarity in range [0, 1]
    """
    if not text1 or not text2:
        return 0.0

    # Tokenize
    words1 = text1.lower().split()
    words2 = text2.lower().split()

    # Compute TF
    tf1 = Counter(words1)
    tf2 = Counter(words2)

    # Get all unique words
    all_words = set(tf1.keys()) | set(tf2.keys())

    # Use uniform IDF if not provided
    if idf is None:
        idf = {w: 1.0 for w in all_words}

    # Compute TF-IDF vectors
    vec1 = [tf1.get(w, 0) * idf.get(w, 1.0) for w in all_words]
    vec2 = [tf2.get(w, 0) * idf.get(w, 1.0) for w in all_words]

    return cosine_similarity(vec1, vec2)
