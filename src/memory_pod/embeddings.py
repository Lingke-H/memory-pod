"""Local embedding providers.

Memory Pod prefers a locally cached sentence-transformers model. If it is not
available, it falls back to a deterministic hashing embedder so demos and tests
still run without network access.
"""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from functools import lru_cache
from typing import Iterable, Protocol

import numpy as np

from memory_pod.config import DEFAULT_MODEL_NAME

LOGGER = logging.getLogger("memory_pod.embeddings")
TOKEN_RE = re.compile(r"[A-Za-z0-9_']+")


class Embedder(Protocol):
    def embed(self, texts: Iterable[str]) -> np.ndarray:
        """Return one normalized vector per input text."""


@dataclass
class HashingEmbedder:
    """Small deterministic local fallback for hackathon reliability."""

    dimensions: int = 384

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        vectors = [self._embed_one(text) for text in texts]
        if not vectors:
            return np.zeros((0, self.dimensions), dtype=np.float32)
        return np.vstack(vectors).astype(np.float32)

    def _embed_one(self, text: str) -> np.ndarray:
        vector = np.zeros(self.dimensions, dtype=np.float32)
        tokens = [_normalize_token(token) for token in TOKEN_RE.findall(text.lower())]
        for token in tokens:
            digest = hashlib.blake2b(token.encode("utf-8"), digest_size=8).digest()
            bucket = int.from_bytes(digest[:4], "big") % self.dimensions
            vector[bucket] += 1.0

        norm = np.linalg.norm(vector)
        if norm > 0:
            vector /= norm
        return vector


class SentenceTransformerEmbedder:
    """Wrapper around a locally cached sentence-transformers model."""

    def __init__(self, model_name: str = DEFAULT_MODEL_NAME) -> None:
        from sentence_transformers import SentenceTransformer

        self.model = SentenceTransformer(model_name, local_files_only=True)

    def embed(self, texts: Iterable[str]) -> np.ndarray:
        text_list = list(texts)
        if not text_list:
            return np.zeros((0, 384), dtype=np.float32)
        vectors = self.model.encode(
            text_list,
            convert_to_numpy=True,
            normalize_embeddings=True,
            show_progress_bar=False,
        )
        return vectors.astype(np.float32)


@lru_cache(maxsize=2)
def get_embedder(prefer_sentence_transformers: bool = True) -> Embedder:
    """Return the best available local embedder without downloading anything."""

    if prefer_sentence_transformers:
        try:
            return SentenceTransformerEmbedder()
        except Exception as exc:
            LOGGER.info(
                "Falling back to hashing embeddings because %s is not available locally: %s",
                DEFAULT_MODEL_NAME,
                exc,
            )

    return HashingEmbedder()


def _normalize_token(token: str) -> str:
    if len(token) > 5 and token.endswith("ing"):
        return token[:-3]
    if len(token) > 4 and token.endswith("ed"):
        return token[:-2]
    if len(token) > 3 and token.endswith("s"):
        return token[:-1]
    return token
