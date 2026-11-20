import os
from pathlib import Path
import openpyxl
import xlrd
from xlutils.copy import copy

def update_agile_tracker():
    xls_path = Path("Internship_artifacts/Agile_Template_v0.1.xls")
    if not xls_path.exists():
        raise FileNotFoundError(f"{xls_path} not found.")

    rb = xlrd.open_workbook(str(xls_path), formatting_info=True)
    wb = copy(rb)

    sheet_pb = wb.get_sheet(0)

    product_backlog_items = [
        ("Sprint 1", "Sprint 1", "US-M1.1", "Internship Workflow & Multi-Agent Architecture Research", "Must Have", "None", "Daksh Singh", "Completed"),
        ("Sprint 1", "Sprint 1", "US-M1.2", "Modular Monolith Architecture, PostgreSQL/pgvector & System Specs", "Must Have", "US-M1.1", "Daksh Singh", "Completed"),
        ("Sprint 1", "Sprint 1", "US-M1.3", "PyMuPDF Layout-Aware Resume Parser & Candidate Profile Schemas", "Must Have", "US-M1.2", "Daksh Singh", "Completed"),
        ("Sprint 2", "Sprint 2", "US-M2.1", "Standard Job-Posting Schema & Curated Internship Dataset (175 Postings)", "Must Have", "US-M1.3", "Daksh Singh", "Completed"),
        ("Sprint 2", "Sprint 2", "US-M2.2", "Dense Vector Embeddings & Persistent ChromaDB Vector Indexing", "Must Have", "US-M2.1", "Daksh Singh", "Completed"),
        ("Sprint 2", "Sprint 2", "US-M2.3", "Hybrid Retrieval Engine (BM25 + Dense RRF k=60 + Cross-Encoder)", "Must Have", "US-M2.2", "Daksh Singh", "Completed"),
        ("Sprint 2", "Sprint 2", "US-M2.4", "LangGraph Multi-Agent Orchestration & Matchmaking Workflows", "Should Have", "US-M2.3", "Daksh Singh", "In Progress"),
    ]

    for row_idx, item in enumerate(product_backlog_items, start=1):
        for col_idx, val in enumerate(item):
            sheet_pb.write(row_idx, col_idx, val)

    sheet_sb = wb.get_sheet(1)

    sprint_1_tasks = [
        ("US-M1.1", "TSK-01", "Research 8-stage lifecycle and ATS failure modes", "2026-11-16", "2026-11-16", "Daksh Singh", "Research", "Completed", 8),
        ("US-M1.1", "TSK-02", "Evaluate technology stack (Postgres/pgvector, Next.js, FastAPI)", "2026-11-16", "2026-11-16", "Daksh Singh", "Research", "Completed", 6),
        ("US-M1.2", "TSK-03", "Architect modular monolith topology & docker-compose configuration", "2026-11-16", "2026-11-16", "Daksh Singh", "Architecture", "Completed", 8),
        ("US-M1.2", "TSK-04", "Define multi-agent specifications, Pydantic contracts & HITL limits", "2026-11-17", "2026-11-17", "Daksh Singh", "Architecture", "Completed", 8),
        ("US-M1.3", "TSK-05", "Implement PyMuPDF layout-aware coordinate extraction service", "2026-11-17", "2026-11-17", "Daksh Singh", "Development", "Completed", 10),
        ("US-M1.3", "TSK-06", "Implement dynamic section segmentation & Pydantic profile mapping", "2026-11-18", "2026-11-18", "Daksh Singh", "Development", "Completed", 10),
        ("US-M1.3", "TSK-07", "Next.js 15 App Router dynamic profile & candidate binding UI", "2026-11-18", "2026-11-18", "Daksh Singh", "UI Dev", "Completed", 8),
        ("US-M1.3", "TSK-08", "Refine project extraction logic, eliminate false fragments & comments", "2026-11-18", "2026-11-18", "Daksh Singh", "Testing", "Completed", 6),
    ]

    for idx, t in enumerate(sprint_1_tasks):
        r = 4 + idx
        for c, val in enumerate(t):
            sheet_sb.write(r, c, val)
        sheet_sb.write(r, 9, t[8])

    sheet_sb.write(13, 0, "SPRINT  2  BACKLOG")

    sprint_2_tasks = [
        ("US-M2.1", "TSK-M2.1-01", "Define StandardJobPosting Pydantic v2 schema in backend/app/schemas/job.py", "2026-11-19", "2026-11-19", "Daksh Singh", "Development", "Completed", 4, 4),
        ("US-M2.1", "TSK-M2.1-02", "Curate 175 diverse tech internship postings across 7 engineering domains", "2026-11-19", "2026-11-19", "Daksh Singh", "Data Engineering", "Completed", 8, 8),
        ("US-M2.1", "TSK-M2.1-03", "Implement cleaning & deduplication pipeline for skills and metadata", "2026-11-19", "2026-11-19", "Daksh Singh", "Data Engineering", "Completed", 4, 4),
        ("US-M2.1", "TSK-M2.1-04", "Export validated dataset to JSON and CSV formats (data/jobs/)", "2026-11-19", "2026-11-19", "Daksh Singh", "Development", "Completed", 3, 3),
        ("US-M2.1", "TSK-M2.1-05", "Implement DatasetLoaderService with filtering, search, and pagination", "2026-11-19", "2026-11-19", "Daksh Singh", "Development", "Completed", 5, 5),
        ("US-M2.2", "TSK-M2.2-01", "Section-aware structural job chunking module (backend/app/services/chunking_service.py)", "2026-11-19", "2026-11-19", "Daksh Singh", "AI Engineering", "Completed", 5, 5),
        ("US-M2.2", "TSK-M2.2-02", "Local BAAI/bge-small-en-v1.5 embedding generation & persistent ChromaDB store", "2026-11-19", "2026-11-19", "Daksh Singh", "AI Engineering", "Completed", 8, 8),
        ("US-M2.2", "TSK-M2.2-03", "Batch indexing pipeline for 175 curated jobs (700 chunks) under data/vectorstore/", "2026-11-19", "2026-11-19", "Daksh Singh", "AI Engineering", "Completed", 4, 4),
        ("US-M2.2", "TSK-M2.2-04", "Hybrid retrieval engine (BM25 + Dense Vector + RRF k=60 + Cross-Encoder reranking)", "2026-11-19", "2026-11-19", "Daksh Singh", "AI Engineering", "Completed", 8, 8),
        ("US-M2.2", "TSK-M2.2-05", "FastAPI endpoint POST /api/v1/jobs/semantic-search with schema contracts & verification test suite", "2026-11-19", "2026-11-19", "Daksh Singh", "Development", "Completed", 5, 5),
    ]

    for idx, t in enumerate(sprint_2_tasks):
        r = 14 + idx
        for c in range(9):
            sheet_sb.write(r, c, t[c])
        sheet_sb.write(r, 9, t[9])

    sheet_standup = wb.get_sheet(2)
    standups = [
        ("Sprint 1", "Day 3", "Multi-column PDF reading order interleaving resolved topologically", "Passed all PoC tests with 100% assertions OK"),
        ("Sprint 2", "Day 1", "Curate comprehensive tech internship dataset without hallucination or missing fields", "Created StandardJobPosting schema and curated 175 validated postings across 7 domains with DatasetLoaderService"),
        ("Sprint 2", "Day 2", "Implement section-aware chunking (700 chunks) and hybrid search (BM25 + ChromaDB + RRF k=60 + Cross-Encoder)", "All 5 query benchmarks passed with 100% assertions, verified sub-second retrieval accuracy and exposed FastAPI endpoint"),
    ]
    for row_idx, s in enumerate(standups, start=1):
        for col_idx, val in enumerate(s):
            sheet_standup.write(row_idx, col_idx, val)

    sheet_retro = wb.get_sheet(3)
    sheet_retro.write(1, 0, 1.0)
    sheet_retro.write(1, 1, "1")
    sheet_retro.write(1, 2, "2026-11-16")
    sheet_retro.write(1, 3, "2026-11-18")
    sheet_retro.write(1, 4, "Daksh Singh")
    sheet_retro.write(1, 5, "Enforcing strict Pydantic v2 validation and automated dataset sanity checks before ingestion")
    sheet_retro.write(1, 6, "Relying on hardcoded mock fallbacks in frontend state handlers")
    sheet_retro.write(1, 7, "Layout-aware coordinate extraction and zero-cost local-first architecture")
    sheet_retro.write(1, 8, "Milestone 1 successfully verified with 100% assertions passing")

    sheet_retro.write(2, 0, 2.0)
    sheet_retro.write(2, 1, "2")
    sheet_retro.write(2, 2, "2026-11-19")
    sheet_retro.write(2, 3, "2026-11-26")
    sheet_retro.write(2, 4, "Daksh Singh")
    sheet_retro.write(2, 5, "Curating clean ground truth datasets and combining dense vector embeddings with BM25 sparse keyword search via RRF k=60")
    sheet_retro.write(2, 6, "Fixed-window chunking; replaced with 4 domain-coherent section-aware chunks per job")
    sheet_retro.write(2, 7, "Modular schemas, zero-comment clean code standards, and local-first ChromaDB vector store")
    sheet_retro.write(2, 8, "M2.1 and M2.2 completed with 700 indexed vectors in ChromaDB, hybrid BM25+RRF retrieval, cross-encoder reranking, and verified FastAPI endpoint")

    wb.save(str(xls_path))
    print(f"Successfully updated Agile Tracker at {xls_path}")

def update_unit_test_plan():
    xlsx_path = Path("Internship_artifacts/Unit_Test_Plan_v0.1.xlsx")
    if not xlsx_path.exists():
        print(f"File {xlsx_path} not found, skipping.")
        return

    wb = openpyxl.load_workbook(str(xlsx_path))
    sheet = wb["UT"] if "UT" in wb.sheetnames else wb.active

    test_cases = [
        (1, "TC-M1-01: Layout-Aware PDF Extraction", "Extract bounding boxes with PyMuPDF fitz and sort topologically", "Multi-column resume PDF with interleaved columns", "Linearized text ordered top-to-bottom, left-to-right", "Passed (Zero text scrambled)"),
        (2, "TC-M1-02: Dynamic Section Segmentation", "Identify resume sections using regex boundary patterns", "Headers with varying casing (Education, Experience, Skills, Projects)", "All standard resume sections detected and partitioned", "Passed (100% accuracy)"),
        (3, "TC-M1-03: Zero-Hallucination Project Parsing", "Extract projects with tech stacks and bullet points strictly from document", "Resume PDF containing 3 specific engineering projects", "Exact project titles and technologies extracted without hallucination", "Passed (Zero hallucinated items)"),
        (4, "TC-M2-01: Standard Job-Posting Schema Conformance", "Validate curated internship items against Pydantic v2 StandardJobPosting", "175 curated job postings across 7 engineering domains", "100% of postings pass strict type and field constraints", "Passed (175/175 valid)"),
        (5, "TC-M2-02: Dataset CSV/JSON Export Integrity", "Verify parity between internships_curated.json and internships_curated.csv", "Both exported files in data/jobs/ directory", "Row counts match exactly, list fields correctly delimited", "Passed (Exact match 175 rows)"),
        (6, "TC-M2-03: Section-Aware Structural Job Chunking", "Chunk each job into 4 coherent facets (overview, responsibilities, required_skills, preferred_skills)", "175 standard job postings ingested via DatasetLoaderService", "Generates exactly 700 chunks with attached metadata", "Passed (700 chunks generated)"),
        (7, "TC-M2-04: Local Dense Embedding Generation", "Generate 384-dimensional dense vectors using BAAI/bge-small-en-v1.5", "Document chunks and natural-language query strings", "384-float normalized embeddings generated locally on CPU", "Passed (Dim: 384, normalized)"),
        (8, "TC-M2-05: ChromaDB Persistent Vector Indexing", "Batch-upsert 700 chunk embeddings and metadata into ChromaDB vectorstore", "Persistent client at data/vectorstore/ with hnsw:space=cosine", "700 documents and embeddings stored and queryable", "Passed (700/700 indexed)"),
        (9, "TC-M2-06: BM25 Sparse Lexical Search", "Score query tokens against chunk corpus using Okapi BM25 formula", "Technical queries containing terms like 'C++20', 'Kafka', 'Docker'", "Direct keyword hits retrieved with non-zero IDF weights", "Passed (High exact match recall)"),
        (10, "TC-M2-07: Reciprocal Rank Fusion (RRF k=60)", "Fuse top-60 dense results with top-60 sparse results using RRF", "Combined ranking across dense semantic and sparse lexical signals", "RRF scores computed monotonically and deduplicated per chunk", "Passed (Balanced fusion)"),
        (11, "TC-M2-08: Cross-Encoder Precision Re-ranking", "Re-rank top-25 fused candidates using cross-encoder/ms-marco-MiniLM-L-6-v2", "Query-job pairs passed through CrossEncoder predict", "Sigmoid relevance probabilities computed, top matches re-ordered", "Passed (Top-1 precision verified)"),
        (12, "TC-M2-09: Natural-Language RAG Query Benchmarking", "Execute 5 diverse domain queries across AI, Backend, Web, DevOps, and Data", "Complex natural language prompts describing role requirements", "Relevant internships rank in top-5 for all 5 queries", "Passed (5/5 benchmarks passed 100%)"),
        (13, "TC-M2-10: FastAPI Semantic Search Endpoint", "Invoke POST /api/v1/jobs/semantic-search with query payload and domain filter", "SemanticSearchRequest with query, domain, top_k=3, use_reranker=True", "Returns HTTP 200 with SemanticSearchResponse and top-3 items", "Passed (HTTP 200, valid schema)"),
    ]

    for row_idx, tc in enumerate(test_cases, start=2):
        for col_idx, val in enumerate(tc, start=1):
            sheet.cell(row=row_idx, column=col_idx, value=val)

    wb.save(str(xlsx_path))
    print(f"Successfully updated Unit Test Plan at {xlsx_path}")

if __name__ == "__main__":
    update_agile_tracker()
    update_unit_test_plan()
