"""
Approximate emirate bounding boxes and bbox-overlap geometry.

Exists because the indexed corpus identifies a document's location
purely by its numeric bounding box (`doc["bbox"]`) — confirmed by
direct inspection that only 18 of 1900 road documents literally
contain the word "Dubai" in their text, and zero contain "Abu Dhabi".
retriever.py's location boost, which does a text substring check,
essentially never fires for road data as a result — passing a
different `entities["location"]` to `retrieve()` for two different
cities was returning the same top-k pool both times.

This gives a real, defensible (if approximate) geographic filter
instead: does a document's bbox actually overlap the target emirate's
bounds. Used by comparison_engine.py (so two cities in a comparison
actually get different, geographically-real document sets) and by
main.py's single-location coverage check (Task 2 — one geographic
conclusion, not a contradiction between "no coverage" and "covered").
"""

import ast

# Approximate extents [min_lon, min_lat, max_lon, max_lat] — public
# geographic knowledge, not derived from or fitted to this corpus.
#
# Abu Dhabi is deliberately the CITY/metro extent, not the full
# emirate (which sprawls west to ~51.4°E and would overlap Dubai's
# border region so broadly it stops being a useful comparison filter —
# verified empirically: the full-emirate bound matched 16 of the same
# 30 documents Dubai's bound matched). A comparison query almost
# always means the two cities, not the administrative territory.
EMIRATE_BOUNDS = {
    "dubai": (54.85, 24.70, 55.65, 25.35),
    "abu dhabi": (54.25, 24.30, 54.70, 24.60),
    "sharjah": (55.35, 25.00, 56.35, 25.60),
    "ajman": (55.40, 25.35, 55.60, 25.50),
    "ras al khaimah": (55.70, 25.50, 56.20, 26.10),
    "fujairah": (56.10, 25.00, 56.50, 25.70),
    "umm al quwain": (55.50, 25.45, 55.75, 25.70),
}


def parse_bbox(bbox_value):
    """doc["bbox"] is a stringified list, e.g. "[54.9, 24.8, 55.5, 25.3]"
    (see web/src/utils/parse-bbox.ts for the frontend's equivalent).
    Returns None for anything that doesn't parse cleanly rather than
    raising — a malformed/missing bbox should degrade to "unknown
    location", never crash a comparison."""

    if not bbox_value:
        return None

    try:
        parsed = ast.literal_eval(bbox_value) if isinstance(bbox_value, str) else bbox_value

        if len(parsed) != 4:
            return None

        return tuple(float(v) for v in parsed)

    except (ValueError, SyntaxError, TypeError):
        return None


def bbox_overlaps(bbox_a, bbox_b):
    """Standard axis-aligned bounding box overlap test."""

    min_lon_a, min_lat_a, max_lon_a, max_lat_a = bbox_a
    min_lon_b, min_lat_b, max_lon_b, max_lat_b = bbox_b

    return (
        min_lon_a <= max_lon_b and max_lon_a >= min_lon_b and
        min_lat_a <= max_lat_b and max_lat_a >= min_lat_b
    )


def document_covers_emirate(document, emirate):
    """True if a retrieved document's bounding box genuinely overlaps
    the named emirate's extent. `emirate` must be a key in
    EMIRATE_BOUNDS (already-normalized, e.g. via location_mapper.py)."""

    target = EMIRATE_BOUNDS.get(emirate)

    if target is None:
        return False

    doc_bbox = parse_bbox(document.get("bbox"))

    if doc_bbox is None:
        return False

    return bbox_overlaps(doc_bbox, target)


def filter_by_emirate(documents, emirate):
    """Documents whose bbox actually overlaps the target emirate —
    preserves the original relevance ordering from retrieve()."""

    return [d for d in documents if document_covers_emirate(d, emirate)]


def is_known_location(name):
    return name in EMIRATE_BOUNDS
