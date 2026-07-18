import re
import pickle
import pandas as pd
from rank_bm25 import BM25Okapi

from app.core.config import (
    PROCESSED_DATA_DIR,
    EMBEDDING_DIR,
)

# Load search corpus
df = pd.read_csv(
    PROCESSED_DATA_DIR / "search_corpus.csv"
)


def tokenize(text):
    return re.findall(r"\w+", str(text).lower())


print("Tokenizing corpus...")

tokenized_corpus = [
    tokenize(text) for text in df["text"].tolist()
]

print("Building BM25 index...")

bm25 = BM25Okapi(tokenized_corpus)

# Save index
with open(EMBEDDING_DIR / "bm25_index.pkl", "wb") as f:
    pickle.dump(bm25, f)

print("\nDocuments Indexed:", len(tokenized_corpus))

print("\nSaved BM25 index to:")
print(EMBEDDING_DIR / "bm25_index.pkl")
