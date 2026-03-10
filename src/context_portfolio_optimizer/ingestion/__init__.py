# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Ingestion system for ContextFusion."""

from .base_loader import BaseLoader
from .code_loader import CodeLoader
from .csv_loader import CSVLoader
from .dispatcher import IngestionDispatcher
from .docx_loader import DocxLoader
from .image_loader import ImageLoader
from .json_loader import JSONLoader
from .markdown_loader import MarkdownLoader
from .pdf_loader import PDFLoader
from .text_loader import TextLoader

__all__ = [
    "BaseLoader",
    "IngestionDispatcher",
    "TextLoader",
    "PDFLoader",
    "DocxLoader",
    "CSVLoader",
    "JSONLoader",
    "MarkdownLoader",
    "ImageLoader",
    "CodeLoader",
]
