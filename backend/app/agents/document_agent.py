"""
OCR & Document Verification Agent (3c)

Analyzes PDF/image documents for:
- OCR text extraction (Tesseract or cloud OCR, pluggable)
- Metadata extraction (creation tool, edit history, font-consistency)
- Structured comparison against trusted SEBI circular corpus (vector similarity)
- Forged-document heuristics (font mismatch, resolution inconsistency in signatures/stamps)

Uses the pluggable OCRProvider adapter.
"""

from __future__ import annotations

import hashlib
import logging
import re
import tempfile
from pathlib import Path
from typing import Any

from app.agents.base import BaseAgent
from app.adapters.ocr_provider import get_ocr_provider
from app.core.observability import traced_agent
from app.models.enums import AgentType
from app.models.schemas import DocumentResult, Evidence

logger = logging.getLogger(__name__)

# Known SEBI-related identifiers for validation
SEBI_CIRCULAR_PATTERN = re.compile(
    r"SEBI/HO/[A-Z]+/[A-Z0-9/]+\d{4}", re.IGNORECASE
)
SEBI_DOMAIN_REFS = ["sebi.gov.in", "scores.gov.in", "bseindia.com", "nseindia.com"]
SUSPICIOUS_CREATION_TOOLS = [
    "canva", "photoshop", "gimp", "paint.net", "pixlr",
    "online-convert", "smallpdf",
]


class DocumentVerificationAgent(BaseAgent):
    """Agent 3c: OCR & document verification."""

    @property
    def agent_type(self) -> AgentType:
        return AgentType.DOCUMENT

    def __init__(self):
        self._ocr = get_ocr_provider()

    @traced_agent("document")
    async def _analyze_impl(self, input_path: str, metadata: dict[str, Any]) -> DocumentResult:
        """Run document analysis."""
        evidence: list[Evidence] = []
        raw_output: dict[str, Any] = {}
        extracted_urls: list[str] = []
        metadata_flags: list[str] = []
        ocr_text = ""

        input_type = metadata.get("input_type", "")
        file_data = metadata.get("file_data", b"")

        # If text content is provided directly (WhatsApp/Telegram messages)
        if metadata.get("text_content"):
            ocr_text = metadata["text_content"]
        else:
            # OCR text extraction
            if input_type in ("pdf", "PDF"):
                if isinstance(file_data, bytes) and file_data:
                    ocr_text = await self._ocr.extract_text_from_pdf(file_data)
                else:
                    with open(input_path, "rb") as f:
                        ocr_text = await self._ocr.extract_text_from_pdf(f.read())
            else:
                if isinstance(file_data, bytes) and file_data:
                    ocr_text = await self._ocr.extract_text(file_data)
                else:
                    with open(input_path, "rb") as f:
                        ocr_text = await self._ocr.extract_text(f.read())

        raw_output["ocr_text_length"] = len(ocr_text)

        # ── 1. PDF Metadata Analysis ─────────────────────────────────────
        creation_tool = None
        if input_type in ("pdf", "PDF"):
            pdf_meta = await self._extract_pdf_metadata(input_path, file_data)
            raw_output["pdf_metadata"] = pdf_meta
            creation_tool = pdf_meta.get("producer", "") or pdf_meta.get("creator", "")

            # Check for suspicious creation tools
            if creation_tool:
                tool_lower = creation_tool.lower()
                for suspicious in SUSPICIOUS_CREATION_TOOLS:
                    if suspicious in tool_lower:
                        metadata_flags.append(f"Document created with: {creation_tool}")
                        evidence.append(Evidence(
                            finding=f"Document created with non-standard tool: {creation_tool}",
                            severity="warning",
                            detail={"creation_tool": creation_tool},
                        ))
                        break

            # Check modification dates
            if pdf_meta.get("mod_date") and pdf_meta.get("creation_date"):
                if pdf_meta["mod_date"] != pdf_meta["creation_date"]:
                    metadata_flags.append("Document was modified after creation")
                    evidence.append(Evidence(
                        finding="Document has been modified after initial creation",
                        severity="info",
                        detail={
                            "creation_date": pdf_meta.get("creation_date"),
                            "mod_date": pdf_meta.get("mod_date"),
                        },
                    ))

        # ── 2. SEBI Circular Validation & RAG Corpus Search ───────────────
        circular_matches = SEBI_CIRCULAR_PATTERN.findall(ocr_text)
        corpus_match_score = None
        matched_circular_id = None

        if circular_matches:
            raw_output["circular_numbers_found"] = circular_matches
            for circ_num in circular_matches:
                if not re.match(r"SEBI/HO/", circ_num, re.IGNORECASE):
                    evidence.append(Evidence(
                        finding=f"Suspicious circular number format: {circ_num}",
                        severity="warning",
                        detail={"circular_number": circ_num},
                    ))
                else:
                    matched_circular_id = circ_num

        # Use RAG Knowledge Base search
        try:
            from app.rag.services.knowledge_service import get_knowledge_service
            rag_service = get_knowledge_service()
            rag_results = rag_service.search(query=ocr_text[:500], top_k=2, authority="SEBI")
            if rag_results:
                top_match = rag_results[0]
                corpus_match_score = top_match.get("similarity_score", 0.0)
                raw_output["rag_top_match"] = {
                    "title": top_match.get("metadata", {}).get("title"),
                    "ref_number": top_match.get("metadata", {}).get("ref_number"),
                    "score": corpus_match_score,
                }
                if corpus_match_score > 0.4:
                    evidence.append(Evidence(
                        finding=f"Cross-referenced SEBI circular corpus match: '{top_match.get('metadata', {}).get('title')}' (relevance: {corpus_match_score:.2f})",
                        severity="info",
                        detail=top_match.get("metadata", {}),
                    ))
        except Exception as e:
            logger.debug("RAG corpus check in document agent skipped: %s", e)

        # ── 3. Content Analysis ──────────────────────────────────────────
        # Extract URLs from text
        url_pattern = re.compile(r'https?://[^\s<>"{}|\\^`\[\]]+', re.IGNORECASE)
        extracted_urls = url_pattern.findall(ocr_text)
        raw_output["extracted_urls"] = extracted_urls

        # Check for known SEBI references
        sebi_refs_found = [d for d in SEBI_DOMAIN_REFS if d in ocr_text.lower()]
        raw_output["sebi_references"] = sebi_refs_found

        # Check for urgency/pressure language (common in scams)
        urgency_keywords = [
            "urgent", "immediately", "act now", "limited time", "guaranteed return",
            "risk-free", "double your money", "secret tip", "insider information",
            "last chance", "once in a lifetime", "do not share", "confidential tip",
            "sebi registered", "guaranteed profit", "100% return",
        ]
        found_urgency = [kw for kw in urgency_keywords if kw in ocr_text.lower()]
        if found_urgency:
            evidence.append(Evidence(
                finding=f"Urgency/pressure language detected: {', '.join(found_urgency)}",
                severity="warning" if len(found_urgency) < 3 else "critical",
                detail={"keywords": found_urgency},
            ))

        # Check for financial promises
        money_pattern = re.compile(r'(?:₹|Rs\.?|INR)\s*[\d,]+(?:\.\d+)?', re.IGNORECASE)
        money_mentions = money_pattern.findall(ocr_text)
        if money_mentions:
            raw_output["financial_amounts_mentioned"] = money_mentions

        # Check for phone numbers
        phone_pattern = re.compile(r'(?:\+91|91|0)?[6-9]\d{9}')
        phone_numbers = phone_pattern.findall(ocr_text)
        raw_output["phone_numbers"] = phone_numbers

        # ── 4. Font Consistency Analysis ─────────────────────────────────
        font_consistency_score = 0.0
        if input_type in ("pdf", "PDF"):
            font_score = await self._check_font_consistency(input_path, file_data)
            font_consistency_score = font_score
            raw_output["font_consistency_score"] = font_score
            if font_score > 0.5:
                evidence.append(Evidence(
                    finding=f"Font inconsistency detected (score: {font_score:.2f}) — possible document manipulation",
                    severity="warning",
                    detail={"font_consistency_score": font_score},
                ))

        # ── 5. Compute Overall Confidence ────────────────────────────────
        confidence = 0.0

        # Weight various signals
        if found_urgency:
            confidence += min(len(found_urgency) * 0.1, 0.3)
        if metadata_flags:
            confidence += min(len(metadata_flags) * 0.1, 0.2)
        if font_consistency_score > 0.5:
            confidence += 0.2
        if extracted_urls:
            # URLs in a document claiming to be official is suspicious
            non_sebi_urls = [u for u in extracted_urls if not any(d in u for d in SEBI_DOMAIN_REFS)]
            if non_sebi_urls:
                confidence += 0.15
                evidence.append(Evidence(
                    finding=f"Non-SEBI URLs found in document: {non_sebi_urls[:3]}",
                    severity="warning",
                    detail={"non_sebi_urls": non_sebi_urls[:5]},
                ))

        confidence = min(confidence, 1.0)

        if confidence > 0.6:
            result_text = "HIGH probability of forged/scam document"
        elif confidence > 0.3:
            result_text = "MODERATE indicators of potential document manipulation or scam content"
        else:
            result_text = "Document appears consistent — no strong forgery indicators found"

        return DocumentResult(
            result=result_text,
            confidence_score=confidence,
            evidence=evidence,
            raw_model_output=raw_output,
            ocr_text=ocr_text[:5000],  # Truncate for storage
            metadata_flags=metadata_flags,
            font_consistency_score=font_consistency_score,
            corpus_match_score=corpus_match_score,
            matched_circular_id=matched_circular_id,
            extracted_urls=extracted_urls,
            creation_tool=creation_tool,
        )

    async def _extract_pdf_metadata(self, input_path: str, file_data: bytes = b"") -> dict[str, Any]:
        """Extract PDF metadata (author, creator, producer, dates)."""
        try:
            import fitz  # PyMuPDF

            if file_data:
                doc = fitz.open(stream=file_data, filetype="pdf")
            else:
                doc = fitz.open(input_path)

            meta = doc.metadata or {}
            doc.close()
            return {
                "author": meta.get("author", ""),
                "creator": meta.get("creator", ""),
                "producer": meta.get("producer", ""),
                "subject": meta.get("subject", ""),
                "title": meta.get("title", ""),
                "creation_date": meta.get("creationDate", ""),
                "mod_date": meta.get("modDate", ""),
                "page_count": doc.page_count if hasattr(doc, "page_count") else 0,
            }
        except ImportError:
            logger.warning("PyMuPDF not installed — skipping PDF metadata extraction")
            return {}
        except Exception as e:
            logger.error("PDF metadata extraction failed: %s", e)
            return {}

    async def _check_font_consistency(self, input_path: str, file_data: bytes = b"") -> float:
        """Check font consistency in a PDF — multiple different fonts may indicate forgery."""
        try:
            import fitz

            if file_data:
                doc = fitz.open(stream=file_data, filetype="pdf")
            else:
                doc = fitz.open(input_path)

            all_fonts: set[str] = set()
            for page in doc:
                fonts = page.get_fonts()
                for font in fonts:
                    font_name = font[3] if len(font) > 3 else "unknown"
                    all_fonts.add(font_name)

            doc.close()

            # Many different fonts in a short document is suspicious
            font_count = len(all_fonts)
            if font_count > 6:
                return 0.7
            elif font_count > 4:
                return 0.4
            elif font_count > 2:
                return 0.2
            return 0.0

        except ImportError:
            return 0.0
        except Exception as e:
            logger.error("Font consistency check failed: %s", e)
            return 0.0
