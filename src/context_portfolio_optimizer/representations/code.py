# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025-2026 Rohan R @rotsl

"""Code-oriented compact representations."""

from __future__ import annotations

import re
from typing import Any

_SIGNATURE_RE = re.compile(r"^\s*(def|class|function|interface)\s+.+", re.MULTILINE)
_IMPORT_RE = re.compile(r"^\s*(import\s+.+|from\s+.+\s+import\s+.+)", re.MULTILINE)
_DOCSTRING_RE = re.compile(r'"""(.*?)"""|\'\'\'(.*?)\'\'\'', re.DOTALL)


def generate_code_variants(block: Any) -> list[dict[str, Any]]:
    """Generate code-specific compact variants."""
    content = str(block.content)

    signature_lines = _extract_lines(_SIGNATURE_RE, content)
    import_lines = _extract_lines(_IMPORT_RE, content)

    doc_match = _DOCSTRING_RE.search(content)
    docstring = ""
    if doc_match:
        docstring = (doc_match.group(1) or doc_match.group(2) or "").strip()

    changed_region = "\n".join(content.splitlines()[:30])
    dependency_summary = ", ".join(sorted(_module_names(import_lines)))

    return [
        {
            "representation_type": "signature_only",
            "text": "\n".join(signature_lines),
            "generation_cost": 0.2,
            "suitability_tags": ["code", "debug"],
        },
        {
            "representation_type": "docstring_only",
            "text": docstring,
            "generation_cost": 0.15,
            "suitability_tags": ["code", "intent"],
        },
        {
            "representation_type": "changed_region",
            "text": changed_region,
            "generation_cost": 0.05,
            "suitability_tags": ["code", "diff"],
        },
        {
            "representation_type": "imports_plus_signature",
            "text": "\n".join(import_lines + signature_lines[:20]),
            "generation_cost": 0.25,
            "suitability_tags": ["code", "dependency"],
        },
        {
            "representation_type": "dependency_summary",
            "text": dependency_summary,
            "generation_cost": 0.15,
            "suitability_tags": ["code", "summary"],
        },
    ]


def _extract_lines(pattern: re.Pattern[str], content: str) -> list[str]:
    return [line.strip() for line in content.splitlines() if pattern.match(line)]


def _module_names(import_lines: list[str]) -> set[str]:
    modules: set[str] = set()
    for line in import_lines:
        if line.startswith("import "):
            for module in line.replace("import", "", 1).split(","):
                modules.add(module.strip().split(" as ")[0])
        elif line.startswith("from "):
            modules.add(line.split()[1])
    return modules
