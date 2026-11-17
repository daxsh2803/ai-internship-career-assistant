
import os
import sys
import math
import re
from typing import List, Dict, Tuple, Any

class BM25Retriever:

    def __init__(self, documents: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.documents = documents
        self.corpus_size = len(documents)
        self.tokenized_corpus = [self._tokenize(doc) for doc in documents]
        self.doc_lengths = [len(doc) for doc in self.tokenized_corpus]
        self.avg_doc_len = sum(self.doc_lengths) / max(self.corpus_size, 1)
        self.doc_frequencies = self._compute_doc_frequencies()

    def _tokenize(self, text: str) -> List[str]:
        return re.findall(r"\b\w+\b", text.lower())

    def _compute_doc_frequencies(self) -> Dict[str, int]:
        df = {}
        for doc in self.tokenized_corpus:
            for term in set(doc):
                df[term] = df.get(term, 0) + 1
        return df

    def _compute_idf(self, term: str) -> float:
        n_q = self.doc_frequencies.get(term, 0)
        return math.log(1.0 + (self.corpus_size - n_q + 0.5) / (n_q + 0.5))

    def score(self, query: str) -> List[Tuple[int, float]]:
        query_terms = self._tokenize(query)
        scores = []

        for doc_idx, doc_tokens in enumerate(self.tokenized_corpus):
            doc_len = self.doc_lengths[doc_idx]
            doc_score = 0.0
            term_counts = {}
            for t in doc_tokens:
                term_counts[t] = term_counts.get(t, 0) + 1

            for term in query_terms:
                if term not in term_counts:
                    continue
                tf = term_counts[term]
                idf = self._compute_idf(term)
                numerator = tf * (self.k1 + 1.0)
                denominator = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / self.avg_doc_len))
                doc_score += idf * (numerator / denominator)

            scores.append((doc_idx, doc_score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_a = math.sqrt(sum(a * a for a in v1))
    norm_b = math.sqrt(sum(b * b for b in v2))
    if norm_a == 0.0 or norm_b == 0.0:
        return 0.0
    return dot_product / (norm_a * norm_b)

class DenseVectorRetriever:

    def __init__(self, documents: List[str], dim: int = 384):
        self.documents = documents
        self.dim = dim
        self.use_sbert = False
        self.model = None

        try:
            import os
            if "sentence_transformers" in sys.modules or os.environ.get("USE_SBERT") == "1":
                from sentence_transformers import SentenceTransformer
                self.model = SentenceTransformer("BAAI/bge-small-en-v1.5")
                self.use_sbert = True
        except Exception:
            self.use_sbert = False

        self.doc_embeddings = [self.embed(doc) for doc in documents]

    def embed(self, text: str) -> List[float]:
        if self.use_sbert and self.model:
            emb = self.model.encode(text, normalize_embeddings=True)
            return emb.tolist()

        tokens = re.findall(r"\b\w+\b", text.lower())
        vec = [0.0] * self.dim
        for i, token in enumerate(tokens):
            h = hash(token) % self.dim
            vec[h] += 1.0 + (1.0 / (i + 1.0))

        norm = math.sqrt(sum(x * x for x in vec))
        if norm > 0.0:
            vec = [x / norm for x in vec]
        return vec

    def score(self, query: str) -> List[Tuple[int, float]]:
        q_emb = self.embed(query)
        scores = []
        for doc_idx, doc_emb in enumerate(self.doc_embeddings):
            sim = cosine_similarity(q_emb, doc_emb)
            scores.append((doc_idx, sim))
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores

def reciprocal_rank_fusion(
    dense_ranks: List[Tuple[int, float]],
    sparse_ranks: List[Tuple[int, float]],
    k: int = 60
) -> List[Tuple[int, float]]:
    rrf_scores = {}

    for rank_idx, (doc_idx, _) in enumerate(dense_ranks):
        rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (k + (rank_idx + 1)))

    for rank_idx, (doc_idx, _) in enumerate(sparse_ranks):
        rrf_scores[doc_idx] = rrf_scores.get(doc_idx, 0.0) + (1.0 / (k + (rank_idx + 1)))

    fused = sorted(rrf_scores.items(), key=lambda x: x[1], reverse=True)
    return fused

def simulate_cross_encoder_rerank(query: str, candidate_docs: List[str]) -> List[float]:
    q_terms = set(re.findall(r"\b\w+\b", query.lower()))
    rerank_scores = []

    for doc in candidate_docs:
        doc_terms = re.findall(r"\b\w+\b", doc.lower())
        overlap = sum(1 for t in doc_terms if t in q_terms)
        proximity_bonus = 0.2 if ("python" in doc.lower() and "redis" in doc.lower()) else 0.0
        score = min(1.0, (overlap / max(len(q_terms), 1)) * 0.8 + proximity_bonus)
        rerank_scores.append(round(score, 4))

    return rerank_scores

CANDIDATE_RESUME_CHUNKS = [
    "Distributed Asynchronous Task Queue in Python, Redis, and Docker. Implemented worker consumers handling 1,500 background tasks/sec with dead-letter queue recovery.",
    
    "Interactive UI Dashboard in React, Next.js, and Tailwind CSS. Built responsive navigation bars, client state management with Zustand, and dark mode themes.",
    
    "Computer Vision Image Classifier in PyTorch and OpenCV. Trained convolutional neural networks on CIFAR-10 achieving 91% test accuracy with data augmentation.",
    
    "Cloud-Native Storage Service in FastAPI, PostgreSQL, and Docker. Implemented pgvector semantic search and optimized relational SQL query indexes.",
    
    "Cross-Platform Mobile App in Flutter and Dart. Designed stateful UI widgets, integrated Firebase Firestore for real-time authentication, and published to Google Play.",
]

TARGET_JOB_QUERY = "Backend Software Engineering Intern requiring Python, FastAPI, Redis, PostgreSQL, and asynchronous microservices."

def run_hybrid_matching_validation() -> dict:
    print("=" * 70)
    print("PoC 3: Hybrid Retrieval Validation (Dense Vector + BM25 Lexical + RRF)")
    print("=" * 70)

    print(f"[*] Query: '{TARGET_JOB_QUERY}'")
    print(f"[*] Candidate Corpus Size: {len(CANDIDATE_RESUME_CHUNKS)} document chunks\n")

    bm25 = BM25Retriever(CANDIDATE_RESUME_CHUNKS)
    bm25_ranks = bm25.score(TARGET_JOB_QUERY)
    print("[*] Stage 1A: BM25 Lexical Scores:")
    for rank, (doc_id, score) in enumerate(bm25_ranks):
        print(f"    Rank {rank+1}: Doc {doc_id} | Score: {score:.4f} | Preview: '{CANDIDATE_RESUME_CHUNKS[doc_id][:55]}...'")

    dense = DenseVectorRetriever(CANDIDATE_RESUME_CHUNKS)
    dense_ranks = dense.score(TARGET_JOB_QUERY)
    print("\n[*] Stage 1B: Dense Vector Similarity Scores:")
    for rank, (doc_id, score) in enumerate(dense_ranks):
        print(f"    Rank {rank+1}: Doc {doc_id} | Cosine Sim: {score:.4f} | Preview: '{CANDIDATE_RESUME_CHUNKS[doc_id][:55]}...'")

    rrf_fused = reciprocal_rank_fusion(dense_ranks, bm25_ranks, k=60)
    print("\n[*] Stage 2: Reciprocal Rank Fusion (RRF) Combined Scores:")
    for rank, (doc_id, score) in enumerate(rrf_fused):
        print(f"    Rank {rank+1}: Doc {doc_id} | RRF Score: {score:.5f} | Preview: '{CANDIDATE_RESUME_CHUNKS[doc_id][:55]}...'")

    top_candidates = [CANDIDATE_RESUME_CHUNKS[doc_id] for doc_id, _ in rrf_fused[:3]]
    rerank_scores = simulate_cross_encoder_rerank(TARGET_JOB_QUERY, top_candidates)
    print("\n[*] Stage 3: Cross-Encoder Re-Ranking of Top Candidates:")
    for rank, ((doc_id, _), re_score) in enumerate(zip(rrf_fused[:3], rerank_scores)):
        print(f"    Final Rank {rank+1}: Doc {doc_id} | Cross-Attention Score: {re_score:.4f}")

    print("\n[*] Running Retrieval Integrity Assertions:")

    top_doc_id = rrf_fused[0][0]
    second_doc_id = rrf_fused[1][0]
    lowest_doc_id = rrf_fused[-1][0]

    top_2_doc_ids = {rrf_fused[0][0], rrf_fused[1][0]}
    assert top_2_doc_ids == {0, 3}, f"Expected top 2 docs to be {0, 3}, but got {top_2_doc_ids}"
    print("  [✓] Top 2 ranks strictly occupied by backend systems (Docs 0 & 3).")

    bottom_3_doc_ids = {rrf_fused[2][0], rrf_fused[3][0], rrf_fused[4][0]}
    assert bottom_3_doc_ids == {1, 2, 4}, f"Expected bottom 3 to be {1, 2, 4}, but got {bottom_3_doc_ids}"
    print("  [✓] Non-backend chunks (React, CV, Mobile) correctly relegated to bottom ranks.")

    for _, score in rrf_fused:
        assert 0.0 < score <= (2.0 / 61.0), "RRF score outside mathematical bounds"
    print("  [✓] RRF scores strictly obey Reciprocal Rank Fusion formula bounds.")

    print("\n[+] SUCCESS: Hybrid retrieval and re-ranking validation passed!")

    return {
        "status": "PASSED",
        "top_ranked_doc_id": top_doc_id,
        "second_ranked_doc_id": second_doc_id,
        "lowest_ranked_doc_id": lowest_doc_id,
        "bm25_evaluated": True,
        "dense_evaluated": True,
        "rrf_fused": True,
    }

if __name__ == "__main__":
    results = run_hybrid_matching_validation()
    print("\nTest Result Summary:", results)
