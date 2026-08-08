"""
Integration test — runs a sample input through the full LangGraph pipeline end-to-end.

This test mocks the actual ML model calls but exercises the full orchestration:
routing → parallel fan-out → join → risk assessment → decision engine.
"""

from __future__ import annotations

import uuid
from unittest.mock import AsyncMock, patch

import pytest

from app.adapters.deepfake_model import DeepfakeModelResult
from app.models.enums import AgentType, CaseStatus, Classification, InputType, ThreatSeverity
from app.orchestrator.graph import run_pipeline
from app.orchestrator.routing import determine_applicable_agents


class TestRouting:
    """Test the routing logic independently."""

    def test_video_routes_to_all_agents(self):
        agents = determine_applicable_agents(InputType.VIDEO)
        assert AgentType.DEEPFAKE in agents
        assert AgentType.VOICE in agents
        assert AgentType.DOCUMENT in agents
        assert AgentType.PHISHING in agents

    def test_url_routes_to_phishing_only(self):
        agents = determine_applicable_agents(InputType.URL)
        assert AgentType.PHISHING in agents
        assert AgentType.DEEPFAKE not in agents
        assert AgentType.VOICE not in agents

    def test_pdf_routes_to_document(self):
        agents = determine_applicable_agents(InputType.PDF)
        assert AgentType.DOCUMENT in agents

    def test_audio_routes_to_voice(self):
        agents = determine_applicable_agents(InputType.AUDIO)
        assert AgentType.VOICE in agents
        assert AgentType.DEEPFAKE not in agents

    def test_whatsapp_routes_to_document_and_phishing(self):
        agents = determine_applicable_agents(InputType.WHATSAPP_MESSAGE)
        assert AgentType.DOCUMENT in agents
        assert AgentType.PHISHING in agents

    def test_conditional_routing_adds_phishing_on_urls(self):
        agents = determine_applicable_agents(
            InputType.IMAGE,
            metadata={"has_urls": True},
        )
        assert AgentType.PHISHING in agents

    def test_deduplication(self):
        agents = determine_applicable_agents(
            InputType.EMAIL,
            metadata={"has_urls": True},
        )
        # PHISHING is already in EMAIL routing, shouldn't be duplicated
        assert agents.count(AgentType.PHISHING) == 1


@pytest.mark.asyncio
class TestIntegrationPipeline:
    """Full pipeline integration test with mocked agent internals."""

    @patch("app.agents.deepfake_agent.get_deepfake_model")
    @patch("app.agents.voice_agent.VoiceAnalysisAgent._extract_audio_from_video")
    @patch("app.adapters.ocr_provider.TesseractOCRProvider.extract_text", new_callable=AsyncMock)
    @patch("app.adapters.ocr_provider.TesseractOCRProvider.extract_text_from_pdf", new_callable=AsyncMock)
    async def test_url_input_full_pipeline(
        self,
        mock_ocr_pdf,
        mock_ocr_text,
        mock_extract_audio,
        mock_deepfake_model,
    ):
        """Test a URL input going through the full pipeline: route → phishing → risk → decision."""
        from app.orchestrator.graph import run_pipeline

        initial_state = {
            "case_id": str(uuid.uuid4()),
            "input_type": InputType.URL.value,
            "artifact_path": "",
            "original_filename": "",
            "metadata": {
                "url": "https://sebl.gov.in/login",
            },
        }

        result = await run_pipeline(initial_state)

        # Verify pipeline completed
        assert result["status"] == CaseStatus.COMPLETED.value

        # Verify phishing agent ran (URL input)
        assert result.get("phishing_result") is not None
        phishing = result["phishing_result"]
        assert "confidence_score" in phishing
        assert isinstance(phishing["evidence"], list)

        # Verify risk assessment ran
        assert result.get("risk_assessment") is not None
        risk = result["risk_assessment"]
        assert "fraud_probability" in risk
        assert "recommended_action" in risk

        # Verify decision engine produced a verdict
        assert result.get("final_verdict") is not None
        verdict = result["final_verdict"]
        assert verdict["classification"] in [c.value for c in Classification]
        assert verdict["threat_severity"] in [s.value for s in ThreatSeverity]
        assert "evidence_breakdown" in verdict
        assert "reasoning_chain" in verdict

        # Verify execution trace captures all nodes
        trace = result.get("execution_trace", [])
        trace_nodes = [t["node"] for t in trace]
        assert "pipeline_start" in trace_nodes
        assert "route_by_input_type" in trace_nodes
        assert "phishing_agent" in trace_nodes
        assert "risk_assessment" in trace_nodes
        assert "decision_engine" in trace_nodes

    @patch("app.agents.deepfake_agent.get_deepfake_model")
    @patch("app.agents.voice_agent.VoiceAnalysisAgent._extract_audio_from_video")
    @patch("app.adapters.ocr_provider.TesseractOCRProvider.extract_text", new_callable=AsyncMock)
    @patch("app.adapters.ocr_provider.TesseractOCRProvider.extract_text_from_pdf", new_callable=AsyncMock)
    async def test_whatsapp_message_full_pipeline(
        self,
        mock_ocr_pdf,
        mock_ocr_text,
        mock_extract_audio,
        mock_deepfake_model,
    ):
        """Test a WhatsApp scam message through the full pipeline."""
        mock_ocr_text.return_value = ""
        mock_ocr_pdf.return_value = ""

        initial_state = {
            "case_id": str(uuid.uuid4()),
            "input_type": InputType.WHATSAPP_MESSAGE.value,
            "artifact_path": "",
            "original_filename": "",
            "metadata": {
                "text_content": (
                    "URGENT: Guaranteed 100% returns! SEBI registered advisor. "
                    "Visit https://fake-sebi-portal.com/invest NOW! "
                    "Contact +919876543210. Limited time only! Act now!"
                ),
            },
        }

        result = await run_pipeline(initial_state)

        assert result["status"] == CaseStatus.COMPLETED.value

        # Both document and phishing agents should have run
        assert result.get("document_result") is not None
        assert result.get("phishing_result") is not None

        # Document agent should have detected urgency language
        doc = result["document_result"]
        assert doc["confidence_score"] > 0  # Should flag scam language

        # Phishing agent should have analyzed the URL
        phishing = result["phishing_result"]
        assert len(phishing.get("analyzed_urls", [])) >= 1

        # Final verdict should flag this as at least suspicious
        verdict = result["final_verdict"]
        assert verdict["classification"] in ["Suspicious", "Fraudulent"]

    async def test_pipeline_handles_empty_input_gracefully(self):
        """Pipeline handles missing/empty input without crashing."""
        from app.orchestrator.graph import run_pipeline

        initial_state = {
            "case_id": str(uuid.uuid4()),
            "input_type": InputType.URL.value,
            "artifact_path": "",
            "metadata": {},
        }

        result = await run_pipeline(initial_state)

        # Should complete without crashing
        assert result["status"] in [CaseStatus.COMPLETED.value, CaseStatus.FAILED.value]
        assert result.get("execution_trace") is not None
