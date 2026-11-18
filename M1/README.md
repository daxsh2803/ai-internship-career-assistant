# AI-Powered Internship Application and Career Assistance Platform

**Milestone 1 — Foundation & Candidate Understanding (Completed & Verified)**

A local-first, zero-cost AI platform designed to empower students through automated internship discovery, ATS-resilient resume tailoring, skill gap diagnostics, and interactive mock interview preparation.

---

## 1. Milestone 1 Overview & Scope

Milestone 1 establishes the research foundations, complete system architecture, data models, and empirical proof-of-concept (PoC) validation for the platform:

- **M1.1 Research & Technical Understanding:** Comprehensive analysis of the 8-stage internship application lifecycle, ATS friction points (addressing Harvard Business School's finding that 88% of surveyed employers acknowledge automated screening filters out qualified high-skills candidates), RAG retrieval patterns, multi-agent coordination topologies, and a zero-cost local technology stack evaluation across 11 technical domains.
- **M1.2 System Architecture Design:** Production specifications for an 8-layer local topology, granular input/output contracts for 6 specialized AI agents, unified PostgreSQL 16 + `pgvector` relational and vector schema with HNSW cosine indexes, and an end-to-end data flow from PDF upload to dense semantic embedding.
- **M1.3 Proof of Concept (PoC) Implementation:** Four deterministic validation scripts verifying PyMuPDF layout-aware coordinate extraction, Pydantic v2 candidate profile parsing, two-stage hybrid retrieval (BM25 + dense embeddings via RRF $k=60$), and compiled LangGraph multi-agent state graph transitions.

---

## 2. Repository Structure

```
.
├── docs/
│   ├── research/                             # M1.1 Research Deliverables
│   │   ├── internship-workflow.md            # 8-stage application lifecycle & ATS analysis
│   │   ├── rag-architecture.md               # Chunking, MTEB benchmarks, hybrid search & RAG Triad
│   │   ├── multi-agent-patterns.md           # Hub-and-spoke supervisor & 6 agent specifications
│   │   ├── technology-evaluation.md          # Zero-cost local-first stack evaluation (11 domains)
│   │   └── M1.1-summary.md                   # Synthesis of research findings & risk mitigations
│   └── architecture/                         # M1.2 & M1.3 Architecture Deliverables
│       ├── system-architecture.md            # 8-layer local system topology & Docker model
│       ├── agent-specifications.md           # Pydantic contracts, tools, & state graph flows
│       ├── data-schema.md                    # PostgreSQL 16 + pgvector DDL, ER diagram, indexes
│       ├── data-flow.md                      # Step-by-step PDF ingestion & embedding pipeline
│       ├── M1.2-summary.md                   # System architecture executive synthesis
│       └── M1.3-poc-results.md               # Empirical PoC execution metrics & validation report
├── tests/
│   └── poc/                                  # M1.3 Proof of Concept Validation Scripts
│       ├── sample_multicolumn_resume.pdf     # Realistic two-column synthetic student CV
│       ├── test_pdf_extraction.py            # PoC 1: PyMuPDF bounding-box column sorting
│       ├── test_profile_parsing.py           # PoC 2: Structured Pydantic v2 candidate models
│       ├── test_hybrid_matching.py           # PoC 3: Dense vector + BM25 + RRF (k=60) retrieval
│       └── test_agent_graph.py               # PoC 4: Compiled LangGraph StateGraph pipeline
├── docker-compose.yml                        # Local multi-container development configuration
├── requirements.txt                          # Python dependencies specification
└── PROJECT_STATUS.md                         # Milestone tracking and delivery roadmap
```

---

## 3. Milestone 1 Deliverables Index

### M1.1 Research & Technical Understanding
| Document | Description | Status |
| :--- | :--- | :---: |
| [internship-workflow.md](docs/research/internship-workflow.md) | 8-stage lifecycle analysis, ATS exclusion analysis (HBS Fuller et al., 2021), illustrative KPI targets. | **Completed** |
| [rag-architecture.md](docs/research/rag-architecture.md) | Section-aware chunking, verified MTEB benchmarks, hybrid search (HNSW + BM25 via RRF), RAG Triad guardrails. | **Completed** |
| [multi-agent-patterns.md](docs/research/multi-agent-patterns.md) | Multi-agent pattern comparison, hub-and-spoke supervisor, 6 agent role specifications, HITL breakpoints. | **Completed** |
| [technology-evaluation.md](docs/research/technology-evaluation.md) | Evaluation across 11 technical domains justifying the zero-cost, local-first stack. | **Completed** |
| [M1.1-summary.md](docs/research/M1.1-summary.md) | Synthesis of technical findings, risk analysis, and architectural guardrails. | **Completed** |

### M1.2 System Architecture Design
| Document | Description | Status |
| :--- | :--- | :---: |
| [system-architecture.md](docs/architecture/system-architecture.md) | 8-layer local topology, single `docker-compose.yml` model, security and path traversal guards. | **Completed** |
| [agent-specifications.md](docs/architecture/agent-specifications.md) | Strict Pydantic input/output contracts, tools, RAG needs, and workflows for all 6 agents. | **Completed** |
| [data-schema.md](docs/architecture/data-schema.md) | Unified PostgreSQL 16 DDL with `pgvector`, HNSW cosine indexes (`m=16, ef=64`), GIN full-text index, ER diagram. | **Completed** |
| [data-flow.md](docs/architecture/data-flow.md) | Step-by-step resume ingestion data flow from raw upload to vector embedding and persistence. | **Completed** |
| [M1.2-summary.md](docs/architecture/M1.2-summary.md) | Architecture synthesis and Milestone 1.3 transition roadmap. | **Completed** |

### M1.3 Proof of Concept (PoC) Validation
| Script | Validation Objective | Result |
| :--- | :--- | :---: |
| [test_pdf_extraction.py](tests/poc/test_pdf_extraction.py) | Validates PyMuPDF bounding-box grouping ($x_1 \le 230\text{pt}$) and vertical sorting, preventing column-interleaving errors on two-column resumes. | **PASSED** (Exit Code 0) |
| [test_profile_parsing.py](tests/poc/test_profile_parsing.py) | Validates Pydantic v2 candidate profile schemas, field constraints (GPA $0.00-4.00$, graduation years $2024-2032$), and error trapping. | **PASSED** (Exit Code 0) |
| [test_hybrid_matching.py](tests/poc/test_hybrid_matching.py) | Validates BM25 lexical scoring, dense vector cosine similarity (`bge-small-en-v1.5`), and Reciprocal Rank Fusion ($k=60$), ranking backend candidates top-2. | **PASSED** (Exit Code 0) |
| [test_agent_graph.py](tests/poc/test_agent_graph.py) | Validates a compiled LangGraph `StateGraph` running a sequential pipeline from Matching Agent to Skill Gap Agent with state passing. | **PASSED** (Exit Code 0) |
| [M1.3-poc-results.md](docs/architecture/M1.3-poc-results.md) | Complete empirical results report documenting test outputs, timings, and implementation findings. | **Completed** |

---

## 4. Running Proof of Concept (PoC) Validations

All PoC test scripts run deterministically in local CPU environments:

```bash
# 1. Test layout-aware PDF coordinate extraction
python tests/poc/test_pdf_extraction.py

# 2. Test structured Pydantic v2 candidate profile validation
python tests/poc/test_profile_parsing.py

# 3. Test two-stage hybrid retrieval & RRF re-ranking
python tests/poc/test_hybrid_matching.py

# 4. Test LangGraph multi-agent sequential pipeline execution
python tests/poc/test_agent_graph.py
```

---

## 5. Architectural Principles & Guarantees

1. **Zero-Cost Operation ($0.00):** Developed and operable entirely using open-source local technologies (PostgreSQL 16 + pgvector, Sentence-Transformers on CPU, Ollama, FastAPI, and Next.js 15). No paid cloud APIs, subscriptions, or credit card dependencies.
2. **Local Privacy Boundary:** Candidate biographical and academic information remains strictly on the local developer workstation when running the local Ollama and CPU embedding stack.
3. **Deterministic Retrieval & Grounding:** Eliminates hallucination in career advice by enforcing section-aware chunking and verified two-stage hybrid search before context injection into LLM prompts.
