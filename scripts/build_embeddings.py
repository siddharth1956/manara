import pandas as pd
import numpy as np
from sentence_transformers import SentenceTransformer

from app.core.config import (
    PROCESSED_DATA_DIR,
    EMBEDDING_DIR,
)

# Load search corpus
df = pd.read_csv(
    PROCESSED_DATA_DIR / "search_corpus.csv"
)

# Load embedding model
print("Loading model...")

model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Generating embeddings...")

embeddings = model.encode(
    df["text"].tolist(),
    show_progress_bar=True
)

# Save embeddings
np.save(
    EMBEDDING_DIR / "embeddings.npy",
    embeddings
)

print("\nEmbeddings Shape:")
print(embeddings.shape)

print("\nSaved embeddings to:")
print(EMBEDDING_DIR / "embeddings.npy")