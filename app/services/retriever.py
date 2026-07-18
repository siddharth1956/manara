import math
import re
import pickle
from app.services.location_mapper import normalize_location
import faiss
import pandas as pd
from sentence_transformers import SentenceTransformer

from app.core.config import (
    PROCESSED_DATA_DIR,
    EMBEDDING_DIR,
)

# ====================================
# Boost Weights
# ====================================
# Calibrated (Task B.1) so semantic similarity stays the dominant
# ranking signal — boosts are tie-breaking nudges, not overrides.

ROAD_INTENT_BOOST = 10        # doc type structurally matches a road_search intent
SATELLITE_INTENT_BOOST = 10   # doc type structurally matches a satellite_search intent
SATELLITE_ENTITY_BOOST = 8    # query names a specific satellite found in the doc's platform
PLATFORM_ENTITY_BOOST = 6     # query names a platform found in the doc's platform field
CLOUD_METRIC_BOOST = 8        # data-verified: doc actually has cloud_cover data
VEGETATION_METRIC_BOOST = 8   # data-verified: doc text mentions vegetation/ndvi
LOCATION_BOOST = 4            # weakest signal: place-name mention alone doesn't confirm relevance
DATE_ENTITY_BOOST = 2         # weakest signal: only confirms a date was extracted, not matched

# ====================================
# Hybrid Retrieval (RRF) Constants
# ====================================
# RRF_K is the standard reciprocal-rank-fusion damping constant from
# IR literature (the default used by Elasticsearch/OpenSearch hybrid
# search) — not corpus-tuned, robust across corpus size/changes, so
# it doesn't carry the re-tuning fragility a weighted-fusion alpha
# would (see Task D design review).
# RRF_SCALE maps RRF's small raw score range onto roughly the same
# 0-100 base-score range the old semantic_score used, so the boost
# weights above stay correctly calibrated without retuning them.

RRF_K = 60
RRF_SCALE = 2000

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

print("Loading BM25 index...")
with open(EMBEDDING_DIR / "bm25_index.pkl", "rb") as f:
    bm25 = pickle.load(f)


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


def tokenize(text):
    """
    Same tokenizer used to build bm25_index.pkl (scripts/build_bm25.py) —
    must stay identical or BM25 term matching silently degrades.
    """

    return re.findall(r"\w+", str(text).lower())


METRIC_CATEGORIES = {

    "cloud": [
        "cloud",
        "cloud cover",
        "الغطاء السحابي",
        "السحب",
        "غيوم"
    ],

    "vegetation": [
        "vegetation",
        "ndvi",
        "النباتات",
        "الغطاء النباتي"
    ]

}


def normalize_metric(value):
    """
    Maps English/Arabic metric phrases to a canonical category.
    """

    if not value:
        return None

    value = value.lower().strip()

    for category, synonyms in METRIC_CATEGORIES.items():

        if value in synonyms:
            return category

    return None


def retrieve(
    query,
    intent=None,
    entities=None,
    k=5
):
    """
    Hybrid Retrieval

    1. Dense (FAISS) + Sparse (BM25) Search, full corpus
    2. Reciprocal Rank Fusion
    3. Intent Filtering
    4. Entity Boosting
    5. Confidence Scoring
    6. Re-ranking
    """

    total_docs = len(df)

    # ====================================
    # Dense Search (FAISS, full corpus)
    # ====================================

    query_embedding = model.encode([query])

    distances, indices = index.search(
        query_embedding,
        total_docs
    )

    dense_distance = {}
    dense_rank = {}

    for rank, (idx, dist) in enumerate(
        zip(indices[0], distances[0]), start=1
    ):

        if idx == -1:
            continue

        dense_distance[idx] = safe_float(dist)
        dense_rank[idx] = rank

    # ====================================
    # Sparse Search (BM25, full corpus)
    # ====================================

    bm25_scores = bm25.get_scores(tokenize(query))

    bm25_order = sorted(
        range(total_docs),
        key=lambda i: bm25_scores[i],
        reverse=True
    )

    bm25_rank = {
        doc_idx: rank
        for rank, doc_idx in enumerate(bm25_order, start=1)
    }

    results = []

    for idx in range(total_docs):

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
        # Reciprocal Rank Fusion
        # ====================================

        distance = dense_distance.get(idx, 0.0)

        rrf_score = (
            1 / (RRF_K + dense_rank.get(idx, total_docs))
        ) + (
            1 / (RRF_K + bm25_rank.get(idx, total_docs))
        )

        base_score = rrf_score * RRF_SCALE

        boost = 0

        # ====================================
        # Intent Boost
        # ====================================

        if intent == "road_search" and row_type == "roads":
            boost += ROAD_INTENT_BOOST

        elif intent == "satellite_search" and row_type == "satellite":
            boost += SATELLITE_INTENT_BOOST

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
                    boost += SATELLITE_ENTITY_BOOST

            if "platform" in entities:

                platform = str(
                    safe_value(
                        row.get("platform", "")
                    )
                ).lower()

                if entities["platform"].lower() in platform:
                    boost += PLATFORM_ENTITY_BOOST

            if "location" in entities and entities["location"]:

                location = normalize_location(
                    entities["location"]
                )

                text_lower = str(
                    safe_value(row.get("text", ""))
                ).lower()

                if location and location in text_lower:
                    boost += LOCATION_BOOST

            if "metric" in entities and entities["metric"]:

                metric = normalize_metric(
                    entities["metric"]
                )

                if metric == "cloud":

                    cloud = safe_value(
                        row.get("cloud_cover")
                    )

                    if cloud is not None:
                        boost += CLOUD_METRIC_BOOST

                elif metric == "vegetation":

                    text_lower = str(
                        safe_value(row.get("text", ""))
                    ).lower()

                    if "vegetation" in text_lower or "ndvi" in text_lower:
                        boost += VEGETATION_METRIC_BOOST

            if "date" in entities:

                boost += DATE_ENTITY_BOOST

        # ====================================
        # Confidence
        # ====================================

        confidence = safe_float(

            round(

                min(
                    base_score + boost,
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