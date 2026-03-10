# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Constants used throughout ContextFusion."""

from typing import Final

# Token budget categories
DEFAULT_INSTRUCTIONS_BUDGET: Final[int] = 1000
DEFAULT_RETRIEVAL_BUDGET: Final[int] = 3000
DEFAULT_MEMORY_BUDGET: Final[int] = 2000
DEFAULT_EXAMPLES_BUDGET: Final[int] = 1500
DEFAULT_TOOL_TRACE_BUDGET: Final[int] = 1000
DEFAULT_OUTPUT_RESERVE: Final[int] = 1000

# Default total budget
DEFAULT_TOTAL_BUDGET: Final[int] = 8000

# Token estimation constants
TOKENS_PER_CHARACTER: Final[float] = 0.25
DEFAULT_ENCODING: Final[str] = "cl100k_base"  # OpenAI's encoding

# File type mappings
TEXT_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".txt", ".log", ".md", ".markdown", ".rst"
})

DOCUMENT_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".pdf", ".docx", ".doc"
})

STRUCTURED_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".csv", ".tsv", ".json", ".jsonl", ".yaml", ".yml"
})

IMAGE_EXTENSIONS: Final[frozenset[str]] = frozenset({
    ".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".webp"
})

CODE_EXTENSIONS: Final[dict[str, str]] = {
    ".py": "python",
    ".js": "javascript",
    ".jsx": "javascript",
    ".ts": "typescript",
    ".tsx": "typescript",
    ".go": "go",
    ".rs": "rust",
    ".java": "java",
    ".c": "c",
    ".cpp": "cpp",
    ".cc": "cpp",
    ".h": "c",
    ".hpp": "cpp",
    ".cs": "csharp",
    ".rb": "ruby",
    ".php": "php",
    ".swift": "swift",
    ".kt": "kotlin",
    ".scala": "scala",
    ".r": "r",
    ".m": "objective-c",
    ".sh": "bash",
    ".bash": "bash",
    ".zsh": "zsh",
    ".ps1": "powershell",
    ".sql": "sql",
    ".html": "html",
    ".css": "css",
    ".scss": "scss",
    ".sass": "sass",
    ".less": "less",
    ".xml": "xml",
    ".toml": "toml",
    ".ini": "ini",
    ".cfg": "ini",
    ".conf": "ini",
}

# Scoring weights defaults
DEFAULT_UTILITY_WEIGHTS: Final[dict[str, float]] = {
    "retrieval": 0.25,
    "trust": 0.20,
    "freshness": 0.15,
    "structure": 0.15,
    "diversity": 0.15,
    "token_cost": -0.10,
}

DEFAULT_RISK_WEIGHTS: Final[dict[str, float]] = {
    "hallucination_proxy": 0.40,
    "staleness": 0.35,
    "privacy": 0.25,
}

# Evaluation reward weights
DEFAULT_REWARD_WEIGHTS: Final[dict[str, float]] = {
    "alpha": 1.0,  # quality
    "beta": 0.1,   # cost
    "gamma": 0.01, # latency
    "delta": 0.5,  # risk
}

# Cache directories
DEFAULT_CACHE_DIR: Final[str] = ".cpo_cache"
DEFAULT_MEMORY_DIR: Final[str] = ".cpo_memory"
DEFAULT_TELEMETRY_DIR: Final[str] = ".cpo_telemetry"

# Time constants
SECONDS_PER_DAY: Final[int] = 86400
DEFAULT_FRESHNESS_HALFLIFE_DAYS: Final[int] = 30

# Representation types
REPRESENTATION_TYPES: Final[frozenset[str]] = frozenset({
    "full_text",
    "bullet_summary",
    "structured_json",
    "extracted_facts",
    "citation_pointer",
    "table_summary",
    "code_signature_summary",
})

# Default representation priorities
DEFAULT_REPRESENTATION_PRIORITY: Final[list[str]] = [
    "citation_pointer",
    "bullet_summary",
    "code_signature_summary",
    "table_summary",
    "extracted_facts",
    "structured_json",
    "full_text",
]
