# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Type definitions for ContextFusion."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum, auto
from typing import Any, Literal, Protocol, TypeVar, runtime_checkable


class SourceType(Enum):
    """Types of content sources."""

    TEXT = auto()
    DOCUMENT = auto()
    STRUCTURED = auto()
    IMAGE = auto()
    CODE = auto()
    MEMORY = auto()
    RETRIEVAL = auto()
    TOOL_TRACE = auto()
    EXAMPLE = auto()


class RepresentationType(Enum):
    """Types of block representations."""

    FULL_TEXT = "full_text"
    BULLET_SUMMARY = "bullet_summary"
    STRUCTURED_JSON = "structured_json"
    EXTRACTED_FACTS = "extracted_facts"
    CITATION_POINTER = "citation_pointer"
    TABLE_SUMMARY = "table_summary"
    CODE_SIGNATURE_SUMMARY = "code_signature_summary"


@dataclass
class RawSegment:
    """A raw segment extracted from a file."""

    text: str
    metadata: dict[str, Any] = field(default_factory=dict)
    source_path: str = ""
    page_number: int | None = None
    row_number: int | None = None
    language: str | None = None
    image_caption: str | None = None
    bounding_box: tuple[float, float, float, float] | None = None


@dataclass
class ContextBlock:
    """A normalized context block."""

    id: str
    content: str
    source_type: SourceType
    file_path: str = ""
    page: int | None = None
    row: int | None = None
    language: str | None = None
    token_count: int = 0
    trust_score: float = 0.5
    freshness: float = 1.0
    retrieval_score: float = 0.0
    privacy_score: float = 0.0
    tags: list[str] = field(default_factory=list)
    timestamp: datetime = field(default_factory=datetime.utcnow)
    representations: dict[RepresentationType, str] = field(default_factory=dict)
    representation_tokens: dict[RepresentationType, int] = field(default_factory=dict)
    metadata: dict[str, Any] = field(default_factory=dict)

    def get_best_representation(self, max_tokens: int) -> tuple[str, int]:
        """Get the best representation that fits within token budget.

        Args:
            max_tokens: Maximum tokens allowed

        Returns:
            Tuple of (content, token_count)
        """
        from .constants import DEFAULT_REPRESENTATION_PRIORITY

        for rep_type_str in DEFAULT_REPRESENTATION_PRIORITY:
            rep_type = RepresentationType(rep_type_str)
            if rep_type in self.representations:
                tokens = self.representation_tokens.get(rep_type, self.token_count)
                if tokens <= max_tokens:
                    return self.representations[rep_type], tokens

        # Fall back to content if no representation fits
        return self.content, self.token_count


@dataclass
class FeatureVector:
    """Feature vector for scoring."""

    token_count: float
    source_type_score: float
    structure_score: float
    freshness: float
    trust: float
    retrieval: float
    diversity: float
    redundancy: float
    privacy_risk: float


@dataclass
class Scores:
    """Utility and risk scores."""

    utility: float
    risk: float


@dataclass
class BudgetAllocation:
    """Token budget allocation across categories."""

    instructions: int
    retrieval: int
    memory: int
    examples: int
    tool_trace: int
    output_reserve: int

    @property
    def total(self) -> int:
        """Total token budget."""
        return (
            self.instructions
            + self.retrieval
            + self.memory
            + self.examples
            + self.tool_trace
            + self.output_reserve
        )


@dataclass
class PortfolioSelection:
    """Selected context portfolio."""

    blocks: list[ContextBlock]
    representations_used: dict[str, RepresentationType]
    total_tokens: int
    expected_utility: float
    total_risk: float


@dataclass
class EvaluationResult:
    """Result of context evaluation."""

    quality: float
    token_cost: int
    latency_ms: float
    citations_retained: float
    reward: float


@dataclass
class AblationResult:
    """Result of ablation study."""

    block_id: str
    baseline_reward: float
    removed_reward: float
    delta: float
    representation_savings: dict[RepresentationType, int]


@dataclass
class ExecutionRecord:
    """Record of a context optimization execution."""

    id: str
    timestamp: datetime
    task_description: str
    budget_allocation: BudgetAllocation
    selected_blocks: list[str]
    evaluation_result: EvaluationResult | None
    ablation_results: list[AblationResult] = field(default_factory=list)


T = TypeVar("T")


@runtime_checkable
class Loader(Protocol):
    """Protocol for file loaders."""

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file."""
        ...

    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from the file."""
        ...


@runtime_checkable
class Collector(Protocol):
    """Protocol for context collectors."""

    def collect(self, query: str | None = None) -> list[ContextBlock]:
        """Collect context blocks."""
        ...


@runtime_checkable
class Provider(Protocol):
    """Protocol for LLM providers."""

    def generate(
        self,
        prompt: str,
        max_tokens: int | None = None,
        temperature: float = 0.7,
    ) -> str:
        """Generate a response from the LLM."""
        ...

    def count_tokens(self, text: str) -> int:
        """Count tokens in text."""
        ...
