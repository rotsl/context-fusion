# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""YAML I/O utilities for ContextFusion."""

from pathlib import Path
from typing import Any

import yaml


def load_yaml(path: str | Path) -> Any:
    """Load YAML from file.

    Args:
        path: Path to YAML file

    Returns:
        Parsed YAML data
    """
    path = Path(path)
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def save_yaml(path: str | Path, data: Any) -> None:
    """Save data to YAML file.

    Args:
        path: Path to output file
        data: Data to save
    """
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        yaml.dump(data, f, default_flow_style=False, allow_unicode=True, sort_keys=False)
