# SPDX-License-Identifier: Apache-2.0
# Copyright (c) 2025–2026 Rohan R @rotsl

"""Image file loader for ContextFusion."""

from ..logging_utils import get_logger
from ..types import RawSegment
from .base_loader import BaseLoader

logger = get_logger("image_loader")


class ImageLoader(BaseLoader):
    """Loader for image files using OCR."""

    SUPPORTED_EXTENSIONS = {".png", ".jpg", ".jpeg", ".tiff", ".tif", ".bmp", ".gif", ".webp"}

    def __init__(self):
        self._tesseract_available = None
        self._pil_available = None

    def _check_pil(self) -> bool:
        """Check if PIL is available."""
        if self._pil_available is None:
            try:
                from PIL import Image

                self._pil_available = True
            except ImportError:
                self._pil_available = False
                logger.warning("Pillow not installed, image loading disabled")
        return self._pil_available

    def _check_tesseract(self) -> bool:
        """Check if tesseract is available."""
        if self._tesseract_available is None:
            try:
                import pytesseract

                # Test if tesseract is installed
                pytesseract.get_tesseract_version()
                self._tesseract_available = True
            except Exception:
                self._tesseract_available = False
                logger.warning("Tesseract not available, OCR disabled")
        return self._tesseract_available

    def supports(self, file_path: str) -> bool:
        """Check if this loader supports the given file.

        Args:
            file_path: Path to the file

        Returns:
            True if file is an image
        """
        return self._get_extension(file_path) in self.SUPPORTED_EXTENSIONS

    def load(self, file_path: str) -> list[RawSegment]:
        """Load text from an image using OCR.

        Args:
            file_path: Path to the image file

        Returns:
            List of raw segments containing extracted text
        """
        if not self._check_pil():
            logger.error("Pillow required for image loading")
            return []

        from PIL import Image

        segments = []

        try:
            img = Image.open(file_path)

            # Get image metadata
            width, height = img.size
            format_name = img.format or "Unknown"

            metadata = {
                "width": width,
                "height": height,
                "format": format_name,
                "mode": img.mode,
            }

            # Try OCR if available
            if self._check_tesseract():
                import pytesseract

                # Convert to RGB if necessary
                if img.mode != "RGB":
                    img = img.convert("RGB")

                text = pytesseract.image_to_string(img)

                if text.strip():
                    segments.append(
                        RawSegment(
                            text=text.strip(),
                            metadata={**metadata, "ocr": True},
                            source_path=file_path,
                            image_caption=f"Image ({width}x{height} {format_name})",
                        )
                    )
                else:
                    segments.append(
                        RawSegment(
                            text="[Image: No text detected]",
                            metadata={**metadata, "ocr": True, "no_text": True},
                            source_path=file_path,
                            image_caption=f"Image ({width}x{height} {format_name})",
                        )
                    )
            else:
                # No OCR, just return image metadata
                segments.append(
                    RawSegment(
                        text=f"[Image: {width}x{height} {format_name} - OCR not available]",
                        metadata={**metadata, "ocr": False},
                        source_path=file_path,
                        image_caption=f"Image ({width}x{height} {format_name})",
                    )
                )

        except Exception as e:
            logger.error(f"Error loading image {file_path}: {e}")
            segments.append(
                RawSegment(
                    text=f"[Error loading image: {e}]",
                    metadata={"error": str(e)},
                    source_path=file_path,
                )
            )

        return segments
