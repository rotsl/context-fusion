# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Representation generation system for ContextFusion."""

from .base_representation import BaseRepresentation, RepresentationGenerator
from .bullet_summary import BulletSummaryRepresentation
from .citation_pointer import CitationPointerRepresentation
from .code_signature_summary import CodeSignatureRepresentation
from .extracted_facts import ExtractedFactsRepresentation
from .full_text import FullTextRepresentation
from .structured_json import StructuredJsonRepresentation
from .table_summary import TableSummaryRepresentation

__all__ = [
    "BaseRepresentation",
    "RepresentationGenerator",
    "FullTextRepresentation",
    "BulletSummaryRepresentation",
    "StructuredJsonRepresentation",
    "ExtractedFactsRepresentation",
    "CitationPointerRepresentation",
    "TableSummaryRepresentation",
    "CodeSignatureRepresentation",
]
