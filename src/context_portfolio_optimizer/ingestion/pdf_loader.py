# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""PDF file loader for ContextFusion."""

from ..logging_utils import get_logger
from ..types import RawSegment
from .base_loader import BaseLoader

logger = get_logger("pdf_loader")


class PDFLoader(BaseLoader):
    """Loader for PDF files using pdfminer.six."""

    SUPPORTED_EXTENSIONS = {".pdf"}

    def __init__(self):
        self._pdfminer_available = None

    def _check_pdfminer(self) -> bool:
        """Check if pdfminer is available."""
        if self._pdfminer_available is None:
            try:
                from pdfminer.high_level import extract_text

                self._pdfminer_available = True
            except ImportError:
                self._pdfminer_available = False
                logger.warning("pdfminer.six not installed, PDF loading disabled")
        return self._pdfminer_available

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is a PDF
        """
        return self._get_extension(file_path) in self.SUPPORTED_EXTENSIONS

    def load(self, file_path: str) -> list[RawSegment]:
        """Load segments from a PDF file.

        Args:
            file_path: Path to the PDF file

        Returns:
            List of raw segments (one per page)
        """
        if not self._check_pdfminer():
            logger.error("pdfminer.six required for PDF loading")
            return []

        from pdfminer.high_level import extract_text

        segments = []

        try:
            # Extract text page by page
            from pdfminer.pdfpage import PDFPage
            from pdfminer.pdfparser import PDFParser
            from pdfminer.pdfdocument import PDFDocument
            from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
            from pdfminer.layout import LAParams
            from pdfminer.converter import TextConverter
            from io import StringIO

            rsrcmgr = PDFResourceManager()
            laparams = LAParams()

            with open(file_path, "rb") as fp:
                # Get page count
                pages = list(PDFPage.get_pages(fp))

                for page_num, page in enumerate(pages, 1):
                    output = StringIO()
                    device = TextConverter(rsrcmgr, output, laparams=laparams)
                    interpreter = PDFPageInterpreter(rsrcmgr, device)
                    interpreter.process_page(page)

                    text = output.getvalue()
                    device.close()
                    output.close()

                    if text.strip():
                        segment = RawSegment(
                            text=text.strip(),
                            metadata={"page_count": len(pages)},
                            source_path=file_path,
                            page_number=page_num,
                        )
                        segments.append(segment)

        except Exception as e:
            logger.error(f"Error loading PDF {file_path}: {e}")
            # Fallback: extract all text as single segment
            try:
                text = extract_text(file_path)
                if text.strip():
                    segments.append(RawSegment(
                        text=text.strip(),
                        source_path=file_path,
                    ))
            except Exception as e2:
                logger.error(f"Fallback PDF extraction failed: {e2}")

        return segments
