# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Code file loader for ContextFusion."""

import re
from pathlib import Path

from ..constants import CODE_EXTENSIONS
from ..logging_utils import get_logger
from ..types import RawSegment
from .base_loader import BaseLoader

logger = get_logger("code_loader")


class CodeLoader(BaseLoader):
    """Loader for source code files."""

    def __init__(self):
        self._tree_sitter_available = None

    def _check_tree_sitter(self) -> bool:
        """Check if tree-sitter is available."""
        if self._tree_sitter_available is None:
            try:
                from tree_sitter import Language, Parser

                self._tree_sitter_available = True
            except ImportError:
                self._tree_sitter_available = False
                logger.debug("tree-sitter not installed, using regex-based parsing")
        return self._tree_sitter_available

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is a recognized code file
        """
        ext = self._get_extension(file_path)
        return ext in CODE_EXTENSIONS

    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from a code file.

        Args:
            file_path: Path to the code file

        Returns:
            List of raw segments (functions, classes, imports, etc.)
        """
        language = self._detect_language(file_path)
        text = self._read_text(file_path)

        if self._check_tree_sitter():
            return self._parse_with_tree_sitter(file_path, text, language)
        else:
            return self._parse_with_regex(file_path, text, language)

    def _detect_language(self, file_path: str) -> str:
        """Detect programming language from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Language name
        """
        ext = self._get_extension(file_path)
        return CODE_EXTENSIONS.get(ext, "unknown")

    def _parse_with_tree_sitter(
        self,
        file_path: str,
        text: str,
        language: str,
    ) -> list[RawSegment]:
        """Parse code using tree-sitter."""
        segments = []

        try:
            from tree_sitter import Language, Parser

            # Try to load language grammar
            language_module = self._get_language_module(language)
            if language_module:
                parser = Parser()
                parser.set_language(language_module)

                tree = parser.parse(bytes(text, "utf8"))
                root_node = tree.root_node

                # Extract functions and classes
                for node in root_node.children:
                    if node.type in ("function_definition", "function_declaration"):
                        segment_text = text[node.start_byte : node.end_byte]
                        name = self._extract_node_name(node, text)
                        segments.append(
                            RawSegment(
                                text=segment_text,
                                metadata={
                                    "type": "function",
                                    "name": name,
                                    "language": language,
                                },
                                source_path=file_path,
                                language=language,
                            )
                        )
                    elif node.type in ("class_definition", "class_declaration"):
                        segment_text = text[node.start_byte : node.end_byte]
                        name = self._extract_node_name(node, text)
                        segments.append(
                            RawSegment(
                                text=segment_text,
                                metadata={
                                    "type": "class",
                                    "name": name,
                                    "language": language,
                                },
                                source_path=file_path,
                                language=language,
                            )
                        )

                # If no segments found, add entire file
                if not segments:
                    segments.append(
                        RawSegment(
                            text=text,
                            metadata={"type": "file", "language": language},
                            source_path=file_path,
                            language=language,
                        )
                    )
            else:
                # Fallback to regex
                return self._parse_with_regex(file_path, text, language)

        except Exception as e:
            logger.debug(f"Tree-sitter parsing failed: {e}, using regex fallback")
            return self._parse_with_regex(file_path, text, language)

        return segments

    def _get_language_module(self, language: str):
        """Get tree-sitter language module."""
        try:
            from tree_sitter import Language

            # Map language names to modules
            module_map = {
                "python": "tree_sitter_python",
                "javascript": "tree_sitter_javascript",
                "typescript": "tree_sitter_typescript",
                "go": "tree_sitter_go",
                "rust": "tree_sitter_rust",
                "java": "tree_sitter_java",
                "c": "tree_sitter_c",
                "cpp": "tree_sitter_cpp",
            }

            module_name = module_map.get(language)
            if module_name:
                module = __import__(module_name)
                return Language(module.language())
        except Exception as e:
            logger.debug(f"Could not load language module for {language}: {e}")

        return None

    def _extract_node_name(self, node, text: str) -> str:
        """Extract name from a node."""
        for child in node.children:
            if "identifier" in child.type or child.type == "name":
                return text[child.start_byte : child.end_byte]
        return "unknown"

    def _parse_with_regex(
        self,
        file_path: str,
        text: str,
        language: str,
    ) -> list[RawSegment]:
        """Parse code using regex patterns."""
        segments = []

        # Extract docstrings/comments
        docstring_pattern = r'("""[\s\S]*?"""|\'\'\'[\s\S]*?\'\'\'|"[^"]*"|\'[^\']*\')'
        docstrings = re.findall(docstring_pattern, text)

        for i, docstring in enumerate(docstrings):
            segments.append(
                RawSegment(
                    text=docstring,
                    metadata={
                        "type": "docstring",
                        "index": i,
                        "language": language,
                    },
                    source_path=file_path,
                    language=language,
                )
            )

        # Extract imports
        import_patterns = [
            r"^(import\s+.+)$",
            r"^(from\s+\S+\s+import\s+.+)$",
            r"^(require\s*\(.+\))$",
            r"^(const\s+.+\s+=\s+require\s*\(.+\))$",
            r"^(#include\s+.+)$",
        ]

        for pattern in import_patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                segments.append(
                    RawSegment(
                        text=match.group(1),
                        metadata={"type": "import", "language": language},
                        source_path=file_path,
                        language=language,
                    )
                )

        # Extract function signatures
        func_patterns = [
            r"^(def\s+(\w+)\s*\([^)]*\).*:)$",
            r"^(function\s+(\w+)\s*\([^)]*\).*)$",
            r"^((\w+)\s*\([^)]*\)\s*\{[^}]*\})$",
        ]

        for pattern in func_patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                segments.append(
                    RawSegment(
                        text=match.group(1),
                        metadata={
                            "type": "function_signature",
                            "name": match.group(2),
                            "language": language,
                        },
                        source_path=file_path,
                        language=language,
                    )
                )

        # Add entire file as fallback
        if not segments:
            segments.append(
                RawSegment(
                    text=text,
                    metadata={"type": "file", "language": language},
                    source_path=file_path,
                    language=language,
                )
            )

        return segments
