import math
import re
from typing import Any, Dict, List, Optional, Set, Tuple

from app.schemas.job import (
    MatchedChunkInfo,
    SemanticSearchRequest,
    SemanticSearchResponse,
    SemanticSearchResultItem,
    StandardJobPosting,
)
from app.services.chunking_service import ChunkingService, JobChunk
from app.services.dataset_loader import DatasetLoaderService
from app.services.embedding_service import LocalEmbeddingService

class BM25Retriever:
    def __init__(self, corpus: List[str], chunk_ids: List[str], k1: float = 1.5, b: float = 0.75):
        self.k1 = k1
        self.b = b
        self.chunk_ids = chunk_ids
        self.corpus_size = len(corpus)
        self.tokenized_corpus = [self._tokenize(doc) for doc in corpus]
        self.doc_lens = [len(doc) for doc in self.tokenized_corpus]
        self.avg_doc_len = sum(self.doc_lens) / max(1, self.corpus_size)

        self.doc_freqs: Dict[str, int] = {}
        for doc in self.tokenized_corpus:
            unique_terms = set(doc)
            for term in unique_terms:
                self.doc_freqs[term] = self.doc_freqs.get(term, 0) + 1

        self.idf: Dict[str, float] = {}
        for term, freq in self.doc_freqs.items():
            self.idf[term] = math.log(1.0 + (self.corpus_size - freq + 0.5) / (freq + 0.5))

    @staticmethod
    def _tokenize(text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\+\#\.]+", " ", text.lower())
        tokens = [t for t in cleaned.split() if len(t) > 1 or t in {"c", "r"}]
        return tokens

    def search(self, query: str, top_n: int = 50) -> List[Tuple[str, float]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return []

        scores: List[Tuple[str, float]] = []
        for i, doc in enumerate(self.tokenized_corpus):
            doc_len = self.doc_lens[i]
            score = 0.0
            term_counts: Dict[str, int] = {}
            for t in doc:
                term_counts[t] = term_counts.get(t, 0) + 1

            for q in query_tokens:
                if q not in term_counts:
                    continue
                tf = term_counts[q]
                idf_val = self.idf.get(q, 0.0)
                denom = tf + self.k1 * (1.0 - self.b + self.b * (doc_len / max(1.0, self.avg_doc_len)))
                score += idf_val * (tf * (self.k1 + 1.0)) / denom

            if score > 0:
                scores.append((self.chunk_ids[i], score))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]

class HybridRetrievalService:
    _instance: Optional["HybridRetrievalService"] = None

    def __init__(self, data_file: Optional[str] = None, vectorstore_dir: Optional[str] = None):
        self.data_loader = DatasetLoaderService.get_instance(data_file)
        self.embedding_service = LocalEmbeddingService.get_instance()
        self.vectorstore_dir = vectorstore_dir or "data/vectorstore"

        self.jobs: Dict[str, StandardJobPosting] = {j.id: j for j in self.data_loader.get_all_postings()}
        self.all_chunks: List[JobChunk] = ChunkingService.chunk_all_jobs(list(self.jobs.values()))
        self.chunk_lookup: Dict[str, JobChunk] = {c.chunk_id: c for c in self.all_chunks}

        corpus = [c.content for c in self.all_chunks]
        chunk_ids = [c.chunk_id for c in self.all_chunks]
        self.bm25 = BM25Retriever(corpus=corpus, chunk_ids=chunk_ids)

    @classmethod
    def get_instance(cls, data_file: Optional[str] = None, vectorstore_dir: Optional[str] = None) -> "HybridRetrievalService":
        if cls._instance is None:
            cls._instance = cls(data_file, vectorstore_dir)
        return cls._instance

    def search(
        self,
        query: str,
        domain: Optional[str] = None,
        is_remote: Optional[bool] = None,
        top_k: int = 5,
        use_reranker: bool = True,
    ) -> SemanticSearchResponse:
        if not query or not query.strip():
            return SemanticSearchResponse(total_matches=0, query=query, results=[])

        dense_ranked_chunks = self._dense_search(query, top_n=60)
        sparse_ranked_chunks = self._sparse_search(query, top_n=60)

        fused_chunk_scores = self._reciprocal_rank_fusion(
            dense_ranked_chunks,
            sparse_ranked_chunks,
            k=60,
        )

        job_chunks_map: Dict[str, List[Tuple[JobChunk, float]]] = {}
        job_base_scores: Dict[str, float] = {}

        for chunk_id, rrf_score in fused_chunk_scores.items():
            chunk = self.chunk_lookup.get(chunk_id)
            if not chunk:
                continue

            job_id = chunk.job_id
            job = self.jobs.get(job_id)
            if not job:
                continue

            if domain and domain.lower() not in job.domain.lower():
                continue
            if is_remote is not None and job.is_remote != is_remote:
                continue

            if job_id not in job_chunks_map:
                job_chunks_map[job_id] = []
                job_base_scores[job_id] = 0.0

            job_chunks_map[job_id].append((chunk, rrf_score))
            job_base_scores[job_id] += rrf_score

        if not job_chunks_map:
            return SemanticSearchResponse(total_matches=0, query=query, results=[])

        sorted_job_ids = sorted(job_base_scores.keys(), key=lambda jid: job_base_scores[jid], reverse=True)
        candidate_job_ids = sorted_job_ids[:25]

        if use_reranker and candidate_job_ids:
            final_job_scores = self._cross_encoder_rerank(query, candidate_job_ids)
        else:
            final_job_scores = {jid: job_base_scores[jid] for jid in candidate_job_ids}

        ranked_jobs = sorted(final_job_scores.keys(), key=lambda jid: final_job_scores[jid], reverse=True)

        result_items: List[SemanticSearchResultItem] = []
        for jid in ranked_jobs[:top_k]:
            job = self.jobs[jid]
            matched_chunks_list = []
            for chunk, score in sorted(job_chunks_map[jid], key=lambda x: x[1], reverse=True)[:3]:
                snippet = chunk.content.split("\n")[0:3]
                matched_chunks_list.append(
                    MatchedChunkInfo(
                        chunk_type=chunk.chunk_type,
                        content_snippet=" | ".join(snippet),
                        score=round(score, 4),
                    )
                )

            norm_score = final_job_scores[jid]
            result_items.append(
                SemanticSearchResultItem(
                    job=job,
                    relevance_score=round(norm_score, 4),
                    matched_chunks=matched_chunks_list,
                )
            )

        return SemanticSearchResponse(
            total_matches=len(result_items),
            query=query,
            results=result_items,
        )

    def _dense_search(self, query: str, top_n: int = 60) -> List[Tuple[str, float]]:
        try:
            collection = self.embedding_service.get_collection("internship_chunks", self.vectorstore_dir)
            query_emb = self.embedding_service.get_embedding(query)
            results = collection.query(
                query_embeddings=[query_emb],
                n_results=min(top_n, collection.count()),
            )

            ids = results.get("ids", [[]])[0]
            distances = results.get("distances", [[]])[0]
            ranked = []
            for cid, dist in zip(ids, distances):
                sim = max(0.0, 1.0 - float(dist)) if dist is not None else 0.5
                ranked.append((cid, sim))
            return ranked
        except Exception:
            query_emb = self.embedding_service.get_embedding(query)
            ranked = []
            for chunk in self.all_chunks:
                chunk_emb = self.embedding_service.get_embedding(chunk.content)
                sim = self.embedding_service.cosine_similarity(query_emb, chunk_emb)
                ranked.append((chunk.chunk_id, sim))
            ranked.sort(key=lambda x: x[1], reverse=True)
            return ranked[:top_n]

    def _sparse_search(self, query: str, top_n: int = 60) -> List[Tuple[str, float]]:
        return self.bm25.search(query, top_n=top_n)

    def _reciprocal_rank_fusion(
        self,
        dense_results: List[Tuple[str, float]],
        sparse_results: List[Tuple[str, float]],
        k: int = 60,
    ) -> Dict[str, float]:
        rrf_scores: Dict[str, float] = {}

        for rank, (chunk_id, _) in enumerate(dense_results, start=1):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank))

        for rank, (chunk_id, _) in enumerate(sparse_results, start=1):
            rrf_scores[chunk_id] = rrf_scores.get(chunk_id, 0.0) + (1.0 / (k + rank))

        return rrf_scores

    def _cross_encoder_rerank(self, query: str, job_ids: List[str]) -> Dict[str, float]:
        candidate_texts = []
        for jid in job_ids:
            job = self.jobs[jid]
            skills = ", ".join(job.required_skills)
            text = f"Title: {job.job_title}. Company: {job.company}. Domain: {job.domain}. Required Skills: {skills}. Description: {job.job_description}"
            candidate_texts.append(text)

        raw_scores = self.embedding_service.rerank(query, candidate_texts)

        final_scores: Dict[str, float] = {}
        for jid, s in zip(job_ids, raw_scores):
            prob = 1.0 / (1.0 + math.exp(-s)) if abs(s) < 30 else (1.0 if s > 0 else 0.0)
            final_scores[jid] = prob

        return final_scores
