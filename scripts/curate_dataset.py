import csv
import json
import os
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "backend"))
from app.schemas.job import StandardJobPosting

DOMAINS_DATA = [
    {
        "domain": "AI / Machine Learning & GenAI",
        "roles": [
            ("Generative AI & LLM Engineering Intern", ["Python", "LangChain", "LLMs", "FastAPI"], ["PyTorch", "Docker", "Groq", "Ollama"], "Develop and benchmark generative AI applications using state-of-the-art LLMs, prompt pipelines, and low-latency inference APIs."),
            ("RAG Systems & Vector Search Intern", ["Python", "Retrieval-Augmented Generation / RAG", "PostgreSQL", "pgvector"], ["LangChain", "Docker", "Redis", "FastAPI"], "Architect retrieval-augmented generation pipelines, evaluate dense embeddings, and optimize vector database retrieval with hybrid search."),
            ("Applied Computer Vision Intern", ["Python", "PyTorch", "Computer Vision", "OpenCV"], ["TensorFlow", "Docker", "C++", "Linux"], "Build deep learning vision models for object detection, segmentation, and multimodal visual reasoning."),
            ("NLP & Conversational AI Intern", ["Python", "NLP", "Hugging Face", "LLMs"], ["PyTorch", "FastAPI", "Streamlit", "Docker"], "Design dialogue management systems, token classification pipelines, and evaluate conversational agents."),
            ("Machine Learning Platform Intern", ["Python", "Docker", "Kubernetes", "Linux"], ["PyTorch", "AWS", "FastAPI", "Git"], "Construct scalable model training pipelines, containerized deployment infrastructure, and experiment tracking systems."),
            ("Deep Learning Research Intern", ["Python", "PyTorch", "Deep Learning", "NumPy"], ["TensorFlow", "C++", "Linux", "Git"], "Implement foundational neural network architectures, train attention-based models, and analyze generalization performance."),
            ("Agentic AI & Autonomous Systems Intern", ["Python", "LangChain", "LLMs", "FastAPI"], ["Docker", "Redis", "PostgreSQL", "Linux"], "Develop multi-agent collaboration frameworks with structured state graphs, tool-calling interfaces, and human-in-the-loop controls."),
            ("Speech & Audio Processing Intern", ["Python", "Deep Learning", "PyTorch", "Linux"], ["C++", "Docker", "FastAPI", "Git"], "Train and fine-tune speech recognition models, acoustic feature extraction pipelines, and low-latency audio inference engines."),
            ("AI Model Evaluation & Alignment Intern", ["Python", "LLMs", "Data Cleaning", "Pandas"], ["PyTorch", "FastAPI", "Streamlit", "Git"], "Establish benchmark evaluation suites for hallucination detection, toxic content filtering, and prompt robustness testing."),
            ("Recommendation Systems & Ranking Intern", ["Python", "SQL", "Scikit-Learn", "PostgreSQL"], ["PyTorch", "Redis", "Docker", "FastAPI"], "Optimize collaborative filtering and deep retrieval models for personalized content ranking and item candidate generation."),
        ]
    },
    {
        "domain": "Backend & Distributed Systems",
        "roles": [
            ("Backend Software Engineering Intern (FastAPI)", ["Python", "FastAPI", "PostgreSQL", "Docker"], ["Redis", "SQLAlchemy", "Linux", "Git"], "Design high-throughput asynchronous REST microservices using FastAPI, SQLAlchemy, and relational databases."),
            ("Distributed Systems Engineering Intern", ["C++", "Linux", "Docker", "Git"], ["Go", "C++20", "Apache Kafka", "CMake"], "Implement distributed consensus algorithms, replicated state machines, and high-performance network IPC protocols."),
            ("High-Performance Backend Intern (Go / gRPC)", ["Go", "Docker", "Linux", "PostgreSQL"], ["gRPC", "Redis", "Kubernetes", "Git"], "Build low-latency microservices with Go and gRPC, optimizing goroutine concurrency and database pooling."),
            ("Enterprise Backend Systems Intern (Java)", ["Java", "Spring Boot", "SQL", "Git"], ["PostgreSQL", "Docker", "AWS", "Linux"], "Engineer modular enterprise APIs using Java, Spring Boot, Hibernate ORM, and relational database migrations."),
            ("Database Kernel & Storage Systems Intern", ["C++", "C++20", "Linux", "CMake"], ["PostgreSQL", "Docker", "Python", "Git"], "Profile database buffer pools, storage engine block layouts, and write-ahead logging (WAL) serialization mechanics."),
            ("Event-Driven Architecture & Messaging Intern", ["Python", "Apache Kafka", "Docker", "Linux"], ["Redis", "PostgreSQL", "Go", "Git"], "Design streaming event processors, pub-sub messaging pipelines, and asynchronous dead-letter queue handlers."),
            ("Asynchronous Microservices Intern (Node.js)", ["TypeScript", "Node.js", "PostgreSQL", "Docker"], ["Redis", "FastAPI", "Linux", "Git"], "Develop non-blocking asynchronous APIs with Node.js and TypeScript, handling database transaction isolation."),
            ("Network & IPC Systems Intern", ["C++", "Linux", "Bash", "Git"], ["Docker", "Python", "CMake", "C++20"], "Profile network socket throughput, protocol buffers, and shared memory IPC mechanisms under heavy synthetic load."),
            ("Cloud Database Reliability Intern", ["SQL", "PostgreSQL", "Linux", "Python"], ["Docker", "AWS", "Redis", "Git"], "Automate database replication health checks, high availability failovers, and backup verification pipelines."),
            ("API Platform & Integration Intern", ["Python", "FastAPI", "SQL", "Git"], ["Docker", "PostgreSQL", "Redis", "Linux"], "Build developer-facing REST endpoints, OAuth2 token authentication flows, and interactive OpenAPI documentation."),
        ]
    },
    {
        "domain": "Full-Stack Web & Applications",
        "roles": [
            ("Full-Stack Software Engineering Intern (React/Node)", ["React", "TypeScript", "Node.js", "PostgreSQL"], ["Next.js", "Docker", "TailwindCSS", "Git"], "Develop modern responsive web applications with React, TypeScript, and Node.js backends with relational persistence."),
            ("Full-Stack AI Product Intern (Next.js/FastAPI)", ["Next.js", "React", "Python", "FastAPI"], ["TailwindCSS", "PostgreSQL", "Docker", "TypeScript"], "Build AI-assisted user experiences combining Next.js App Router frontends with high-speed FastAPI AI microservices."),
            ("Real-Time Collaborative Web Apps Intern", ["React", "TypeScript", "Socket.io", "Node.js"], ["Redis", "PostgreSQL", "Yjs", "Docker"], "Construct collaborative multiplayer canvas and editor interfaces using WebSockets, Socket.io, and operational transformation."),
            ("Modern Web Applications Intern (Next.js 15)", ["Next.js", "React", "TypeScript", "TailwindCSS"], ["PostgreSQL", "Docker", "Node.js", "Git"], "Implement performant server components, optimistic UI mutations, and state management using Next.js 15 and TailwindCSS."),
            ("Enterprise Web Platform Intern", ["Java", "React", "SQL", "Git"], ["Spring Boot", "TypeScript", "Docker", "PostgreSQL"], "Bridge backend Spring Boot business logic with responsive React single-page enterprise web portals."),
            ("Interactive Frontend & Data Visualization Intern", ["JavaScript", "TypeScript", "React", "HTML5"], ["Next.js", "TailwindCSS", "Python", "Git"], "Design dynamic data dashboards, interactive SVG charts, and responsive analytics interfaces for large-scale telemetry."),
            ("Frontend Systems & UI Components Intern", ["TypeScript", "React", "CSS3", "Git"], ["Next.js", "TailwindCSS", "Node.js", "Jest"], "Maintain design system component libraries, accessibility compliance (WCAG), and responsive cross-browser styling."),
            ("Web Performance & Client Architecture Intern", ["JavaScript", "React", "Next.js", "Git"], ["TypeScript", "Node.js", "Docker", "Linux"], "Audit frontend bundle size, client-side caching strategies, and Core Web Vitals across critical rendering paths."),
        ]
    },
    {
        "domain": "Data Engineering & Analytics",
        "roles": [
            ("Data Engineering & ETL Pipelines Intern", ["Python", "SQL", "PostgreSQL", "Docker"], ["Apache Kafka", "Linux", "Pandas", "Git"], "Construct robust automated ETL data pipelines, validating schema migrations and database transformation pipelines."),
            ("Analytics Engineering Intern", ["SQL", "Python", "PostgreSQL", "Git"], ["Pandas", "Docker", "Tableau", "Linux"], "Model dimensional data warehouses, author analytics queries, and curate metrics marts for reporting stakeholders."),
            ("Exploratory Data Science & EDA Intern", ["Python", "Pandas", "NumPy", "Exploratory Data Analysis / EDA"], ["Data Cleaning", "Matplotlib", "Scikit-Learn", "SQL"], "Perform exploratory data analysis on multi-dimensional tabular datasets, uncovering patterns and cleaning dirty telemetry."),
            ("Big Data Processing Intern", ["Python", "SQL", "Linux", "Git"], ["Docker", "Apache Kafka", "PostgreSQL", "Java"], "Develop batch and streaming data transformation jobs across distributed data storage environments."),
            ("Business Intelligence & Metrics Intern", ["SQL", "Data Cleaning", "Pandas", "Python"], ["Matplotlib", "PostgreSQL", "Git", "Tableau"], "Transform raw application event logs into structured metric dashboards, cohort retention tables, and revenue analytics."),
            ("Data Quality & Pipeline Validation Intern", ["Python", "SQL", "Data Cleaning", "Git"], ["PostgreSQL", "Docker", "Linux", "Pandas"], "Implement automated data assertion checks, anomaly detection on pipeline inputs, and data drift monitoring suites."),
        ]
    },
    {
        "domain": "Cloud, DevOps, Platform & SRE",
        "roles": [
            ("Cloud Infrastructure & DevOps Intern", ["Docker", "Linux", "AWS", "Git"], ["Kubernetes", "CI/CD", "GitHub Actions", "Python"], "Automate cloud infrastructure provisioning, containerize legacy workloads, and configure continuous integration workflows."),
            ("Kubernetes & Container Platform Intern", ["Docker", "Kubernetes", "Linux", "Git"], ["Go", "AWS", "CI/CD", "Bash"], "Deploy and manage containerized microservices across Kubernetes clusters, writing Helm charts and ingress configurations."),
            ("Site Reliability Engineering (SRE) Intern", ["Linux", "Python", "Bash", "Git"], ["Docker", "Kubernetes", "AWS", "CI/CD"], "Build telemetry dashboards, configure synthetic health monitors, and automate incident remediation procedures."),
            ("DevSecOps & Platform Security Intern", ["Linux", "Docker", "Git", "CI/CD"], ["AWS", "Python", "Bash", "Kubernetes"], "Scan container images for CVE vulnerabilities, automate secret rotation, and enforce zero-trust network policies."),
            ("CI/CD Automation & Build Systems Intern", ["Git", "GitHub Actions", "Docker", "Linux"], ["Python", "Bash", "CI/CD", "CMake"], "Maintain multi-stage build pipelines, automate integration test execution, and accelerate developer release cycles."),
            ("Cloud Operations & FinOps Intern", ["AWS", "Linux", "Python", "SQL"], ["Docker", "Bash", "Git", "CI/CD"], "Analyze cloud resource utilization metrics, identify idle compute capacity, and configure auto-scaling rules."),
        ]
    },
    {
        "domain": "Mobile & Systems Software",
        "roles": [
            ("Android Mobile Engineering Intern", ["Java", "Kotlin", "Android SDK", "Git"], ["REST APIs", "SQL", "Linux", "Docker"], "Develop responsive Android mobile views, manage background synchronization workers, and integrate REST APIs."),
            ("iOS Mobile Application Intern", ["Swift", "iOS SDK", "Git", "REST APIs"], ["Objective-C", "GraphQL", "Linux", "Python"], "Engineer native iOS user flows using modern Swift architectures, handling local storage and offline-first caching."),
            ("Embedded Systems & Firmware Intern", ["C", "C++", "Linux", "Git"], ["CMake", "RTOS", "Bash", "Python"], "Write hardware peripheral drivers, configure microcontroller timers, and debug UART/SPI serial communication."),
            ("Low-Level Systems & Kernel Intern", ["C++", "C++20", "Linux", "Git"], ["CMake", "Bash", "Docker", "Python"], "Profile memory allocators, analyze OS system call latency, and optimize multithreaded locks in C++20."),
        ]
    },
    {
        "domain": "Cybersecurity, Tooling & Quality Engineering",
        "roles": [
            ("Application Security & Penetration Testing Intern", ["Python", "Linux", "Git", "SQL"], ["Docker", "Bash", "AWS", "FastAPI"], "Audit web application source code for OWASP Top 10 vulnerabilities, verify input sanitization, and assess API security."),
            ("QA Automation & Testing Intern", ["Python", "pytest", "Git", "SQL"], ["Docker", "FastAPI", "Linux", "CI/CD"], "Write automated end-to-end integration test suites, mock third-party dependencies, and enforce code coverage standards."),
            ("Developer Productivity & Tooling Intern", ["Go", "Python", "Git", "Linux"], ["Docker", "Bash", "GitHub Actions", "CI/CD"], "Build CLI developer tools, formatters, and automated repository linter plugins to enhance engineering ergonomics."),
            ("Cloud Identity & Access Governance Intern", ["Python", "AWS", "Linux", "Git"], ["Docker", "SQL", "Bash", "CI/CD"], "Implement automated least-privilege IAM policy analyzers and review multi-tenant role assignments."),
        ]
    }
]

COMPANIES = [
    ("Google", "Bengaluru, India", "Hybrid", False, "₹85,000 / month"),
    ("Microsoft", "Hyderabad, India", "Hybrid", False, "₹80,000 / month"),
    ("Amazon Web Services (AWS)", "Bengaluru, India", "Hybrid", False, "₹80,000 / month"),
    ("Meta", "London, UK", "Hybrid", False, "£3,800 / month"),
    ("Apple", "Austin, TX", "On-site", False, "$52 / hour"),
    ("NVIDIA", "Pune, India", "Hybrid", False, "₹75,000 / month"),
    ("OpenAI", "San Francisco, CA", "Hybrid", False, "$60 / hour"),
    ("Anthropic", "San Francisco, CA", "On-site", False, "$60 / hour"),
    ("Databricks", "San Francisco, CA", "Hybrid", False, "$55 / hour"),
    ("Snowflake", "Seattle, WA", "Hybrid", False, "$54 / hour"),
    ("Cloudflare", "Remote (Global)", "Remote", True, "$48 / hour"),
    ("Stripe", "Remote (US)", "Remote", True, "$55 / hour"),
    ("Uber", "Bengaluru, India", "Hybrid", False, "₹75,000 / month"),
    ("Airbnb", "Remote (US)", "Remote", True, "$50 / hour"),
    ("Atlassian", "Bengaluru, India", "Remote", True, "₹70,000 / month"),
    ("GitHub", "Remote (Global)", "Remote", True, "$52 / hour"),
    ("Postman", "Bengaluru, India", "Hybrid", False, "₹65,000 / month"),
    ("MongoDB", "Dublin, Ireland", "Hybrid", False, "€3,400 / month"),
    ("Elastic", "Remote (US)", "Remote", True, "$48 / hour"),
    ("Redis", "Tel Aviv, Israel", "Hybrid", False, "$4,500 / month"),
    ("Palantir Technologies", "New York, NY", "On-site", False, "$55 / hour"),
    ("Scale AI", "San Francisco, CA", "On-site", False, "$52 / hour"),
    ("Pinecone", "New York, NY", "Hybrid", False, "$50 / hour"),
    ("Hugging Face", "Remote (Global)", "Remote", True, "$48 / hour"),
    ("Cohere", "Toronto, Canada", "Hybrid", False, "CAD $7,000 / month"),
    ("DeepMind", "London, UK", "Hybrid", False, "£4,200 / month"),
    ("Infosys", "Bengaluru, India", "Hybrid", False, "₹45,000 / month"),
    ("TCS", "Hyderabad, India", "On-site", False, "₹40,000 / month"),
    ("Wipro", "Pune, India", "Hybrid", False, "₹40,000 / month"),
    ("Razorpay", "Bengaluru, India", "Hybrid", False, "₹60,000 / month"),
    ("Swiggy", "Bengaluru, India", "Remote", True, "₹55,000 / month"),
    ("Zomato", "Gurugram, India", "On-site", False, "₹55,000 / month"),
    ("Zerodha", "Bengaluru, India", "Hybrid", False, "₹65,000 / month"),
    ("CRED", "Bengaluru, India", "On-site", False, "₹70,000 / month"),
    ("Flipkart", "Bengaluru, India", "Hybrid", False, "₹65,000 / month"),
    ("Adobe", "Noida, India", "Hybrid", False, "₹70,000 / month"),
    ("Cisco", "Bengaluru, India", "Hybrid", False, "₹65,000 / month"),
    ("Intel", "Bengaluru, India", "On-site", False, "₹60,000 / month"),
    ("AMD", "Hyderabad, India", "Hybrid", False, "₹62,000 / month"),
    ("Salesforce", "Hyderabad, India", "Hybrid", False, "₹75,000 / month"),
    ("Oracle", "Bengaluru, India", "Hybrid", False, "₹65,000 / month"),
    ("IBM", "Bengaluru, India", "Hybrid", False, "₹50,000 / month"),
    ("Canva", "Sydney, Australia", "Hybrid", False, "AUD $7,500 / month"),
    ("Figma", "San Francisco, CA", "Hybrid", False, "$54 / hour"),
    ("CrowdStrike", "Austin, TX", "Remote", True, "$48 / hour"),
]

def build_postings(target_count: int = 175) -> List[StandardJobPosting]:
    postings: List[StandardJobPosting] = []
    postings_set = set()
    job_idx = 1
    random.seed(42)

    all_domain_roles = []
    for d in DOMAINS_DATA:
        for r in d["roles"]:
            all_domain_roles.append((d["domain"], r))

    now = datetime(2026, 11, 15, 10, 0, 0)
    round_robin_idx = 0
    company_idx = 0

    while len(postings) < target_count:
        domain, role_info = all_domain_roles[round_robin_idx % len(all_domain_roles)]
        company_info = COMPANIES[company_idx % len(COMPANIES)]
        
        round_robin_idx += 1
        company_idx += 1

        title, req_skills, pref_skills, mission_desc = role_info
        company, loc, mode, is_remote, stipend = company_info

        key = (company, title, loc)
        if key in postings_set:
            title = f"{title} (Cohort {((job_idx % 3) + 1)})"
        postings_set.add(key)

        posted_time = now - timedelta(days=random.randint(1, 45), hours=random.randint(1, 23))

        qualifications = [
            "Currently enrolled in or recently graduated with a Bachelor's, Master's, or PhD in Computer Science, Data Science, Electrical Engineering, or related STEM field.",
            "Solid theoretical foundation in data structures, algorithms, and modular object-oriented software design.",
            "Demonstrated hands-on experience through academic projects, open-source repositories, or prior internships.",
            "Strong communication skills with proactive technical problem-solving capabilities."
        ]

        responsibilities = [
            f"Collaborate with senior staff engineers to design, implement, and maintain robust {domain} services.",
            f"Write clean, thoroughly tested code adhering to strict type safety and modular architecture.",
            f"Participate actively in agile sprint planning, daily stand-up meetings, and peer code reviews.",
            f"Profile execution bottlenecks and deliver measurable performance optimizations across core workloads."
        ]

        tags = list(dict.fromkeys([domain.split('/')[0].strip(), title.split()[0], req_skills[0]] + req_skills[:3] + [mode]))

        posting = StandardJobPosting(
            id=f"job_{job_idx:03d}",
            job_title=title,
            company=company,
            location=loc,
            work_mode=mode,
            is_remote=is_remote,
            job_description=f"{mission_desc} As a key technical intern at {company}, you will work alongside world-class engineers solving high-impact industry problems at scale.",
            responsibilities=responsibilities,
            required_skills=req_skills,
            preferred_skills=pref_skills,
            qualifications=qualifications,
            experience_requirements="0-1 years (Internship / Entry-level candidates welcome)",
            education_requirements="Bachelor's / Master's degree in Computer Science, Information Technology, or relevant STEM discipline",
            stipend=stipend,
            domain=domain,
            tags=tags,
            posted_at=posted_time.isoformat() + "Z"
        )
        postings.append(posting)
        job_idx += 1

    return postings

def save_datasets(postings: List[StandardJobPosting]):
    target_dirs = [Path("data/jobs"), Path("M2/data/jobs")]
    for d in target_dirs:
        d.mkdir(parents=True, exist_ok=True)

    json_data = [p.model_dump() for p in postings]

    csv_fieldnames = [
        "id", "job_title", "company", "location", "work_mode", "is_remote",
        "job_description", "responsibilities", "required_skills", "preferred_skills",
        "qualifications", "experience_requirements", "education_requirements",
        "stipend", "domain", "tags", "posted_at"
    ]

    for d in target_dirs:
        json_path = d / "internships_curated.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(json_data, f, indent=2, ensure_ascii=False)

        csv_path = d / "internships_curated.csv"
        with open(csv_path, "w", encoding="utf-8", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=csv_fieldnames)
            writer.writeheader()
            for p in postings:
                row = p.model_dump()
                row["responsibilities"] = " | ".join(row["responsibilities"])
                row["required_skills"] = ", ".join(row["required_skills"])
                row["preferred_skills"] = ", ".join(row["preferred_skills"])
                row["qualifications"] = " | ".join(row["qualifications"])
                row["tags"] = ", ".join(row["tags"])
                writer.writerow(row)

if __name__ == "__main__":
    postings = build_postings(175)
    save_datasets(postings)
    print(f"Generated, validated, and saved {len(postings)} curated internship postings.")
