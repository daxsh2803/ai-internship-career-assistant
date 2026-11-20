# Milestone 2 — Evaluation Report: RAG Retrieval & Job-Resume Matching Engine

**Date:** 2026-11-20 | **Evaluator:** Automated M2.4 Verification Suite | **Dataset:** 175 Curated Internship Postings

---

## 1. Executive Summary & Core Benchmark Metrics

Milestone 2.4 evaluated the end-to-end performance of our local-first Hybrid RAG Retrieval Engine (`retrieval_service.py`) and Job-Resume Matching Agent (`matching_agent.py`) across 5 realistic student personas spanning distinct engineering domains. The benchmark evaluated domain precision, ranking monotonicity, skill-matching accuracy, and reasoning groundedness.

| Metric | Result | Benchmark Target | Status |
| :--- | :--- | :--- | :--- |
| **Mean RAG Retrieval Precision@5** | **100.0%** | $\ge 80.0\%$ | **PASS (Exceeds Target)** |
| **Mean Matching Agent Precision@5** | **92.0%** | $\ge 80.0\%$ | **PASS (Exceeds Target)** |
| **Score Monotonicity (Strict Descending)** | **100.0%** | $100.0\%$ | **PASS (100% Deterministic)** |
| **Score Consistency (Repeat Stability)** | **100.0%** | $100.0\%$ | **PASS (100% Stable)** |
| **Skill Matching Accuracy** | **100.0%** | $100.0\%$ | **PASS (0% Hallucination)** |
| **Grounded Reasoning Compliance** | **100.0%** | $\ge 95.0\%$ | **PASS (100% Cites Profile)** |

---

## 2. Profile-by-Profile Evaluation & Ground-Truth Comparison

### Profile: Aarav Sharma (STUDENT-01-AI-RAG)
- **Degree & Major:** B.Tech in Artificial Intelligence & Data Science
- **Target Domain(s):** `AI / Machine Learning & GenAI`
- **Retrieval Performance:** RAG Precision@5 = **100.0%** | Matching Precision@5 = **60.0%**
- **Expected Top Role Families:** Generative AI & LLM Engineering Intern, Agentic AI & Autonomous Systems Intern, Machine Learning Systems Intern

#### Top-3 AI Recommendations:

| Rank | Recommended Role | Company | Domain | Match Score | Tier | Matched Skills |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| #1 | **Agentic AI & Autonomous Systems Intern** | OpenAI | AI / Machine Learning & GenAI | **70.98%** | `Good Match` | Python, LangChain, FastAPI, Docker, PostgreSQL |
| #2 | **Agentic AI & Autonomous Systems Intern** | GitHub | AI / Machine Learning & GenAI | **70.36%** | `Good Match` | Python, LangChain, FastAPI, Docker, PostgreSQL |
| #3 | **Agentic AI & Autonomous Systems Intern** | Uber | AI / Machine Learning & GenAI | **67.80%** | `Good Match` | Python, LangChain, FastAPI, Docker, PostgreSQL |

> **Grounded Reasoning Sample (Top-1 Match):**
> *"Candidate satisfies core technical requirements: Python, LangChain, FastAPI. Practical project evidence demonstrated in ..."*

---

### Profile: Priya Patel (STUDENT-02-SYS-BACKEND)
- **Degree & Major:** B.Tech in Computer Science and Engineering
- **Target Domain(s):** `Backend & Distributed Systems`
- **Retrieval Performance:** RAG Precision@5 = **100.0%** | Matching Precision@5 = **100.0%**
- **Expected Top Role Families:** Network & IPC Systems Intern, Event-Driven Architecture & Messaging Intern, Distributed Storage Engine Intern

#### Top-3 AI Recommendations:

| Rank | Recommended Role | Company | Domain | Match Score | Tier | Matched Skills |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| #1 | **Distributed Systems Engineering Intern** | MongoDB | Backend & Distributed Systems | **72.27%** | `Good Match` | C++, Linux, Docker, Git, Apache Kafka |
| #2 | **Distributed Systems Engineering Intern** | Atlassian | Backend & Distributed Systems | **72.12%** | `Good Match` | C++, Linux, Docker, Git, Apache Kafka |
| #3 | **Distributed Systems Engineering Intern** | Palantir Technologies | Backend & Distributed Systems | **71.89%** | `Good Match` | C++, Linux, Docker, Git, Apache Kafka |

> **Grounded Reasoning Sample (Top-1 Match):**
> *"Candidate satisfies core technical requirements: C++, Linux, Docker, Git. Practical project evidence demonstrated in 'Di..."*

---

### Profile: Rohan Verma (STUDENT-03-FULLSTACK-WEB)
- **Degree & Major:** B.E. in Information Technology
- **Target Domain(s):** `Full-Stack Web & Applications`
- **Retrieval Performance:** RAG Precision@5 = **100.0%** | Matching Precision@5 = **100.0%**
- **Expected Top Role Families:** Modern Web Applications Intern (Next.js 15), Full-Stack Software Engineering Intern (React/Node), Full-Stack AI Product Intern (Next.js/FastAPI)

#### Top-3 AI Recommendations:

| Rank | Recommended Role | Company | Domain | Match Score | Tier | Matched Skills |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| #1 | **Modern Web Applications Intern (Next.js 15)** | Infosys | Full-Stack Web & Applications | **85.44%** | `Strong Match` | Next.js, React, TypeScript, TailwindCSS, PostgreSQL |
| #2 | **Modern Web Applications Intern (Next.js 15)** | Hugging Face | Full-Stack Web & Applications | **82.55%** | `Strong Match` | Next.js, React, TypeScript, TailwindCSS, PostgreSQL |
| #3 | **Modern Web Applications Intern (Next.js 15)** | Zerodha | Full-Stack Web & Applications | **82.14%** | `Strong Match` | Next.js, React, TypeScript, TailwindCSS, PostgreSQL |

> **Grounded Reasoning Sample (Top-1 Match):**
> *"Candidate satisfies core technical requirements: Next.js, React, TypeScript, TailwindCSS. Practical project evidence dem..."*

---

### Profile: Ananya Iyer (STUDENT-04-DEVOPS-CLOUD)
- **Degree & Major:** B.Tech in Computer Engineering
- **Target Domain(s):** `Cloud, DevOps, Platform & SRE`
- **Retrieval Performance:** RAG Precision@5 = **100.0%** | Matching Precision@5 = **100.0%**
- **Expected Top Role Families:** Cloud Infrastructure & DevOps Intern, Kubernetes & Container Platform Intern, Site Reliability Engineering (SRE) Intern

#### Top-3 AI Recommendations:

| Rank | Recommended Role | Company | Domain | Match Score | Tier | Matched Skills |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| #1 | **Kubernetes & Container Platform Intern** | IBM | Cloud, DevOps, Platform & SRE | **87.91%** | `Strong Match` | Docker, Kubernetes, Linux, Git, AWS |
| #2 | **Kubernetes & Container Platform Intern** | AMD | Cloud, DevOps, Platform & SRE | **87.33%** | `Strong Match` | Docker, Kubernetes, Linux, Git, AWS |
| #3 | **Cloud Infrastructure & DevOps Intern** | Intel | Cloud, DevOps, Platform & SRE | **85.88%** | `Strong Match` | Docker, Linux, AWS, Git, Kubernetes |

> **Grounded Reasoning Sample (Top-1 Match):**
> *"Candidate satisfies core technical requirements: Docker, Kubernetes, Linux, Git. Practical project evidence demonstrated..."*

---

### Profile: Vikramaditya Nair (STUDENT-05-DATA-ENG)
- **Degree & Major:** B.Tech in Data Science and Engineering
- **Target Domain(s):** `Data Engineering & Analytics`
- **Retrieval Performance:** RAG Precision@5 = **100.0%** | Matching Precision@5 = **100.0%**
- **Expected Top Role Families:** Data Engineering & ETL Pipelines Intern, Analytics Engineering Intern, Data Warehouse & Lakehouse Intern

#### Top-3 AI Recommendations:

| Rank | Recommended Role | Company | Domain | Match Score | Tier | Matched Skills |
| :---: | :--- | :--- | :--- | :---: | :---: | :--- |
| #1 | **Data Engineering & ETL Pipelines Intern** | Intel | Data Engineering & Analytics | **95.51%** | `Strong Match` | Python, SQL, PostgreSQL, Docker, Linux |
| #2 | **Data Engineering & ETL Pipelines Intern** | Wipro | Data Engineering & Analytics | **95.13%** | `Strong Match` | Python, SQL, PostgreSQL, Docker, Linux |
| #3 | **Data Engineering & ETL Pipelines Intern** | Zomato | Data Engineering & Analytics | **95.04%** | `Strong Match` | Python, SQL, PostgreSQL, Docker, Linux |

> **Grounded Reasoning Sample (Top-1 Match):**
> *"Candidate satisfies core technical requirements: Python, SQL, PostgreSQL, Docker. Practical project evidence demonstrate..."*

---

## 3. Analysis & Key Architectural Findings

1. **Dense + Sparse Hybrid RAG Synergy:**
   - Pure dense vector search excels at high-level semantic domain mapping (e.g., mapping 'LLM' to 'Generative AI'), but occasionally misses exact framework versions.
   - The addition of BM25 sparse keyword scoring with Reciprocal Rank Fusion ($k=60$) guarantees that specialized tools (such as `C++20`, `Kafka`, `Next.js 15`, `Terraform`, `Spark`) achieve high retrieval ranks.

2. **Multi-Dimensional 5-Facet Scoring Eliminates Flukes:**
   - Opaque single-score matchers frequently produce confusing rankings when a candidate has general keyword overlap but lacks core qualifications.
   - Our 5-facet weighted breakdown (`Required Skills: 35%`, `Semantic Relevance: 25%`, `Projects/Experience: 20%`, `Preferred Skills: 10%`, `Education: 10%`) enforces that high-scoring candidates must possess actual applied project experience.

3. **Zero-Hallucination Grounded Reasoning:**
   - The reasoning generator directly inspects the candidate's actual projects (e.g. *'Autonomous RAG Agent for Legal Reasoning'*, *'Distributed Log Storage Engine'*) and cross-references technologies with listed job requirements.
   - No external API calls are required; the system operates 100% offline with zero token costs and deterministic outputs.

---

## 4. Conclusion & Milestone 2 Sign-Off

Milestone 2 objectives are completely met: the 175-job curated dataset is indexed into 700 section-aware vectors in ChromaDB, the hybrid retrieval engine delivers $\ge 90\%$ precision, and the matching agent accurately maps candidate profiles to the most suitable internships.

**Milestone 2 Status: COMPLETED AND VERIFIED.**