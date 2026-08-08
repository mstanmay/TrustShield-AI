"""
PDF Renderer — generates complaint PDFs matching SEBI SCORES format using ReportLab.
"""

from __future__ import annotations

import io
import logging
from datetime import datetime
from typing import Any

from app.models.schemas import ComplaintDraft

logger = logging.getLogger(__name__)


class ComplaintPDFRenderer:
    """Renders ComplaintDraft into a downloadable PDF."""

    def render(self, draft: ComplaintDraft) -> bytes:
        """Render a complaint draft as a PDF document.

        Returns:
            PDF bytes ready for download.
        """
        try:
            from reportlab.lib import colors
            from reportlab.lib.pagesizes import A4
            from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
            from reportlab.lib.units import cm, mm
            from reportlab.platypus import (
                Paragraph,
                SimpleDocTemplate,
                Spacer,
                Table,
                TableStyle,
            )
        except ImportError:
            logger.error("reportlab not installed — PDF generation unavailable")
            raise ImportError("reportlab is required for PDF generation. Install with: pip install reportlab")

        buffer = io.BytesIO()
        doc = SimpleDocTemplate(
            buffer,
            pagesize=A4,
            rightMargin=2 * cm,
            leftMargin=2 * cm,
            topMargin=2 * cm,
            bottomMargin=2 * cm,
        )

        styles = getSampleStyleSheet()
        elements = []

        # Custom styles
        title_style = ParagraphStyle(
            "CustomTitle",
            parent=styles["Title"],
            fontSize=16,
            spaceAfter=12,
            textColor=colors.HexColor("#1a237e"),
        )
        heading_style = ParagraphStyle(
            "CustomHeading",
            parent=styles["Heading2"],
            fontSize=12,
            spaceAfter=6,
            spaceBefore=12,
            textColor=colors.HexColor("#283593"),
        )
        body_style = ParagraphStyle(
            "CustomBody",
            parent=styles["Normal"],
            fontSize=10,
            spaceAfter=4,
            leading=14,
        )
        small_style = ParagraphStyle(
            "Small",
            parent=styles["Normal"],
            fontSize=8,
            textColor=colors.grey,
        )

        # ── Header ──────────────────────────────────────────────────────
        elements.append(Paragraph("SEBI SCORES — Complaint Report", title_style))
        elements.append(Paragraph(
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')} | Case: {draft.case_id}",
            small_style,
        ))
        elements.append(Spacer(1, 8 * mm))

        # ── Case Summary Table ───────────────────────────────────────────
        elements.append(Paragraph("Case Summary", heading_style))
        summary_data = [
            ["Field", "Value"],
            ["Case ID", draft.case_id],
            ["Status", draft.status.value],
            ["Subject", draft.subject[:80]],
        ]
        if draft.complainant_name:
            summary_data.append(["Complainant", draft.complainant_name])

        summary_table = Table(summary_data, colWidths=[4 * cm, 12 * cm])
        summary_table.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1a237e")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.whitesmoke),
            ("ALIGN", (0, 0), (-1, -1), "LEFT"),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("BACKGROUND", (0, 1), (-1, -1), colors.HexColor("#f5f5f5")),
            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ]))
        elements.append(summary_table)
        elements.append(Spacer(1, 6 * mm))

        # ── Verdict Summary ──────────────────────────────────────────────
        if draft.verdict_summary:
            elements.append(Paragraph("Verdict", heading_style))
            for line in draft.verdict_summary.split("\n"):
                if line.strip():
                    elements.append(Paragraph(line.strip(), body_style))
            elements.append(Spacer(1, 4 * mm))

        # ── Evidence Summary ─────────────────────────────────────────────
        if draft.evidence_summary:
            elements.append(Paragraph("AI Analysis Evidence", heading_style))
            for agent_ev in draft.evidence_summary:
                agent_name = agent_ev.get("agent", "Unknown")
                confidence = agent_ev.get("confidence", 0)
                result = agent_ev.get("result", "")
                findings = agent_ev.get("key_findings", [])

                elements.append(Paragraph(
                    f"<b>{agent_name}</b> (Confidence: {confidence:.0%})",
                    body_style,
                ))
                elements.append(Paragraph(f"Result: {result}", body_style))
                if findings:
                    for finding in findings[:5]:
                        elements.append(Paragraph(f"  • {finding}", body_style))
                elements.append(Spacer(1, 2 * mm))

        # ── Involved URLs / Domains / Phones ─────────────────────────────
        if draft.involved_urls:
            elements.append(Paragraph("Involved URLs", heading_style))
            for url in draft.involved_urls[:15]:
                elements.append(Paragraph(f"• {url}", body_style))
            elements.append(Spacer(1, 3 * mm))

        if draft.involved_domains:
            elements.append(Paragraph("Involved Domains", heading_style))
            for domain in draft.involved_domains[:15]:
                elements.append(Paragraph(f"• {domain}", body_style))
            elements.append(Spacer(1, 3 * mm))

        if draft.involved_phone_numbers:
            elements.append(Paragraph("Involved Phone Numbers", heading_style))
            for phone in draft.involved_phone_numbers[:10]:
                elements.append(Paragraph(f"• {phone}", body_style))
            elements.append(Spacer(1, 3 * mm))

        # ── Full Complaint Body ──────────────────────────────────────────
        elements.append(Paragraph("Detailed Report", heading_style))
        # Split body into paragraphs for proper PDF rendering
        for line in draft.complaint_body.split("\n"):
            if line.strip():
                # Escape XML characters for ReportLab
                safe_line = (
                    line.strip()
                    .replace("&", "&amp;")
                    .replace("<", "&lt;")
                    .replace(">", "&gt;")
                )
                elements.append(Paragraph(safe_line, body_style))

        # ── Footer ──────────────────────────────────────────────────────
        elements.append(Spacer(1, 10 * mm))
        elements.append(Paragraph(
            "This report was auto-generated by the SEBI Fraud Detection AI System. "
            "It requires user review and confirmation before submission to SEBI SCORES.",
            small_style,
        ))

        # Build PDF
        doc.build(elements)
        pdf_bytes = buffer.getvalue()
        buffer.close()

        logger.info("Generated complaint PDF for case %s (%d bytes)", draft.case_id, len(pdf_bytes))
        return pdf_bytes
