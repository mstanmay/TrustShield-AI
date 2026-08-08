"""
Base Agent — abstract base class defining the standard interface for all agents.
Every agent must return an AgentResult with result, confidence_score, evidence, raw_model_output.
"""

from __future__ import annotations

import abc
import logging
import time
from typing import Any

from app.models.schemas import AgentResult, Evidence
from app.models.enums import AgentType

logger = logging.getLogger(__name__)


class BaseAgent(abc.ABC):
    """Abstract base class for all fraud detection agents.

    Subclasses must implement:
        - agent_type: the AgentType enum value
        - _analyze_impl: the actual analysis logic

    The public analyze() method handles:
        - Timing
        - Error handling
        - Confidence normalization
        - Standard result packaging
    """

    @property
    @abc.abstractmethod
    def agent_type(self) -> AgentType:
        """Return the agent's type identifier."""
        ...

    @abc.abstractmethod
    async def _analyze_impl(self, input_path: str, metadata: dict[str, Any]) -> AgentResult:
        """Internal analysis implementation. Override in subclasses."""
        ...

    async def analyze(self, input_path: str, metadata: dict[str, Any] | None = None) -> AgentResult:
        """Public interface: run analysis with standard error handling and timing.

        Args:
            input_path: Path to the file/URL to analyze.
            metadata: Additional context (input_type, extracted_text, etc.)

        Returns:
            AgentResult (or subclass) with all required fields populated.
        """
        metadata = metadata or {}
        start_time = time.time()

        try:
            result = await self._analyze_impl(input_path, metadata)

            # Normalize confidence score
            result.confidence_score = max(0.0, min(1.0, result.confidence_score))

            # Attach execution time
            result.execution_time_ms = (time.time() - start_time) * 1000

            return result

        except Exception as e:
            elapsed_ms = (time.time() - start_time) * 1000
            logger.error(
                "Agent %s failed: %s",
                self.agent_type.value,
                str(e),
                exc_info=True,
            )

            # Return a safe error result rather than crashing the pipeline
            return AgentResult(
                agent_type=self.agent_type,
                result=f"Agent failed: {str(e)}",
                confidence_score=0.0,
                evidence=[
                    Evidence(
                        finding=f"Agent error: {str(e)}",
                        severity="warning",
                        detail={"exception_type": type(e).__name__},
                    )
                ],
                raw_model_output={"error": str(e)},
                execution_time_ms=elapsed_ms,
                error=str(e),
            )
