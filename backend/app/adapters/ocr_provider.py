"""
OCR Provider adapter — pluggable interface for text extraction from images/PDFs.
Default: Tesseract OCR via pytesseract.
"""

from __future__ import annotations

import abc
import logging
import tempfile
from pathlib import Path

logger = logging.getLogger(__name__)


class OCRProvider(abc.ABC):
    """Abstract interface for OCR text extraction."""

    @abc.abstractmethod
    async def extract_text(self, image_data: bytes, lang: str = "eng") -> str:
        """Extract text from image bytes."""
        ...

    @abc.abstractmethod
    async def extract_text_from_pdf(self, pdf_data: bytes, lang: str = "eng") -> str:
        """Extract text from PDF bytes (renders pages → OCR)."""
        ...


class TesseractOCRProvider(OCRProvider):
    """Tesseract OCR via pytesseract — working default implementation."""

    async def extract_text(self, image_data: bytes, lang: str = "eng") -> str:
        """Extract text from an image using Tesseract."""
        try:
            import pytesseract
            from PIL import Image
            import io

            image = Image.open(io.BytesIO(image_data))
            text = pytesseract.image_to_string(image, lang=lang)
            return text.strip()
        except ImportError:
            logger.error("pytesseract or Pillow not installed")
            return ""
        except Exception as e:
            logger.error("Tesseract OCR failed: %s", e)
            return ""

    async def extract_text_from_pdf(self, pdf_data: bytes, lang: str = "eng") -> str:
        """Extract text from PDF — tries direct extraction first, then OCR on rendered pages."""
        extracted_parts: list[str] = []

        # 1. Try direct text extraction (for non-scanned PDFs)
        try:
            import fitz  # PyMuPDF

            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp:
                tmp.write(pdf_data)
                tmp_path = tmp.name

            doc = fitz.open(tmp_path)
            for page in doc:
                text = page.get_text()
                if text.strip():
                    extracted_parts.append(text.strip())
            doc.close()
            Path(tmp_path).unlink(missing_ok=True)

            if extracted_parts:
                return "\n\n".join(extracted_parts)
        except ImportError:
            logger.warning("PyMuPDF not installed — falling back to OCR-only PDF extraction")
        except Exception as e:
            logger.warning("Direct PDF text extraction failed: %s", e)

        # 2. Fallback: render pages to images → OCR
        try:
            from pdf2image import convert_from_bytes
            import pytesseract

            images = convert_from_bytes(pdf_data, dpi=300)
            for i, img in enumerate(images):
                text = pytesseract.image_to_string(img, lang=lang)
                if text.strip():
                    extracted_parts.append(text.strip())
        except ImportError:
            logger.error("pdf2image or pytesseract not installed for PDF OCR")
        except Exception as e:
            logger.error("PDF OCR extraction failed: %s", e)

        return "\n\n".join(extracted_parts)


class CloudOCRProvider(OCRProvider):
    """Placeholder for cloud-based OCR (Google Cloud Vision, AWS Textract).

    # TODO: upgrade to trained model — implement with actual cloud OCR API
    """

    async def extract_text(self, image_data: bytes, lang: str = "eng") -> str:
        logger.warning("CloudOCRProvider: not implemented, returning empty string")
        return ""

    async def extract_text_from_pdf(self, pdf_data: bytes, lang: str = "eng") -> str:
        logger.warning("CloudOCRProvider: not implemented, returning empty string")
        return ""


def get_ocr_provider() -> OCRProvider:
    """Factory: returns the configured OCR provider."""
    return TesseractOCRProvider()
