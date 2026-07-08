import math

import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

from app.core.config import (
    PROCESSED_DATA_DIR,
    EMBEDDING_DIR,
)

print("Loading embedding model...")
model = SentenceTransformer(
    "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
)

print("Loading FAISS index...")
index = faiss.read_index(
    str(EMBEDDING_DIR / "faiss_index.bin")
)

print("Loading search corpus...")
df = pd.read_csv(
    PROCESSED_DATA_DIR / "search_corpus.csv"
)


def safe_float(value, default=0.0):
    """
    Converts values safely for JSON serialization.
    """

    try:
        value = float(value)

        if math.isnan(value):
            return default

        if math.isinf(value):
            return default

        return value

    except Exception:
        return default


def safe_value(value):
    """
    Converts Pandas NaN into JSON-safe values.
    """

    if pd.isna(value):
        return None

    return value


def retrieve(
    query,
    intent=None,
    entities=None,
    k=5
):
    """
    Hybrid Retrieval

    1. Semantic Search
    2. Intent Filtering
    3. Entity Boosting
    4. Confidence Scoring
    5. Re-ranking
    """

    query_embedding = model.encode([query])

    distances, indices = index.search(
        query_embedding,
        k * 3
    )

    results = []

    for idx, dist in zip(indices[0], distances[0]):

        if idx == -1:
            continue

        row = df.iloc[idx]

        # ====================================
        # Intent Filtering
        # ====================================

        row_type = str(
            safe_value(row.get("type", ""))
        ).lower()

        if intent == "road_search":

            if row_type != "roads":
                continue

        elif intent == "satellite_search":

            if row_type != "satellite":
                continue

        # ====================================
        # Semantic Score
        # ====================================

        distance = safe_float(dist)

        semantic_score = (
            1 / (1 + distance)
        ) * 100

        boost = 0

        # ====================================
        # Intent Boost
        # ====================================

        if intent == "road_search" and row_type == "roads":
            boost += 20

        elif intent == "satellite_search" and row_type == "satellite":
            boost += 20

        # ====================================
        # Entity Boost
        # ====================================

        if entities:

            if "satellite" in entities:

                platform = str(
                    safe_value(
                        row.get("platform", "")
                    )
                ).lower()

                if entities["satellite"].lower() in platform:
                    boost += 15

            if "platform" in entities:

                platform = str(
                    safe_value(
                        row.get("platform", "")
                    )
                ).lower()

                if entities["platform"].lower() in platform:
                    boost += 10

            if "metric" in entities:

                if entities["metric"] == "cloud":

                    cloud = safe_value(
                        row.get("cloud_cover")
                    )

                    if cloud is not None:
                        boost += 10

            if "date" in entities:

                boost += 5

        # ====================================
        # Confidence
        # ====================================

        confidence = safe_float(

            round(

                min(
                    semantic_score + boost,
                    100
                ),

                2

            )

        )

        # ====================================
        # Build Result
        # ====================================

        result = {

            "id": str(
                safe_value(
                    row.get("id", "")
                )
            ),

            "type": row_type,

            "platform": str(
                safe_value(
                    row.get("platform", "")
                )
            ),

            "constellation": str(
                safe_value(
                    row.get("constellation", "")
                )
            ),

            "datetime": str(
                safe_value(
                    row.get("datetime", "")
                )
            ),

            "cloud_cover": safe_value(
                row.get("cloud_cover")
            ),

            "bbox": str(
                safe_value(
                    row.get("bbox", "")
                )
            ),

            "confidence": confidence,

            "distance": distance,

            "text": str(
                safe_value(
                    row.get("text", "")
                )
            )

        }

        results.append(result)

    # ====================================
    # Re-ranking
    # ====================================

    results = sorted(

        results,

        key=lambda x: x["confidence"],

        reverse=True

    )

    return results[:k]