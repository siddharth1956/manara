"""
Static, hand-authored relevance ground truth for MANARA's retrieval
evaluation (Task F).

Every entry below was determined by directly inspecting the live
1,920-document corpus (data/processed/search_corpus.csv) — bbox
geometry checks against real Dubai/Abu Dhabi coordinates, text
content checks, and datetime comparisons — NOT by running queries
through the retriever and treating its output as ground truth. That
would be circular and would make the evaluation meaningless.

Each entry has two relevance tiers:
  - "relevant"   : the primary, best-answer document ID(s). Grade 2
                    for nDCG; counted in the binary relevant set for
                    Precision/Recall/MRR.
  - "acceptable" : secondary documents a reasonable system could
                    return without being "wrong". Grade 1 for nDCG;
                    also counted in the binary relevant set for
                    Precision/Recall/MRR (see metrics.py).

Where an entry's "relevant" list is empty, that is a deliberate,
documented finding (see rationale) — not a placeholder.
"""

# The 20 satellite documents in the corpus, verified directly against
# data/processed/search_corpus.csv. None of their bboxes geometrically
# contain Dubai's coordinates (55.2708, 25.2048) and none of their
# `text` fields mention "Dubai" at all — only ONE contains Abu Dhabi's
# coordinates. This is a genuine corpus gap (see report §Weaknesses),
# not an evaluation artifact.
ALL_SATELLITE_IDS = [
    "S2A_MSIL2A_20260705T064321_N0512_R120_T40QDM_20260705T115359",
    "S2A_MSIL2A_20260705T064321_N0512_R120_T40QDL_20260705T115359",
    "S2A_MSIL2A_20260705T064321_N0512_R120_T40QDK_20260705T115359",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39RXK_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39RXJ_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39RXH_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39RWK_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39RWJ_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39RWH_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39QXG_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39QWG_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39QWF_20260704T121414",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39QWF_20260704T104054",
    "S2A_MSIL2A_20260704T071321_N0512_R106_T39QWE_20260704T121414",
    "S2B_MSIL2A_20260704T065619_N0512_R063_T40RCQ_20260704T105318",
    "S2B_MSIL2A_20260704T065619_N0512_R063_T40RCP_20260704T105318",
    "S2B_MSIL2A_20260704T065619_N0512_R063_T40RBQ_20260704T105318",
    "S2B_MSIL2A_20260704T065619_N0512_R063_T40RBP_20260704T105318",
    "S2B_MSIL2A_20260704T065619_N0512_R063_T40RBN_20260704T105318",  # only tile covering Abu Dhabi
    "S2B_MSIL2A_20260704T065619_N0512_R063_T40QBM_20260704T105318",
]

LATEST_SATELLITE_IDS = [
    "S2A_MSIL2A_20260705T064321_N0512_R120_T40QDM_20260705T115359",
    "S2A_MSIL2A_20260705T064321_N0512_R120_T40QDK_20260705T115359",
    "S2A_MSIL2A_20260705T064321_N0512_R120_T40QDL_20260705T115359",
]  # verified: these 3 tie for the most recent datetime (2026-07-05T06:43:21.024000Z)

# The 13 (of 15) unnamed-road-by-type documents whose aggregate bbox
# was verified to contain Dubai's coordinates (busway and
# passing_place did not qualify).
DUBAI_ROAD_TYPE_IDS = [
    "road_type_motorway",
    "road_type_tertiary",
    "road_type_motorway_link",
    "road_type_residential",
    "road_type_secondary",
    "road_type_primary",
    "road_type_primary_link",
    "road_type_tertiary_link",
    "road_type_trunk",
    "road_type_secondary_link",
    "road_type_unclassified",
    "road_type_trunk_link",
    "road_type_living_street",
]

EVALUATION_QUERIES = [

    # ============================================================
    # Road queries
    # ============================================================
    {
        "query": "Show Dubai roads",
        "language": "english",
        "category": "road",
        "relevant": DUBAI_ROAD_TYPE_IDS,
        "acceptable": [],
        "rationale": (
            "Generic, non-specific road query — no single named road is "
            "more 'correct' than another. The 13 unnamed-road-by-type "
            "documents whose aggregate bbox was verified to contain "
            "Dubai's coordinates are the most directly representative "
            "answer. Named roads sharing these type tags (1000+ of them) "
            "are topically related but excluded from the relevant set "
            "for practicality — enumerating them would make Recall@5 "
            "trivially satisfiable by nearly any road document."
        ),
    },
    {
        "query": "Sheikh Zayed Road",
        "language": "english",
        "category": "road",
        "relevant": ["road_named_17"],
        "acceptable": ["road_named_1425"],
        "rationale": (
            "Verified by direct inspection: there are TWO documents in "
            "the corpus plausibly matching this name. road_named_17 "
            "('شارع الشيخ زايد', 172 segments, 119.08 km) is unambiguously "
            "the real E11 highway. road_named_1425 (literally named "
            "'Sheikh Zayed Road' in English) is a 0.1 km, 4-segment "
            "fragment — almost certainly a coincidentally/mis-named minor "
            "road in the source OSM data, not the highway. Marked as an "
            "acceptable alternative (it IS a lexically exact match) but "
            "not primary, since it is very unlikely to be what a user "
            "means. This dual-naming is a genuine corpus data-quality "
            "issue, not an evaluation artifact."
        ),
    },
    {
        "query": "شارع الشيخ زايد",
        "language": "arabic",
        "category": "road",
        "relevant": ["road_named_17"],
        "acceptable": ["road_named_0", "road_named_1570", "road_named_378"],
        "rationale": (
            "road_named_17 is the exact, unqualified name match. Verified "
            "(Task E analysis) that three other real Dubai roads share "
            "compound 'Sheikh ... Zayed' names — شارع الشيخ محمد بن زايد "
            "(road_named_0), شارع الشيخ خليفة بن زايد (road_named_1570), "
            "شارع الشيخ زايد بن حمدان آل نهيان (road_named_378) — these "
            "are legitimately different roads, marked acceptable since a "
            "reasonable lexical system could surface them, not because "
            "they're the intended answer."
        ),
    },
    {
        "query": "Motorway in Dubai",
        "language": "english",
        "category": "road",
        "relevant": ["road_type_motorway"],
        "acceptable": [],
        "rationale": (
            "road_type_motorway aggregates all 611 unnamed motorway "
            "segments — the direct, generic answer. Verified 23 named "
            "roads also carry a 'motorway' Road Type tag (e.g. "
            "road_named_17 itself); excluded from the relevant set for "
            "the same enumeration-practicality reason as the generic "
            "'Show Dubai roads' query above."
        ),
    },
    {
        "query": "Residential roads",
        "language": "english",
        "category": "road",
        "relevant": ["road_type_residential"],
        "acceptable": [],
        "rationale": (
            "road_type_residential aggregates 71,001 unnamed residential "
            "segments — by far the largest road category in the corpus "
            "and the direct generic answer. Verified 1,462 named roads "
            "also carry a 'residential' tag; deliberately excluded from "
            "the relevant set — at that scale, including them would make "
            "Recall@5 meaningless (satisfied by almost any road result)."
        ),
    },

    # ============================================================
    # Satellite queries
    # ============================================================
    {
        "query": "Show satellite images of Dubai",
        "language": "english",
        "category": "satellite",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": (
            "Verified directly: none of the 20 satellite tiles' bboxes "
            "geometrically contain Dubai's coordinates, and none of "
            "their `text` fields mention 'Dubai' anywhere. This is a "
            "real corpus gap (flagged in the Task F report), not "
            "something the ground truth should paper over — but since "
            "no better answer exists in the corpus, all 20 satellite "
            "documents are marked relevant as the intent-appropriate "
            "'best available' answer for a satellite-imagery request."
        ),
    },
    {
        "query": "اعرض صور الأقمار الصناعية لدبي",
        "language": "arabic",
        "category": "satellite",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": "Arabic equivalent of 'Show satellite images of Dubai' — same corpus gap and same reasoning applies.",
    },
    {
        "query": "Satellite imagery",
        "language": "english",
        "category": "satellite",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": "Fully generic, no location qualifier — all 20 satellite documents are equally valid answers.",
    },
    {
        "query": "Latest satellite data",
        "language": "english",
        "category": "satellite",
        "relevant": LATEST_SATELLITE_IDS,
        "acceptable": [
            sid for sid in ALL_SATELLITE_IDS if sid not in LATEST_SATELLITE_IDS
        ],
        "rationale": (
            "Unlike other satellite queries, 'latest' has an objectively "
            "correct answer given the explicit datetime field. Verified "
            "3 tiles tie for the most recent datetime "
            "(2026-07-05T06:43:21.024000Z) — these are primary; the "
            "remaining 17 satellite documents are marked acceptable "
            "(still topically satellite data, just not the latest)."
        ),
    },

    # ============================================================
    # Analytics queries
    # ============================================================
    {
        "query": "What is the cloud cover status in Dubai?",
        "language": "english",
        "category": "analytics",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": (
            "Same Dubai-coverage gap as the satellite queries above — no "
            "tile geometrically covers Dubai. All 20 satellite documents "
            "carry cloud_cover data and are the best available answer."
        ),
    },
    {
        "query": "Cloud cover",
        "language": "english",
        "category": "analytics",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": "Generic, no location qualifier — all 20 satellite documents (all carry cloud_cover data) are valid.",
    },
    {
        "query": "Vegetation index",
        "language": "english",
        "category": "analytics",
        "relevant": [],
        "acceptable": [],
        "rationale": (
            "Verified directly: no document anywhere in the 1,920-document "
            "corpus contains the word 'vegetation' or 'ndvi' in its text. "
            "The satellite document template (scripts/build_search_corpus.py) "
            "never includes vegetation content. This is a deliberate empty "
            "ground truth reflecting a real corpus gap, not a missing label — "
            "flagged already in the Task D design review and Task B.1 "
            "verification. A well-behaved system should return low-confidence "
            "or no results here; see metrics.py for how empty ground truth "
            "is handled."
        ),
    },
    {
        "query": "NDVI Dubai",
        "language": "english",
        "category": "analytics",
        "relevant": [],
        "acceptable": [],
        "rationale": "Same as 'Vegetation index' — no NDVI/vegetation content exists in the corpus, compounded by the Dubai-coverage gap.",
    },
    {
        "query": "الغطاء السحابي",
        "language": "arabic",
        "category": "analytics",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": "Arabic for 'the cloud cover' — generic, no location; same reasoning as the English 'Cloud cover' query.",
    },
    {
        "query": "مؤشر الغطاء النباتي",
        "language": "arabic",
        "category": "analytics",
        "relevant": [],
        "acceptable": [],
        "rationale": "Arabic for 'vegetation index' — same empty ground truth as 'Vegetation index', same underlying corpus gap.",
    },

    # ============================================================
    # Map queries
    # ============================================================
    {
        "query": "Show Dubai map",
        "language": "english",
        "category": "map",
        "relevant": DUBAI_ROAD_TYPE_IDS,
        "acceptable": [],
        "rationale": (
            "The corpus has no true map/gazetteer document type — this is "
            "a structural gap, flagged here rather than hidden. The "
            "closest defensible answer is the set of documents whose "
            "bbox actually covers Dubai, which (verified) is exclusively "
            "the road type-bucket documents; no satellite document "
            "qualifies (see satellite-query rationale above). Note "
            "'map' intent has no retriever.py filter branch by design, "
            "so this evaluates the raw ranking quality, not a filter."
        ),
    },
    {
        "query": "اعرض خريطة دبي",
        "language": "arabic",
        "category": "map",
        "relevant": DUBAI_ROAD_TYPE_IDS,
        "acceptable": [],
        "rationale": "Arabic equivalent of 'Show Dubai map' — same reasoning and same verified relevant set.",
    },

    # ============================================================
    # Comparison queries
    # ============================================================
    {
        "query": "Compare Dubai and Abu Dhabi cloud cover",
        "language": "english",
        "category": "comparison",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": (
            "Verified only ONE tile "
            "(S2B_MSIL2A_20260704T065619_N0512_R063_T40RBN_20260704T105318) "
            "geometrically covers Abu Dhabi, and none cover Dubai — a "
            "precise two-location comparison isn't actually answerable "
            "from this corpus. All 20 satellite documents are marked "
            "relevant as the intent-appropriate best-available answer; "
            "this gap is called out explicitly in the report rather than "
            "concealed by the ground truth."
        ),
    },
    {
        "query": "قارن الغطاء السحابي بين دبي وأبوظبي",
        "language": "arabic",
        "category": "comparison",
        "relevant": ALL_SATELLITE_IDS,
        "acceptable": [],
        "rationale": "Arabic equivalent of 'Compare Dubai and Abu Dhabi cloud cover' — same reasoning and same gap.",
    },
]
