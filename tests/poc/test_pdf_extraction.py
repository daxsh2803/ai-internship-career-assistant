
import os
import sys
import unicodedata
from typing import List, Tuple
import pymupdf

def create_sample_multicolumn_resume(pdf_path: str) -> None:
    doc = pymupdf.open()
    page = doc.new_page(width=612, height=792)

    page.insert_text(
        pymupdf.Point(50, 50),
        "DAKSH SHARMA — SOFTWARE ENGINEERING INTERN",
        fontsize=16,
        fontname="helv",
    )
    page.insert_text(
        pymupdf.Point(50, 70),
        "Email: daksh@example.com | GitHub: github.com/daksh | Location: Bengaluru, IN",
        fontsize=9,
        fontname="helv",
    )

    left_content = [
        (100, "EDUCATION"),
        (118, "B.Tech Computer Science"),
        (132, "ABC Institute of Technology"),
        (146, "Graduation: June 2026"),
        (160, "GPA: 3.82 / 4.00"),
        (190, "TECHNICAL SKILLS"),
        (208, "Languages: Python, Go, SQL"),
        (222, "Frameworks: FastAPI, React"),
        (236, "Databases: PostgreSQL, Redis"),
        (250, "Tools: Docker, Git, Linux"),
        (280, "COURSEWORK"),
        (298, "Data Structures & Algos"),
        (312, "Operating Systems"),
        (326, "Database Systems"),
        (340, "Distributed Systems"),
    ]
    for y_pos, text in left_content:
        font_size = 11 if text.isupper() else 9
        page.insert_text(pymupdf.Point(50, y_pos), text, fontsize=font_size, fontname="helv")

    right_content = [
        (100, "FEATURED TECHNICAL PROJECTS"),
        (120, "Distributed Asynchronous Task Queue (Python, Redis, Docker)"),
        (136, "• Engineered an asynchronous task queue handling 1,500 jobs/sec using Redis streams."),
        (152, "• Implemented consumer acknowledgments and dead-letter queues to prevent job loss."),
        (168, "• Containerized microservices using multi-stage Dockerfiles, reducing image size by 45%."),
        (200, "Cloud-Native File Storage Gateway (FastAPI, PostgreSQL, S3 API)"),
        (216, "• Built a high-throughput RESTful storage gateway supporting streaming file uploads."),
        (232, "• Designed schema with pgvector supporting semantic search over indexed documents."),
        (248, "• Implemented SHA-256 deduplication, saving 28% storage capacity on duplicate uploads."),
        (280, "WORK EXPERIENCE"),
        (300, "Backend Engineering Intern — CloudScale Systems (May 2025 – July 2025)"),
        (316, "• Optimized PostgreSQL database queries, reducing p95 query latency from 240ms to 45ms."),
        (332, "• Developed automated unit and integration tests using pytest, increasing coverage to 88%."),
    ]
    for y_pos, text in right_content:
        font_size = 11 if text.isupper() and not text.startswith("•") else 9
        page.insert_text(pymupdf.Point(240, y_pos), text, fontsize=font_size, fontname="helv")

    os.makedirs(os.path.dirname(pdf_path), exist_ok=True)
    doc.save(pdf_path)
    doc.close()

def naive_extract_text(pdf_path: str) -> str:
    doc = pymupdf.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text("text")
    doc.close()
    return text

def layout_aware_extract_text(pdf_path: str, column_split_x: float = 230.0) -> str:
    doc = pymupdf.open(pdf_path)
    full_text_parts = []

    for page_idx, page in enumerate(doc):
        blocks = page.get_text("blocks")
        
        text_blocks = [b for b in blocks if b[6] == 0]

        header_blocks = []
        left_blocks = []
        right_blocks = []

        for b in text_blocks:
            x0, y0, x1, y1, text, block_no, _ = b
            if y1 <= 85.0:
                header_blocks.append(b)
            elif x1 <= column_split_x:
                left_blocks.append(b)
            else:
                right_blocks.append(b)

        header_blocks.sort(key=lambda b: b[1])
        left_blocks.sort(key=lambda b: b[1])
        right_blocks.sort(key=lambda b: b[1])

        page_blocks = header_blocks + left_blocks + right_blocks
        page_text = "\n".join(b[4].strip() for b in page_blocks if b[4].strip())
        
        normalized_page_text = unicodedata.normalize("NFKD", page_text)
        full_text_parts.append(normalized_page_text)

    doc.close()
    return "\n\n".join(full_text_parts)

def run_pdf_extraction_validation() -> dict:
    sample_pdf = os.path.abspath("tests/poc/sample_multicolumn_resume.pdf")
    
    print("=" * 70)
    print("PoC 1: PyMuPDF Layout-Aware Multi-Column PDF Extraction Validation")
    print("=" * 70)

    create_sample_multicolumn_resume(sample_pdf)
    print(f"[*] Generated synthetic multi-column resume at: {sample_pdf}")
    assert os.path.exists(sample_pdf), "Failed to generate sample PDF"

    naive_text = naive_extract_text(sample_pdf)
    print(f"[*] Naive text extraction length: {len(naive_text)} chars")

    layout_text = layout_aware_extract_text(sample_pdf)
    print(f"[*] Layout-aware extraction length: {len(layout_text)} chars")

    print("\n[*] Validating Reading Order & Section Integrity:")

    pos_education = layout_text.find("EDUCATION")
    pos_skills = layout_text.find("TECHNICAL SKILLS")
    pos_coursework = layout_text.find("COURSEWORK")
    pos_projects = layout_text.find("FEATURED TECHNICAL PROJECTS")
    pos_experience = layout_text.find("WORK EXPERIENCE")

    print(f"  - Position of 'EDUCATION': {pos_education}")
    print(f"  - Position of 'TECHNICAL SKILLS': {pos_skills}")
    print(f"  - Position of 'COURSEWORK': {pos_coursework}")
    print(f"  - Position of 'FEATURED TECHNICAL PROJECTS': {pos_projects}")
    print(f"  - Position of 'WORK EXPERIENCE': {pos_experience}")

    assert pos_education != -1, "EDUCATION section missing"
    assert pos_skills != -1, "TECHNICAL SKILLS section missing"
    assert pos_coursework != -1, "COURSEWORK section missing"
    assert pos_projects != -1, "PROJECTS section missing"
    assert pos_experience != -1, "WORK EXPERIENCE section missing"

    assert pos_education < pos_projects, "Layout error: Projects preceded Education"
    assert pos_skills < pos_projects, "Layout error: Projects preceded Technical Skills"
    assert pos_coursework < pos_projects, "Layout error: Projects preceded Coursework"
    assert pos_projects < pos_experience, "Reading order error: Experience preceded Projects"

    assert "Engineered an asynchronous task queue handling 1,500 jobs/sec" in layout_text
    assert "Optimized PostgreSQL database queries" in layout_text

    print("\n[+] SUCCESS: All layout-aware extraction assertions passed!")
    print(f"[+] Output preview (first 300 chars):\n---\n{layout_text[:300]}...\n---")

    return {
        "status": "PASSED",
        "pdf_path": sample_pdf,
        "naive_length": len(naive_text),
        "layout_aware_length": len(layout_text),
        "reading_order_verified": True,
    }

if __name__ == "__main__":
    results = run_pdf_extraction_validation()
    print("\nTest Result Summary:", results)
