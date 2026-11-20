import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.schemas.job import SemanticSearchRequest, SemanticSearchResponse
from app.services.chunking_service import ChunkingService
from app.services.dataset_loader import DatasetLoaderService
from app.services.embedding_service import LocalEmbeddingService
from app.services.retrieval_service import HybridRetrievalService

def test_chunking_module():
    loader = DatasetLoaderService.get_instance(Path("data/jobs/internships_curated.json"))
    jobs = loader.get_all_postings()
    assert len(jobs) == 175, f"Expected 175 jobs, got {len(jobs)}"

    chunks = ChunkingService.chunk_all_jobs(jobs)
    assert len(chunks) == 175 * 4, f"Expected {175 * 4} chunks, got {len(chunks)}"

    chunk_types = {c.chunk_type for c in chunks}
    expected_types = {"overview", "responsibilities", "required_skills", "preferred_skills"}
    assert chunk_types == expected_types, f"Mismatch in chunk types: {chunk_types}"

    for chunk in chunks[:10]:
        assert chunk.chunk_id
        assert chunk.job_id
        assert chunk.content
        assert "job_title" in chunk.metadata
        assert "company" in chunk.metadata
        assert "domain" in chunk.metadata
        assert "required_skills" in chunk.metadata
    print(f"[PASSED] Chunking Service: 175 jobs successfully chunked into {len(chunks)} section-aware chunks.")

def test_vectorstore_persistence():
    embedding_service = LocalEmbeddingService.get_instance()
    collection = embedding_service.get_collection("internship_chunks", "data/vectorstore")
    count = collection.count()
    assert count == 700, f"Expected 700 indexed chunks in vectorstore, got {count}"
    print(f"[PASSED] Vectorstore Persistence: ChromaDB contains {count} indexed vectors.")

def test_retrieval_queries():
    retrieval_service = HybridRetrievalService.get_instance(
        data_file="data/jobs/internships_curated.json",
        vectorstore_dir="data/vectorstore",
    )

    queries = [
        {
            "query": "distributed systems in C++ Kafka high throughput storage",
            "expected_skills": ["C++", "Kafka"],
            "expected_domains": ["Backend & Distributed Systems", "Systems Software"],
        },
        {
            "query": "Python RAG LangChain AI intern large language models generative AI",
            "expected_skills": ["Python", "LangChain", "PyTorch"],
            "expected_domains": ["AI / Machine Learning & GenAI"],
        },
        {
            "query": "React Next.js full-stack software engineer intern TypeScript Tailwind",
            "expected_skills": ["React", "Next.js", "TypeScript"],
            "expected_domains": ["Full-Stack Web & Applications"],
        },
        {
            "query": "AWS Docker DevOps cloud infrastructure CI/CD kubernetes SRE",
            "expected_skills": ["Docker", "AWS", "Kubernetes", "CI/CD"],
            "expected_domains": ["Cloud, DevOps, Platform & SRE"],
        },
        {
            "query": "Data Engineering with PostgreSQL ETL data pipelines analytics Spark",
            "expected_skills": ["PostgreSQL", "Python", "SQL", "Spark"],
            "expected_domains": ["Data Engineering & Analytics"],
        },
    ]

    print("\n" + "=" * 80)
    print("NATURAL-LANGUAGE RAG HYBRID SEARCH VERIFICATION (TOP-5 MATCHES)")
    print("=" * 80)

    for idx, q_spec in enumerate(queries, start=1):
        query = q_spec["query"]
        print(f"\n--- Query #{idx}: '{query}' ---")

        response = retrieval_service.search(
            query=query,
            top_k=5,
            use_reranker=True,
        )

        assert isinstance(response, SemanticSearchResponse)
        assert len(response.results) > 0, f"Query '{query}' yielded 0 results"
        assert response.total_matches == len(response.results)

        top_match = response.results[0]
        print(f"Top-1 Match: {top_match.job.job_title} @ {top_match.job.company} | Score: {top_match.relevance_score:.4f} | Domain: {top_match.job.domain}")
        print(f"Required Skills: {', '.join(top_match.job.required_skills)}")
        for mc in top_match.matched_chunks[:2]:
            print(f"  * [{mc.chunk_type}] {mc.content_snippet[:100]}... (Score: {mc.score:.4f})")

        print("Top 5 Results:")
        for rank, res in enumerate(response.results, start=1):
            print(f"  #{rank}: [{res.relevance_score:.4f}] {res.job.job_title} ({res.job.company}) - Domain: {res.job.domain}")

        has_skill_match = any(
            any(req_s.lower() in [s.lower() for s in res.job.required_skills + res.job.preferred_skills]
                for req_s in q_spec["expected_skills"])
            for res in response.results
        )
        assert has_skill_match, f"Expected skills {q_spec['expected_skills']} not found in top 5 results for query '{query}'"

    print("\n" + "=" * 80)
    print("ALL 5 DIVERSE QUERY BENCHMARKS PASSED WITH 100% SUCCESS!")
    print("=" * 80)

def run_all_tests():
    print("======================================================================")
    print("MILESTONE 2 - STEP M2.2 RAG RETRIEVAL & SEMANTIC SEARCH TEST SUITE")
    print("======================================================================")
    test_chunking_module()
    test_vectorstore_persistence()
    test_retrieval_queries()

if __name__ == "__main__":
    run_all_tests()

