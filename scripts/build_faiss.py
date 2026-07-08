import faiss
import numpy as np

from app.core.config import EMBEDDING_DIR

# Load embeddings
embeddings = np.load(
    EMBEDDING_DIR / "embeddings.npy"
)

print("Loaded embeddings:", embeddings.shape)

# FAISS requires float32
embeddings = embeddings.astype("float32")

# Dimension of vectors
dimension = embeddings.shape[1]

print("Embedding Dimension:", dimension)

# Create index
index = faiss.IndexFlatL2(dimension)

# Add vectors
index.add(embeddings)

print("Vectors in index:", index.ntotal)

# Save index
faiss.write_index(
    index,
    str(EMBEDDING_DIR / "faiss_index.bin")
)

print("\nFAISS index saved!")