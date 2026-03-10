# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Hashing utilities for ContextFusion."""

import hashlib
import uuid
from pathlib import Path


def compute_hash(text: str, algorithm: str = "sha256") -> str:
    """Compute hash of text.

    Args:
        text: Input text
        algorithm: Hash algorithm (sha256, md5, sha1)

    Returns:
        Hex digest of hash
    """
    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    hasher.update(text.encode("utf-8"))
    return hasher.hexdigest()


def compute_file_hash(file_path: str | Path, algorithm: str = "sha256") -> str:
    """Compute hash of file contents.

    Args:
        file_path: Path to file
        algorithm: Hash algorithm

    Returns:
        Hex digest of hash
    """
    file_path = Path(file_path)

    if algorithm == "sha256":
        hasher = hashlib.sha256()
    elif algorithm == "md5":
        hasher = hashlib.md5()
    elif algorithm == "sha1":
        hasher = hashlib.sha1()
    else:
        raise ValueError(f"Unsupported algorithm: {algorithm}")

    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            hasher.update(chunk)

    return hasher.hexdigest()


def compute_id(text: str, prefix: str = "") -> str:
    """Compute a unique ID from text.

    Args:
        text: Input text
        prefix: Optional prefix for the ID

    Returns:
        Unique ID string
    """
    hash_part = compute_hash(text, "md5")[:12]
    if prefix:
        return f"{prefix}_{hash_part}"
    return hash_part


def generate_uuid() -> str:
    """Generate a random UUID.

    Returns:
        UUID string
    """
    return str(uuid.uuid4())


def short_hash(text: str, length: int = 8) -> str:
    """Compute a short hash of text.

    Args:
        text: Input text
        length: Length of hash to return

    Returns:
        Short hex digest
    """
    return compute_hash(text, "md5")[:length]
