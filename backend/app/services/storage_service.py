
import hashlib
from pathlib import Path
from typing import Tuple
import uuid
from fastapi import HTTPException, UploadFile, status

from app.core.config import settings

class LocalStorageService:
    def __init__(self, base_dir: Path = settings.UPLOAD_DIR):
        self.base_dir = base_dir.resolve()
        self.base_dir.mkdir(parents=True, exist_ok=True)

    async def save_resume_file(
        self, candidate_id: uuid.UUID, file: UploadFile
    ) -> Tuple[str, str, int]:
        if file.content_type not in ("application/pdf", "application/octet-stream"):
            if not file.filename.lower().endswith(".pdf"):
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid file format. Only PDF files are supported.",
                )

        content = await file.read()
        file_size = len(content)

        if file_size > settings.MAX_UPLOAD_SIZE_BYTES:
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail=f"File exceeds maximum permitted size of {settings.MAX_UPLOAD_SIZE_BYTES / (1024 * 1024)}MB",
            )

        if file_size == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Uploaded file is empty (0 bytes).",
            )

        sha256_hash = hashlib.sha256(content).hexdigest()

        candidate_dir = (self.base_dir / str(candidate_id)).resolve()
        if not str(candidate_dir).startswith(str(self.base_dir)):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Security violation: Path traversal detected.",
            )

        candidate_dir.mkdir(parents=True, exist_ok=True)

        target_file_id = uuid.uuid4()
        target_path = candidate_dir / f"{target_file_id}.pdf"

        target_path.write_bytes(content)

        relative_storage_path = str(target_path.relative_to(Path.cwd())).replace("\\", "/")

        return relative_storage_path, sha256_hash, file_size
