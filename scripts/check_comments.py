from pathlib import Path

files = [
    Path("backend/app/schemas/matching.py"),
    Path("backend/app/services/matching_agent.py"),
    Path("backend/app/api/v1/endpoints/jobs.py"),
    Path("backend/app/services/pdf_service.py"),
    Path("M2/backend/app/schemas/matching.py"),
    Path("M2/backend/app/services/matching_agent.py"),
    Path("M2/backend/app/api/v1/endpoints/jobs.py"),
    Path("M2/backend/app/services/pdf_service.py"),
    Path("tests/test_m2_matching_agent.py"),
]

all_clean = True
for f in files:
    if not f.exists():
        continue
    with open(f, "r", encoding="utf-8") as fp:
        lines = fp.readlines()
    for idx, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("#"):
            print(f"COMMENT FOUND: {f}:{idx} -> {stripped}")
            all_clean = False

if all_clean:
    print("ALL M2.3 PYTHON FILES ARE 100% COMMENT-FREE!")
