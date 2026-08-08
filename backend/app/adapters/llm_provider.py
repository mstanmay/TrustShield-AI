"""
LLM Provider adapter — pluggable interface for language model calls.
Default: Anthropic Claude via the `anthropic` SDK.
Model name configurable via ANTHROPIC_MODEL_NAME env var.
"""

from __future__ import annotations

import abc
import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class LLMResponse:
    """Response from an LLM call."""
    content: str
    model: str = ""
    usage: dict = field(default_factory=dict)
    raw_response: dict = field(default_factory=dict)


class LLMProvider(abc.ABC):
    """Abstract interface for LLM calls."""

    @abc.abstractmethod
    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Generate a completion from the LLM."""
        ...


class AnthropicLLMProvider(LLMProvider):
    """Anthropic Claude integration via the official SDK."""

    def __init__(self, api_key: str, model_name: str = "claude-sonnet-4-20250514"):
        self._api_key = api_key
        self._model_name = model_name
        self._client = None

    def _get_client(self):
        if self._client is None:
            import anthropic
            self._client = anthropic.AsyncAnthropic(api_key=self._api_key)
        return self._client

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        """Call Claude for a completion."""
        try:
            client = self._get_client()
            kwargs = {
                "model": self._model_name,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": [{"role": "user", "content": prompt}],
            }
            if system_prompt:
                kwargs["system"] = system_prompt

            response = await client.messages.create(**kwargs)

            content = ""
            if response.content:
                content = response.content[0].text

            return LLMResponse(
                content=content,
                model=response.model,
                usage={
                    "input_tokens": response.usage.input_tokens,
                    "output_tokens": response.usage.output_tokens,
                },
                raw_response={"id": response.id, "stop_reason": response.stop_reason},
            )
        except Exception as e:
            logger.error("Anthropic API call failed: %s", e)
            return LLMResponse(
                content=f"LLM call failed: {e}",
                model=self._model_name,
                raw_response={"error": str(e)},
            )


class FallbackLLMProvider(LLMProvider):
    """Fallback provider that generates template-based explanations without an API.

    # TODO: upgrade to trained model — use this only when no API key is available.
    """

    async def generate(
        self,
        prompt: str,
        system_prompt: str = "",
        max_tokens: int = 4096,
        temperature: float = 0.1,
    ) -> LLMResponse:
        logger.warning("FallbackLLMProvider: generating template-based response (no LLM API configured)")

        # Extract key phrases from prompt for a semi-useful response
        content = (
            "Analysis completed based on available agent outputs. "
            "Detailed reasoning: The system evaluated all applicable detection agents "
            "and computed a weighted risk score based on their individual confidence levels "
            "and evidence findings. Please review the evidence breakdown for specifics. "
            "[Note: This explanation was generated without an LLM — configure ANTHROPIC_API_KEY "
            "for detailed natural-language reasoning.]"
        )

        return LLMResponse(
            content=content,
            model="fallback-template",
            raw_response={"note": "No LLM API configured"},
        )


def get_llm_provider() -> LLMProvider:
    """Factory: returns the configured LLM provider."""
    from app.config import settings
    if settings.ANTHROPIC_API_KEY:
        return AnthropicLLMProvider(
            api_key=settings.ANTHROPIC_API_KEY,
            model_name=settings.ANTHROPIC_MODEL_NAME,
        )
    logger.warning("No ANTHROPIC_API_KEY set — using FallbackLLMProvider")
    return FallbackLLMProvider()
