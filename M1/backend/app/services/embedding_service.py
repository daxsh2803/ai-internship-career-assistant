
import hashlib
import math
from typing import List, Optional
import numpy as np

from app.core.config import settings

class LocalEmbeddingService:
    _instance: Optional["LocalEmbeddingService"] = None
    _model = None

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dim = settings.EMBEDDING_DIM

    @classmethod
    def get_instance(cls) -> "LocalEmbeddingService":
        if cls._instance is None:
            cls._instance = LocalEmbeddingService()
        return cls._instance

    def _load_model(self):
        if self._model is None:
            try:
                import os
                os.environ["HF_HUB_OFFLINE"] = "1"
                os.environ["TRANSFORMERS_OFFLINE"] = "1"
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name, device="cpu")
            except Exception:
                self._model = None

    def get_embedding(self, text: str) -> List[float]:
        if not text or not text.strip():
            return [0.0] * self.dim

        self._load_model()

        if self._model is not None:
            try:
                vec = self._model.encode(text.strip(), normalize_embeddings=True)
                return [float(x) for x in vec]
            except Exception:
                pass

        return self._generate_fallback_vector(text.strip())

    def _generate_fallback_vector(self, text: str) -> List[float]:
        tokens = text.lower().split()
        vec = np.zeros(self.dim, dtype=np.float32)

        for i, token in enumerate(tokens):
            h = int(hashlib.sha256(token.encode("utf-8")).hexdigest(), 16)
            idx = h % self.dim
            val = ((h >> 8) % 1000) / 1000.0 - 0.5
            vec[idx] += val

        norm = np.linalg.norm(vec)
        if norm > 1e-6:
            vec = vec / norm
        else:
            vec[0] = 1.0

        return [float(x) for x in vec]

    @staticmethod
    def cosine_similarity(v1: List[float], v2: List[float]) -> float:
        if len(v1) != len(v2) or not v1:
            return 0.0
        dot = sum(a * b for a, b in zip(v1, v2))
        norm1 = math.sqrt(sum(a * a for a in v1))
        norm2 = math.sqrt(sum(b * b for b in v2))
        if norm1 < 1e-6 or norm2 < 1e-6:
            return 0.0
        return float(dot / (norm1 * norm2))
