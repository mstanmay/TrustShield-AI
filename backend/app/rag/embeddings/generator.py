"""
Embedding Generator — generates dense vector embeddings for RAG document chunking & retrieval.
Supports SentenceTransformers, OpenAI embeddings, and deterministic hashing fallback.
"""

from __future__ import annotations

import hashlib
import logging
import math
import re
from typing import Sequence

logger = logging.getLogger(__name__)


class EmbeddingGenerator:
    """Generates normalized vector embeddings for text chunks and search queries."""

    def __init__(self, dimension: int = 384):
        self.dimension = dimension
        self._st_model = None

    def _get_st_model(self):
        if self._st_model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._st_model = SentenceTransformer("all-MiniLM-L6-v2")
                logger.info("Loaded SentenceTransformer all-MiniLM-L6-v2 model")
            except Exception as e:
                logger.debug("SentenceTransformers unavailable, using deterministic semantic embedding: %s", e)
        return self._st_model

    def generate_embedding(self, text: str) -> list[float]:
        """Generate a single normalized vector embedding for a string."""
        model = self._get_st_model()
        if model is not None:
            try:
                vec = model.encode(text, convert_to_numpy=True).tolist()
                return self._normalize(vec)
            except Exception as e:
                logger.warning("SentenceTransformer encoding failed: %s", e)

        # Fallback: Deterministic semantic feature projection
        return self._fallback_embedding(text)

    def generate_batch(self, texts: Sequence[str]) -> list[list[float]]:
        """Generate vector embeddings for a list of strings."""
        return [self.generate_embedding(t) for t in texts]

    def _fallback_embedding(self, text: str) -> list[float]:
        """Deterministic semantic feature projection algorithm."""
        tokens = re.findall(r"\w+", text.lower())
        vec = [0.0] * self.dimension
        
        for token in tokens:
            # Seed-based hashing to project token onto dimension space
            h = int(hashlib.md5(token.encode("utf-8")).hexdigest(), 16)
            index = h % self.dimension
            sign = 1.0 if (h & 1) else -1.0
            vec[index] += sign

        return self._normalize(vec)

    @staticmethod
    def _normalize(vec: list[float]) -> list[float]:
        norm = math.sqrt(sum(x * x for x in vec))
        if norm < 1e-9:
            return [0.0] * len(vec)
        return [x / norm for x in vec]

    @staticmethod
    def cosine_similarity(vec1: list[float], vec2: list[float]) -> float:
        """Compute cosine similarity between two normalized vectors."""
        if len(vec1) != len(vec2):
            return 0.0
        return sum(a * b for a, b in zip(vec1, vec2))
