from pathlib import Path
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
        ("Sprint 2", "Sprint 2", "US-M2.3", "Job-Resume Matching Agent & Multi-Dimensional Scoring Engine", "Must Have", "US-M2.2", "Daksh Singh", "Completed"),
        ("Sprint 2", "Sprint 2", "US-M2.4", "Matching & Retrieval Systematic Evaluation Benchmark (Precision@5)", "Must Have", "US-M2.3", "Daksh Singh", "Completed"),
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
        ("US-M2.3", "TSK-M2.3-01", "Define CandidateProfile, MatchRequest, and ScoreBreakdown Pydantic v2 schemas", "2026-11-19", "2026-11-19", "Daksh Singh", "Development", "Completed", 4, 4),
        ("US-M2.3", "TSK-M2.3-02", "Implement JobResumeMatchingAgent with 5-facet weighted scoring (0-100)", "2026-11-19", "2026-11-19", "Daksh Singh", "AI Engineering", "Completed", 8, 8),
        ("US-M2.3", "TSK-M2.3-03", "Implement grounded reasoning engine with project citation & optional Ollama", "2026-11-19", "2026-11-19", "Daksh Singh", "AI Engineering", "Completed", 6, 6),
        ("US-M2.3", "TSK-M2.3-04", "Expose FastAPI POST /api/v1/jobs/match and /match-resume endpoints", "2026-11-19", "2026-11-19", "Daksh Singh", "Development", "Completed", 4, 4),
        ("US-M2.3", "TSK-M2.3-05", "Author and execute comprehensive matching verification test suite", "2026-11-19", "2026-11-19", "Daksh Singh", "Testing", "Completed", 4, 4),
        ("US-M2.4", "TSK-M2.4-01", "Author 5 diverse student profile evaluation fixtures with ground-truth criteria", "2026-11-19", "2026-11-19", "Daksh Singh", "Data Engineering", "Completed", 4, 4),
        ("US-M2.4", "TSK-M2.4-02", "Implement automated evaluation benchmark script (tests/evaluate_m2_pipeline.py)", "2026-11-19", "2026-11-19", "Daksh Singh", "Testing", "Completed", 6, 6),
        ("US-M2.4", "TSK-M2.4-03", "Compute Precision@5, score determinism, and zero-hallucination accuracy metrics", "2026-11-19", "2026-11-19", "Daksh Singh", "AI Engineering", "Completed", 4, 4),
        ("US-M2.4", "TSK-M2.4-04", "Generate comprehensive evaluation report (docs/M2_EVALUATION_REPORT.md)", "2026-11-19", "2026-11-19", "Daksh Singh", "Documentation", "Completed", 3, 3),
        ("US-M2.4", "TSK-M2.4-05", "Update Agile tracker and Unit Test Plan with M2.4 sign-off and retrospective", "2026-11-19", "2026-11-19", "Daksh Singh", "Project Mgmt", "Completed", 3, 3),
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
        ("Sprint 2", "Day 3", "Implement JobResumeMatchingAgent with 5-facet scoring, project citation reasoning, and match endpoints", "All M2.3 tests passed with 100% success; verified strict score descending order and grounded non-hallucinated explanations"),
        ("Sprint 2", "Day 4", "Execute systematic M2.4 evaluation benchmark across 5 diverse profiles (Precision@5, determinism, reasoning)", "Mean RAG Precision@5 = 100.0%, Matching Precision@5 = 92.0%, 0% hallucination rate, 100% deterministic; Milestone 2 complete"),
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
    sheet_retro.write(2, 5, "Fusing dense vector embeddings with BM25 keyword search via RRF k=60 and evaluating multi-dimensional match scores")
    sheet_retro.write(2, 6, "Opaque single-number match scores; replaced with transparent 5-facet ScoreBreakdown and project citations")
    sheet_retro.write(2, 7, "Rigorous automated benchmark suites, Pydantic v2 schemas, zero-comment clean code, and local-first ChromaDB vectorstore")
    sheet_retro.write(2, 8, "Milestone 2 fully completed and signed off: 175 postings, 700 chunks, hybrid RAG (100% P@5), matching agent (92% P@5), and evaluation report")

    wb.save(str(xls_path))
    print(f"Successfully updated Agile Tracker at {xls_path}")

if __name__ == "__main__":
    update_agile_tracker()
