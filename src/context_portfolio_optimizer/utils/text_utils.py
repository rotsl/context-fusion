# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Text processing utilities for ContextFusion."""

import re
from collections import Counter


def clean_text(text: str) -> str:
    """Clean and normalize text.

    Args:
        text: Input text

    Returns:
        Cleaned text
    """
    if not text:
        return ""

    # Normalize whitespace
    text = re.sub(r"\s+", " ", text)

    # Remove control characters
    text = re.sub(r"[\x00-\x08\x0b-\x0c\x0e-\x1f]", "", text)

    # Strip whitespace
    text = text.strip()

    return text


def truncate_text(text: str, max_length: int, suffix: str = "...") -> str:
    """Truncate text to maximum length.

    Args:
        text: Input text
        max_length: Maximum length
        suffix: Suffix to add if truncated

    Returns:
        Truncated text
    """
    if len(text) <= max_length:
        return text

    return text[: max_length - len(suffix)] + suffix


def extract_keywords(text: str, top_n: int = 10, min_length: int = 3) -> list[str]:
    """Extract keywords from text using simple frequency.

    Args:
        text: Input text
        top_n: Number of top keywords to return
        min_length: Minimum keyword length

    Returns:
        List of keywords
    """
    if not text:
        return []

    # Simple word extraction
    words = re.findall(r"\b[a-zA-Z]+\b", text.lower())

    # Filter by length and common stop words
    stop_words = {
        "the", "a", "an", "is", "are", "was", "were", "be", "been",
        "being", "have", "has", "had", "do", "does", "did", "will",
        "would", "could", "should", "may", "might", "must", "shall",
        "can", "need", "dare", "ought", "used", "to", "of", "in",
        "for", "on", "with", "at", "by", "from", "as", "into",
        "through", "during", "before", "after", "above", "below",
        "between", "under", "and", "but", "or", "yet", "so", "if",
        "because", "although", "though", "while", "where", "when",
        "that", "which", "who", "whom", "whose", "what", "this",
        "these", "those", "i", "you", "he", "she", "it", "we", "they",
    }

    filtered = [w for w in words if len(w) >= min_length and w not in stop_words]

    # Count and return top N
    counter = Counter(filtered)
    return [word for word, _ in counter.most_common(top_n)]


def split_paragraphs(text: str) -> list[str]:
    """Split text into paragraphs.

    Args:
        text: Input text

    Returns:
        List of paragraphs
    """
    if not text:
        return []

    # Split on multiple newlines
    paragraphs = re.split(r"\n\s*\n", text)

    # Clean and filter
    return [clean_text(p) for p in paragraphs if clean_text(p)]


def split_sentences(text: str) -> list[str]:
    """Split text into sentences.

    Args:
        text: Input text

    Returns:
        List of sentences
    """
    if not text:
        return []

    # Simple sentence splitting
    sentences = re.split(r"(?<=[.!?])\s+", text)

    # Clean and filter
    return [clean_text(s) for s in sentences if clean_text(s)]


def normalize_whitespace(text: str) -> str:
    """Normalize whitespace in text.

    Args:
        text: Input text

    Returns:
        Normalized text
    """
    return re.sub(r"\s+", " ", text).strip()


def remove_html_tags(text: str) -> str:
    """Remove HTML tags from text.

    Args:
        text: Input text

    Returns:
        Text without HTML tags
    """
    return re.sub(r"<[^>]+>", "", text)


def escape_special_chars(text: str) -> str:
    """Escape special characters for safe display.

    Args:
        text: Input text

    Returns:
        Escaped text
    """
    # Escape backslashes first
    text = text.replace("\\", "\\\\")
    # Escape other special chars
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    text = text.replace("\t", "\\t")
    text = text.replace('"', '\\"')
    return text
