from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"

RAW_DATA_DIR = DATA_DIR / "raw"

PROCESSED_DATA_DIR = DATA_DIR / "processed"

EMBEDDING_DIR = DATA_DIR / "embeddings"

CACHE_DIR = DATA_DIR / "cache"