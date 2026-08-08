"""
LangGraph routing logic — determines which agents to invoke based on input type.

Implements conditional routing with the routing matrix:
- Video → Deepfake + Voice + Document (if text overlays) + Phishing (if QR/URLs)
- Image → Deepfake + Document (if text) + Phishing (if QR/URLs)
- Audio → Voice
- PDF → Document + Phishing (if URLs in text)
- URL → Phishing
- Email → Document + Phishing
- QR Code → Phishing
- WhatsApp/Telegram → Document + Phishing
"""

from __future__ import annotations

import logging
from typing import Any

from app.models.enums import AgentType, InputType

logger = logging.getLogger(__name__)

# Static routing matrix: which agents always apply for each input type
ROUTING_MATRIX: dict[InputType, list[AgentType]] = {
    InputType.VIDEO: [AgentType.DEEPFAKE, AgentType.VOICE],
    InputType.IMAGE: [AgentType.DEEPFAKE],
    InputType.AUDIO: [AgentType.VOICE],
    InputType.PDF: [AgentType.DOCUMENT],
    InputType.URL: [AgentType.PHISHING],
    InputType.EMAIL: [AgentType.DOCUMENT, AgentType.PHISHING],
    InputType.QR_CODE: [AgentType.PHISHING],
    InputType.WHATSAPP_MESSAGE: [AgentType.DOCUMENT, AgentType.PHISHING],
    InputType.TELEGRAM_LINK: [AgentType.DOCUMENT, AgentType.PHISHING],
}

# Conditional additions (added based on content analysis)
CONDITIONAL_AGENTS: dict[str, AgentType] = {
    "has_text_overlays": AgentType.DOCUMENT,
    "has_urls": AgentType.PHISHING,
    "has_qr_code": AgentType.PHISHING,
    "has_audio": AgentType.VOICE,
}


def determine_applicable_agents(
    input_type: InputType | str,
    metadata: dict[str, Any] | None = None,
) -> list[AgentType]:
    """Determine which agents should run for a given input type and metadata.

    Args:
        input_type: The detected input type
        metadata: Additional content metadata (e.g., has_urls, has_qr_code)

    Returns:
        Deduplicated list of applicable AgentType values.
    """
    if isinstance(input_type, str):
        try:
            input_type = InputType(input_type)
        except ValueError:
            logger.warning("Unknown input type: %s, defaulting to all agents", input_type)
            return [AgentType.DEEPFAKE, AgentType.VOICE, AgentType.DOCUMENT, AgentType.PHISHING]

    metadata = metadata or {}

    # Start with the static matrix
    agents = list(ROUTING_MATRIX.get(input_type, []))

    # Add conditional agents based on metadata
    if metadata.get("has_text_overlays") and AgentType.DOCUMENT not in agents:
        agents.append(AgentType.DOCUMENT)
        logger.info("Added DOCUMENT agent: text overlays detected in media")

    if metadata.get("has_urls") and AgentType.PHISHING not in agents:
        agents.append(AgentType.PHISHING)
        logger.info("Added PHISHING agent: URLs detected in content")

    if metadata.get("has_qr_code") and AgentType.PHISHING not in agents:
        agents.append(AgentType.PHISHING)
        logger.info("Added PHISHING agent: QR code detected in image")

    if metadata.get("has_audio") and AgentType.VOICE not in agents:
        agents.append(AgentType.VOICE)
        logger.info("Added VOICE agent: audio track detected")

    # For video inputs, always check for document/phishing potential
    if input_type == InputType.VIDEO:
        if AgentType.DOCUMENT not in agents:
            agents.append(AgentType.DOCUMENT)
        if AgentType.PHISHING not in agents:
            agents.append(AgentType.PHISHING)

    # Deduplicate while preserving order
    seen = set()
    deduped = []
    for agent in agents:
        if agent not in seen:
            seen.add(agent)
            deduped.append(agent)

    logger.info(
        "Routing for input_type=%s: %s",
        input_type.value,
        [a.value for a in deduped],
    )

    return deduped


def should_run_agent(agent_type: AgentType, applicable_agents: list[str]) -> bool:
    """Check if a specific agent should run based on the routing decision."""
    return agent_type.value in applicable_agents
