"""
IR metric implementations for Task F, written from the formulas
directly (no pytrec_eval / ranx / sklearn) so the math is auditable.

Two relevance views are used, both derived from ground_truth.py's
"relevant" (grade 2) and "acceptable" (grade 1) lists:

  - binary_relevant_set(entry): relevant | acceptable, used for
    Precision@K, Recall@K, and MRR — "was a genuinely useful
    document returned at all".
  - relevance_grades(entry): {doc_id: 2|1}, used for nDCG@K, which
    is graded by design — a primary match should score higher than
    an acceptable-but-not-ideal one, even at the same rank.

Every function returns None (not 0) when the metric is mathematically
undefined for that query (an empty ground-truth relevant set — see
the "Vegetation index" family of queries in ground_truth.py). Callers
must exclude None values from averages explicitly; silently coercing
to 0 would understate a system for correctly having nothing relevant
to find, which is a different failure mode than actually missing a
real answer.
"""

import math


def binary_relevant_set(entry):
    return set(entry["relevant"]) | set(entry["acceptable"])


def relevance_grades(entry):
    grades = {doc_id: 1 for doc_id in entry["acceptable"]}
    grades.update({doc_id: 2 for doc_id in entry["relevant"]})
    return grades


def precision_at_k(ranked_ids, relevant_set, k):
    """
    Precision@K = |{relevant docs in top K}| / K

    Undefined (None) only if k <= 0. An empty relevant_set is NOT
    undefined here — precision is well-defined (and will be 0 unless
    the top K is also empty) even with nothing relevant to find.
    """

    if k <= 0:
        return None

    top_k = ranked_ids[:k]

    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)

    return hits / k


def recall_at_k(ranked_ids, relevant_set, k):
    """
    Recall@K = |{relevant docs in top K}| / |relevant_set|

    Undefined (None) when relevant_set is empty — there is nothing
    to recall, so the ratio is 0/0, not 0.
    """

    if not relevant_set:
        return None

    top_k = ranked_ids[:k]

    hits = sum(1 for doc_id in top_k if doc_id in relevant_set)

    return hits / len(relevant_set)


def reciprocal_rank(ranked_ids, relevant_set):
    """
    Reciprocal Rank = 1 / (rank of the first relevant document),
    1-indexed. 0.0 if no relevant document appears anywhere in the
    ranked list. None if relevant_set is empty (nothing to rank for).

    Mean Reciprocal Rank (MRR) is the average of this value across
    all queries — computed by the caller, not here, since it's a
    corpus-level aggregate, not a per-query metric.
    """

    if not relevant_set:
        return None

    for rank, doc_id in enumerate(ranked_ids, start=1):

        if doc_id in relevant_set:
            return 1 / rank

    return 0.0


def _dcg_at_k(grades_in_rank_order, k):
    """
    DCG@K = sum_{i=1..K} (2^rel_i - 1) / log2(i + 1)

    Standard (exponential-gain) formulation, i=1-indexed rank.
    """

    dcg = 0.0

    for i, rel in enumerate(grades_in_rank_order[:k], start=1):

        gain = (2 ** rel) - 1
        discount = math.log2(i + 1)

        dcg += gain / discount

    return dcg


def ndcg_at_k(ranked_ids, grades, k):
    """
    nDCG@K = DCG@K / IDCG@K

    - DCG@K: computed over the actual ranked_ids, using each
      document's relevance grade (0 if not in `grades`).
    - IDCG@K: DCG@K of the ideal ranking — every known relevant
      document sorted by descending grade, placed at the top.

    None if IDCG@K is 0 (no relevant documents exist at all, i.e.
    an empty ground truth) — 0/0 is undefined, not 0.
    """

    actual_grades = [
        grades.get(doc_id, 0) for doc_id in ranked_ids
    ]

    dcg = _dcg_at_k(actual_grades, k)

    ideal_grades = sorted(grades.values(), reverse=True)
    idcg = _dcg_at_k(ideal_grades, k)

    if idcg == 0:
        return None

    return dcg / idcg


def summarize(values):
    """
    Mean of the non-None values in `values`, plus how many were
    excluded as undefined — so exclusions are visible, not silent.
    """

    defined = [v for v in values if v is not None]

    return {
        "mean": (sum(defined) / len(defined)) if defined else None,
        "n": len(defined),
        "excluded_undefined": len(values) - len(defined),
    }
