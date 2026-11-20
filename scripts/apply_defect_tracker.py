import shutil
from pathlib import Path

src = Path("Internship_artifacts/Defect_Tracker_v0.1_M2_Logged.xlsx")
dst = Path("Internship_artifacts/Defect_Tracker Template_v0.1.xlsx")

if src.exists():
    shutil.copyfile(src, dst)
    print("Successfully updated Defect_Tracker Template_v0.1.xlsx")
