"""
Read-only baseline retrieval wrappers for Task F evaluation.

These do NOT modify or reimplement retriever.py's production ranking
math. hybrid() calls the real, unmodified retrieve() directly — the
exact function production uses. faiss_only() and bm25_only() reuse
the same already-loaded model/index/bm25/df objects from
app.services.retriever (not fresh copies) and apply the identical
intent-filtering rule retrieve() uses, duplicated here only because
that filter isn't exposed as a standalone function — with NO entity
boosts, since isolating pure dense-only / sparse-only ranking quality
is the entire point of these two baselines. hybrid() genuinely
includes boosts, because that's what a real user actually receives.

All three functions return the FULL ranked document-ID list (not
sliced to a small k) so metrics.py's MRR can find a relevant document
wherever it actually lands, not just within an arbitrary top-K. This
is cheap: retrieve()'s underlying cost is dominated by the full-corpus
encode + dense + sparse search regardless of the `k` slice size (see
app/services/retriever.py — the boost loop runs over every document
unconditionally; only the final `results[:k]` slice depends on k), so
requesting the full ranking does not distort latency measurements.
"""

import time

from app.services.retriever import (
    model, index, bm25, df, tokenize, safe_value, retrieve,
)

TOTAL_DOCS = len(df)


def _passes_intent_filter(row_type, intent):
    """Mirrors retriever.py's intent-filtering rule exactly (read-only)."""

    if intent == "road_search":
        return row_type == "roads"

    if intent == "satellite_search":
        return row_type == "satellite"

    return True


def faiss_only(query, intent=None):
    """Pure dense ranking: FAISS distance order, intent-filtered, no boosts."""

    start = time.perf_counter()

    query_embedding = model.encode([query])
    distances, indices = index.search(query_embedding, TOTAL_DOCS)

    ranked_ids = []

    for idx in indices[0]:

        if idx == -1:
            continue

        row = df.iloc[idx]
        row_type = str(safe_value(row.get("type", ""))).lower()

        if not _passes_intent_filter(row_type, intent):
            continue

        ranked_ids.append(str(safe_value(row.get("id", ""))))

    latency_ms = (time.perf_counter() - start) * 1000

    return ranked_ids, latency_ms


def bm25_only(query, intent=None):
    """Pure sparse ranking: BM25 score order, intent-filtered, no boosts."""

    start = time.perf_counter()

    scores = bm25.get_scores(tokenize(query))
    order = sorted(range(TOTAL_DOCS), key=lambda i: scores[i], reverse=True)

    ranked_ids = []

    for idx in order:

        row = df.iloc[idx]
        row_type = str(safe_value(row.get("type", ""))).lower()

        if not _passes_intent_filter(row_type, intent):
            continue

        ranked_ids.append(str(safe_value(row.get("id", ""))))

    latency_ms = (time.perf_counter() - start) * 1000

    return ranked_ids, latency_ms


def hybrid(query, intent=None, entities=None):
    """Production hybrid retrieval — calls the real, unmodified retrieve()."""

    start = time.perf_counter()

    results = retrieve(
        query=query,
        intent=intent,
        entities=entities,
        k=TOTAL_DOCS,
    )

    latency_ms = (time.perf_counter() - start) * 1000

    ranked_ids = [r["id"] for r in results]

    return ranked_ids, latency_ms
