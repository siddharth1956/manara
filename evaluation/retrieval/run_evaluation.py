"""
Task F evaluation orchestrator.

Runs FAISS-only, BM25-only, and Hybrid (production retrieve()) against
every query in ground_truth.py, computes Precision@1/3/5, Recall@5,
MRR, and nDCG@5 for each system, benchmarks latency, and writes a
markdown report.

Read-only with respect to production code: imports app.services.nlu /
app.services.arabic.pipeline / app.services.language_detector exactly
as app/main.py does, to get the same intent/entities a real request
would use — this is "use the real system's own classification", not
"guess relevance"; ground truth (which documents are relevant) is
entirely static and defined in ground_truth.py, independent of this.

Run with:
    python -m evaluation.retrieval.run_evaluation
"""

import math

from app.services.nlu import IntentClassifier
from app.services.arabic.pipeline import ArabicPipeline
from app.services.language_detector import detect_language

from evaluation.retrieval.ground_truth import EVALUATION_QUERIES
from evaluation.retrieval.baselines import faiss_only, bm25_only, hybrid
from app.services.retriever import model as _model, index as _index
from evaluation.retrieval.metrics import (
    binary_relevant_set,
    relevance_grades,
    precision_at_k,
    recall_at_k,
    reciprocal_rank,
    ndcg_at_k,
    summarize,
)

SYSTEMS = ["faiss", "bm25", "hybrid"]

english_classifier = IntentClassifier()
arabic_pipeline = ArabicPipeline()


def classify(query):
    """Same NLU routing app/main.py uses — read-only reuse, not a copy."""

    language = detect_language(query)

    if language == "arabic":
        analysis = arabic_pipeline.analyze(query)
    else:
        analysis = english_classifier.analyze(query)

    return analysis["intent"], analysis["entities"]


def run_system(system, query, intent, entities):

    if system == "faiss":
        return faiss_only(query, intent=intent)

    if system == "bm25":
        return bm25_only(query, intent=intent)

    if system == "hybrid":
        return hybrid(query, intent=intent, entities=entities)

    raise ValueError(system)


def evaluate_all():
    """
    Returns per_query: list of dicts, one per (query, system) pair,
    with ranked_ids, latency, and every metric already computed.
    """

    # Warm up the encoder/index once before timing anything — the first
    # SentenceTransformer.encode() call in a process pays a one-time
    # torch/thread-pool init cost (~2-3s) that would otherwise
    # contaminate the very first latency sample and skew P95.
    _warmup_embedding = _model.encode(["warmup"])
    _index.search(_warmup_embedding, 1)

    per_query = []

    for entry in EVALUATION_QUERIES:

        query = entry["query"]
        intent, entities = classify(query)

        relevant_set = binary_relevant_set(entry)
        grades = relevance_grades(entry)

        for system in SYSTEMS:

            ranked_ids, latency_ms = run_system(system, query, intent, entities)

            record = {
                "query": query,
                "category": entry["category"],
                "language": entry["language"],
                "system": system,
                "intent": intent,
                "ranked_ids": ranked_ids,
                "top5": ranked_ids[:5],
                "latency_ms": latency_ms,
                "ground_truth_empty": len(relevant_set) == 0,
                "p_at_1": precision_at_k(ranked_ids, relevant_set, 1),
                "p_at_3": precision_at_k(ranked_ids, relevant_set, 3),
                "p_at_5": precision_at_k(ranked_ids, relevant_set, 5),
                "recall_at_5": recall_at_k(ranked_ids, relevant_set, 5),
                "rr": reciprocal_rank(ranked_ids, relevant_set),
                "ndcg_at_5": ndcg_at_k(ranked_ids, grades, 5),
            }

            per_query.append(record)

    return per_query


def aggregate_by_system(per_query):

    aggregates = {}

    for system in SYSTEMS:

        rows = [r for r in per_query if r["system"] == system]

        aggregates[system] = {
            "precision_at_1": summarize([r["p_at_1"] for r in rows]),
            "precision_at_3": summarize([r["p_at_3"] for r in rows]),
            "precision_at_5": summarize([r["p_at_5"] for r in rows]),
            "recall_at_5": summarize([r["recall_at_5"] for r in rows]),
            "mrr": summarize([r["rr"] for r in rows]),
            "ndcg_at_5": summarize([r["ndcg_at_5"] for r in rows]),
            "latency": latency_stats([r["latency_ms"] for r in rows]),
        }

    return aggregates


def latency_stats(values):

    ordered = sorted(values)
    n = len(ordered)

    def percentile(p):
        if n == 1:
            return ordered[0]
        idx = min(n - 1, max(0, math.ceil(p / 100 * n) - 1))
        return ordered[idx]

    return {
        "avg_ms": sum(ordered) / n,
        "median_ms": percentile(50),
        "p95_ms": percentile(95),
    }


def sign_test_p_value(wins, losses):
    """
    Two-tailed exact sign test, implemented from the binomial formula
    directly (no scipy). Ties are excluded before calling this, per
    standard sign-test practice. Appropriate here (vs. a paired t-test)
    because per-query metric differences are not assumed normal and
    the sample size is small.
    """

    n = wins + losses

    if n == 0:
        return None

    k = min(wins, losses)

    cumulative = sum(math.comb(n, i) for i in range(0, k + 1))

    p_one_tail = cumulative / (2 ** n)

    return min(1.0, 2 * p_one_tail)


def compare_systems(per_query, metric_key, sys_a, sys_b):
    """Paired per-query comparison of two systems on one metric."""

    by_query_a = {r["query"]: r[metric_key] for r in per_query if r["system"] == sys_a}
    by_query_b = {r["query"]: r[metric_key] for r in per_query if r["system"] == sys_b}

    wins = losses = ties = 0

    for query in by_query_a:

        a = by_query_a[query]
        b = by_query_b[query]

        if a is None or b is None:
            continue

        if a > b:
            wins += 1
        elif a < b:
            losses += 1
        else:
            ties += 1

    p_value = sign_test_p_value(wins, losses)

    return {
        "wins_a": wins,
        "wins_b": losses,
        "ties": ties,
        "p_value": p_value,
    }


if __name__ == "__main__":

    from evaluation.retrieval.report import generate_report

    per_query = evaluate_all()
    aggregates = aggregate_by_system(per_query)

    hybrid_vs_faiss = compare_systems(per_query, "ndcg_at_5", "hybrid", "faiss")
    hybrid_vs_bm25 = compare_systems(per_query, "ndcg_at_5", "hybrid", "bm25")

    generate_report(
        per_query=per_query,
        aggregates=aggregates,
        hybrid_vs_faiss=hybrid_vs_faiss,
        hybrid_vs_bm25=hybrid_vs_bm25,
    )
