# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Code signature summary representation for ContextFusion."""

import re

from ..types import ContextBlock, RepresentationType
from .base_representation import BaseRepresentation


class CodeSignatureRepresentation(BaseRepresentation):
    """Code signature summary representation."""

    @property
    def representation_type(self) -> RepresentationType:
        return RepresentationType.CODE_SIGNATURE_SUMMARY

    # Patterns for extracting signatures
    FUNCTION_PATTERNS = [
        r"(?:def|function)\s+(\w+)\s*\(([^)]*)\)",
        r"(?:async\s+)?def\s+(\w+)\s*\(([^)]*)\)",
        r"(\w+)\s*:\s*function\s*\(([^)]*)\)",
    ]

    CLASS_PATTERNS = [
        r"class\s+(\w+)(?:\(([^)]*)\))?:",
        r"class\s+(\w+)(?:\s+extends\s+(\w+))?:",
    ]

    def generate(self, block: ContextBlock) -> str:
        """Generate code signature summary.

        Args:
            block: Context block

        Returns:
            Code signature summary
        """
        content = block.content
        language = block.language or "unknown"

        signatures = []

        # Extract function signatures
        functions = self._extract_functions(content)
        for func_name, params in functions:
            sig = f"{language} function {func_name}({params})"
            signatures.append(sig)

        # Extract class signatures
        classes = self._extract_classes(content)
        for class_name, parent in classes:
            if parent:
                sig = f"{language} class {class_name}({parent})"
            else:
                sig = f"{language} class {class_name}"
            signatures.append(sig)

        # Extract imports
        imports = self._extract_imports(content)
        for imp in imports[:3]:  # Limit imports
            signatures.append(f"{language} import: {imp}")

        if not signatures:
            # Fallback: first line
            first_line = content.split("\n")[0].strip()
            if first_line:
                return f"{language}: {first_line}"
            return ""

        return "\n".join(signatures)

    def can_generate(self, block: ContextBlock) -> bool:
        """Can generate if block has code-related metadata."""
        if block.language:
            return True
        if block.source_type.name == "CODE":
            return True
        if block.metadata.get("type") in ("function", "class", "import"):
            return True
        return False

    def _extract_functions(self, content: str) -> list[tuple[str, str]]:
        """Extract function names and parameters.

        Args:
            content: Code content

        Returns:
            List of (name, params) tuples
        """
        functions = []

        for pattern in self.FUNCTION_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                name = match.group(1)
                params = match.group(2).strip()
                # Truncate long parameter lists
                if len(params) > 50:
                    params = params[:47] + "..."
                functions.append((name, params))

        return functions

    def _extract_classes(self, content: str) -> list[tuple[str, str | None]]:
        """Extract class names and parent classes.

        Args:
            content: Code content

        Returns:
            List of (name, parent) tuples
        """
        classes = []

        for pattern in self.CLASS_PATTERNS:
            matches = re.finditer(pattern, content)
            for match in matches:
                name = match.group(1)
                parent = match.group(2) if len(match.groups()) > 1 else None
                classes.append((name, parent))

        return classes

    def _extract_imports(self, content: str) -> list[str]:
        """Extract import statements.

        Args:
            content: Code content

        Returns:
            List of import strings
        """
        imports = []

        # Python imports
        py_imports = re.findall(r"^(?:from\s+(\S+)\s+)?import\s+(.+)$", content, re.MULTILINE)
        for module, names in py_imports:
            if module:
                imports.append(f"from {module} import {names.strip()}")
            else:
                imports.append(names.strip())

        # JavaScript/TypeScript imports
        js_imports = re.findall(r"import\s+(?:\{([^}]+)\}|(\w+))\s+from\s+['\"]([^'\"]+)['\"]", content)
        for named, default, source in js_imports:
            if named:
                imports.append(f"{{{named.strip()}}} from '{source}'")
            elif default:
                imports.append(f"{default} from '{source}'")

        return imports[:5]  # Limit to first 5
