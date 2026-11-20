import hashlib
import math
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
import numpy as np

os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"
os.environ["TOKENIZERS_PARALLELISM"] = "false"

try:
    import opentelemetry.util.types as otel_types
    otel_types._ExtendedAttributes = getattr(otel_types, "Attributes", None)
    import opentelemetry.attributes as otel_attrs
    otel_attrs._VALID_ANY_VALUE_TYPES = (bool, str, bytes, int, float)
except Exception:
    pass

try:
    import chromadb
    from chromadb.config import Settings as ChromaSettings
except Exception:
    chromadb = None
    ChromaSettings = None

from app.core.config import settings
from app.services.chunking_service import JobChunk

class LocalEmbeddingService:
    _instance: Optional["LocalEmbeddingService"] = None
    _model = None
    _reranker = None
    _chroma_client = None

    def __init__(self):
        self.model_name = settings.EMBEDDING_MODEL_NAME
        self.dim = settings.EMBEDDING_DIM
        self.reranker_model_name = "cross-encoder/ms-marco-MiniLM-L-6-v2"
        self.vectorstore_path = Path("./data/vectorstore")

    @classmethod
    def get_instance(cls) -> "LocalEmbeddingService":
        if cls._instance is None:
            cls._instance = LocalEmbeddingService()
        return cls._instance

    def _load_model(self):
        if self._model is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer(self.model_name, device="cpu")
            return
        except Exception:
            pass

        try:
            from sentence_transformers import SentenceTransformer
            self._model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2", device="cpu")
            return
        except Exception:
            self._model = None

    def _load_reranker(self):
        if self._reranker is not None:
            return
        try:
            from sentence_transformers import CrossEncoder
            self._reranker = CrossEncoder(self.reranker_model_name, device="cpu")
        except Exception:
            self._reranker = None

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

    def get_embeddings(self, texts: List[str], batch_size: int = 64) -> List[List[float]]:
        cleaned = [t.strip() if t and t.strip() else "" for t in texts]
        if not cleaned:
            return []
        self._load_model()
        if self._model is not None:
            try:
                vectors = self._model.encode(
                    cleaned,
                    batch_size=batch_size,
                    normalize_embeddings=True,
                    show_progress_bar=False,
                )
                return [[float(val) for val in row] for row in vectors]
            except Exception:
                pass
        return [self._generate_fallback_vector(t) for t in cleaned]

    def rerank(self, query: str, candidate_texts: List[str]) -> List[float]:
        if not candidate_texts:
            return []
        self._load_reranker()
        if self._reranker is not None:
            try:
                pairs = [[query, text] for text in candidate_texts]
                scores = self._reranker.predict(pairs)
                return [float(s) for s in scores]
            except Exception:
                pass

        query_emb = self.get_embedding(query)
        cand_embs = self.get_embeddings(candidate_texts)
        return [self.cosine_similarity(query_emb, ce) for ce in cand_embs]

    def _generate_fallback_vector(self, text: str) -> List[float]:
        tokens = text.lower().split()
        vec = np.zeros(self.dim, dtype=np.float32)
        for token in tokens:
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

    def get_chroma_client(self, persist_dir: Optional[str] = None):
        target_dir = Path(persist_dir) if persist_dir else self.vectorstore_path
        target_dir.mkdir(parents=True, exist_ok=True)
        if self._chroma_client is None:
            if chromadb is None:
                raise RuntimeError("ChromaDB is not installed or available.")
            self._chroma_client = chromadb.PersistentClient(path=str(target_dir))
        return self._chroma_client

    def get_collection(self, collection_name: str = "internship_chunks", persist_dir: Optional[str] = None):
        client = self.get_chroma_client(persist_dir)
        return client.get_or_create_collection(
            name=collection_name,
            metadata={"hnsw:space": "cosine"},
        )

    def index_chunks(
        self,
        chunks: List[JobChunk],
        collection_name: str = "internship_chunks",
        persist_dir: Optional[str] = None,
        batch_size: int = 64,
    ) -> int:
        if not chunks:
            return 0
        collection = self.get_collection(collection_name, persist_dir)
        total_chunks = len(chunks)

        for i in range(0, total_chunks, batch_size):
            batch = chunks[i : i + batch_size]
            ids = [c.chunk_id for c in batch]
            docs = [c.content for c in batch]
            embs = self.get_embeddings(docs, batch_size=batch_size)
            metas = []
            for c in batch:
                clean_meta: Dict[str, Any] = {}
                for k, v in c.metadata.items():
                    if isinstance(v, (str, int, float, bool)):
                        clean_meta[k] = v
                    elif v is None:
                        clean_meta[k] = ""
                    else:
                        clean_meta[k] = str(v)
                metas.append(clean_meta)

            collection.upsert(
                ids=ids,
                embeddings=embs,
                documents=docs,
                metadatas=metas,
            )

        return total_chunks
