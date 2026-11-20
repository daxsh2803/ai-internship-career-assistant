import os
import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT_DIR / "backend"))

from app.services.chunking_service import ChunkingService
from app.services.dataset_loader import DatasetLoaderService
from app.services.embedding_service import LocalEmbeddingService

def run_indexing(data_file: str = "data/jobs/internships_curated.json", vectorstore_dir: str = "data/vectorstore") -> int:
    loader = DatasetLoaderService.get_instance(data_file)
    jobs = loader.get_all_jobs()
    print(f"Loaded {len(jobs)} jobs from {data_file}")

    chunks = ChunkingService.chunk_all_jobs(jobs)
    print(f"Generated {len(chunks)} section-aware chunks across 4 facets (Overview, Responsibilities, Required Skills, Preferred Skills)")

    embedding_service = LocalEmbeddingService.get_instance()
    indexed_count = embedding_service.index_chunks(
        chunks=chunks,
        collection_name="internship_chunks",
        persist_dir=vectorstore_dir,
        batch_size=64,
    )

    collection = embedding_service.get_collection("internship_chunks", persist_dir=vectorstore_dir)
    actual_count = collection.count()
    print(f"ChromaDB persistent collection 'internship_chunks' populated at {vectorstore_dir}")
    print(f"Total indexed chunks verified: {actual_count} / {len(chunks)}")
    return actual_count

if __name__ == "__main__":
    count = run_indexing()
    m2_vectorstore = Path("M2/data/vectorstore")
    if Path("M2").exists():
        run_indexing("M2/data/jobs/internships_curated.json", str(m2_vectorstore))
    print(f"Indexing completed successfully! Total indexed: {count}")

