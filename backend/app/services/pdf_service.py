from pathlib import Path
import re
from typing import Dict, List, Optional
import pymupdf as fitz

class PDFExtractionService:
    @staticmethod
    def extract_text_from_pdf(file_path: Path) -> str:
        path = Path(file_path)
        if not path.exists():
            raise FileNotFoundError(f"PDF file does not exist at {path}")

        doc = fitz.open(path)
        extracted_text_blocks: List[str] = []

        try:
            for page in doc:
                page_width = page.rect.width
                blocks = page.get_text("blocks")
                text_blocks = [b for b in blocks if b[6] == 0 and b[4].strip()]

                has_two_columns = False
                left_col_blocks = []
                right_col_blocks = []

                column_split_x = page_width * 0.45

                for b in text_blocks:
                    x0, y0, x1, y1, text, *_ = b
                    if x1 <= column_split_x + 20:
                        left_col_blocks.append(b)
                    elif x0 >= column_split_x - 20:
                        right_col_blocks.append(b)
                    else:
                        pass

                if len(left_col_blocks) >= 2 and len(right_col_blocks) >= 2:
                    has_two_columns = True

                if has_two_columns:
                    left_sorted = sorted(left_col_blocks, key=lambda b: (round(b[1] / 10), b[0]))
                    right_sorted = sorted(right_col_blocks, key=lambda b: (round(b[1] / 10), b[0]))

                    spanning_top = [
                        b for b in text_blocks
                        if b not in left_col_blocks and b not in right_col_blocks and b[1] < page.rect.height * 0.25
                    ]
                    spanning_bottom = [
                        b for b in text_blocks
                        if b not in left_col_blocks and b not in right_col_blocks and b[1] >= page.rect.height * 0.25
                    ]

                    for b in spanning_top:
                        extracted_text_blocks.append(b[4].strip())
                    for b in left_sorted:
                        extracted_text_blocks.append(b[4].strip())
                    for b in right_sorted:
                        extracted_text_blocks.append(b[4].strip())
                    for b in spanning_bottom:
                        extracted_text_blocks.append(b[4].strip())
                else:
                    sorted_blocks = sorted(text_blocks, key=lambda b: (round(b[1] / 10), b[0]))
                    for b in sorted_blocks:
                        extracted_text_blocks.append(b[4].strip())

        finally:
            doc.close()

        return "\n\n".join(extracted_text_blocks)

    @staticmethod
    def identify_sections(full_text: str) -> List[Dict[str, str]]:
        lines = full_text.splitlines()
        sections: List[Dict[str, str]] = []

        section_headers = {
            "SUMMARY": [
                "SUMMARY", "PROFESSIONAL SUMMARY", "PROFILE", "CAREER OBJECTIVE",
                "OBJECTIVE", "ABOUT ME", "CANDIDATE SUMMARY"
            ],
            "EDUCATION": [
                "EDUCATION", "ACADEMIC BACKGROUND", "ACADEMICS", "EDUCATIONAL QUALIFICATIONS",
                "STUDIES", "ACADEMIC DETAILS"
            ],
            "EXPERIENCE": [
                "EXPERIENCE", "WORK EXPERIENCE", "EMPLOYMENT HISTORY", "PROFESSIONAL EXPERIENCE",
                "INTERNSHIPS", "WORK HISTORY", "EMPLOYMENT"
            ],
            "PROJECTS": [
                "PROJECTS", "ACADEMIC PROJECTS", "KEY PROJECTS", "PERSONAL PROJECTS",
                "FEATURED PROJECTS", "TECHNICAL PROJECTS", "FEATURED TECHNICAL PROJECTS"
            ],
            "SKILLS": [
                "SKILLS", "TECHNICAL SKILLS", "COMPETENCIES", "CORE COMPETENCIES",
                "SKILLS & COMPETENCIES", "AREAS OF EXPERTISE", "TECHNOLOGIES", "TECH STACK"
            ],
            "CERTIFICATIONS": [
                "CERTIFICATIONS", "CERTIFICATES", "LICENSES", "COURSES",
                "TRAININGS", "ACCREDITATIONS", "CERTIFICATIONS & AWARDS", "CERTIFICATIONS & ACHIEVEMENTS"
            ],
            "AWARDS": [
                "AWARDS", "HONORS", "ACHIEVEMENTS", "PUBLICATIONS", "HONORS & AWARDS"
            ],
            "LANGUAGES": [
                "LANGUAGES", "SPOKEN LANGUAGES", "LANGUAGE PROFICIENCY"
            ],
        }

        current_type = "SUMMARY"
        current_title = "Candidate Summary"
        current_lines: List[str] = []

        for line in lines:
            trimmed = line.strip()
            if not trimmed:
                continue

            matched_type = None
            clean_line = trimmed.strip("#*-_: ")
            upper = clean_line.upper()

            if len(clean_line.split()) <= 4 and not any(ch in clean_line for ch in ["|", ",", "(", ")", "/", "\\"]) and not any(w in clean_line.lower().split() for w in ["with", "in", "and", "for", "at", "by", "on", "using", "to", "over", "across", "under"]):
                cleaned_upper = re.sub(r"[:\-—]+$", "", upper).strip()
                for stype, keywords in section_headers.items():
                    if any(cleaned_upper == kw for kw in keywords):
                        matched_type = stype
                        break

            if matched_type:
                if current_lines:
                    sections.append({
                        "section_type": current_type,
                        "section_title": current_title,
                        "raw_text": "\n".join(current_lines).strip(),
                    })
                    current_lines = []
                current_type = matched_type
                current_title = trimmed
            else:
                current_lines.append(trimmed)

        if current_lines:
            sections.append({
                "section_type": current_type,
                "section_title": current_title,
                "raw_text": "\n".join(current_lines).strip(),
            })

        return sections
