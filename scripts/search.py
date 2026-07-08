import faiss
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer

from app.core.config import (
    PROCESSED_DATA_DIR,
    EMBEDDING_DIR,
)

print("=" * 60)
print("MANARA SEMANTIC SEARCH")
print("=" * 60)

df = pd.read_csv(
    PROCESSED_DATA_DIR / "search_corpus.csv"
)

# Load embedding model
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

# Load FAISS index
index = faiss.read_index(
    str(EMBEDDING_DIR / "faiss_index.bin")
)

# Ask user for a query
query = input("\nEnter your question: ")

# Convert query to embedding
query_embedding = model.encode([query]).astype("float32")

# Search Top-3 matches
distances, indices = index.search(query_embedding, k=3)

print("\nTop Results\n")

for i, idx in enumerate(indices[0]):
    print(f"Result {i+1}")
    print(df.iloc[idx]["text"])
    print(f"Distance: {distances[0][i]:.4f}")
    print("-" * 50)