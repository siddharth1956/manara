import logging
import os
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.retriever import retrieve
from app.services.generator import generate_answer, CONFIDENCE_LABEL
from app.services.comparison_engine import (
    extract_all_locations,
    extract_all_satellites,
    summarize_documents,
    build_comparison_table,
    comparison_intro,
    display_name,
)
from app.services.geo_bounds import filter_by_emirate, is_known_location

from app.services.nlu import IntentClassifier
from app.services.arabic.pipeline import ArabicPipeline
from app.services.language_detector import detect_language
from app.services.conversation_router import (
    classify_chitchat,
    chitchat_response,
    is_followup_query,
    resolve_followup,
    is_vegetation_query,
    vegetation_response,
    needs_clarification,
    clarification_response,
    resolve_comparison_subjects,
    detect_landmark,
    confidence_bucket,
    confidence_explanation,
)


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("manara")

app = FastAPI(
    title="MANARA API",
    description="Arabic Geospatial Intelligence Assistant",
    version="1.0.0"
)

# ---------------------------------------------------
# CORS
# ---------------------------------------------------
# Locally, Vite's dev proxy (see web/vite.config.ts) means the browser
# never makes a cross-origin request at all, so this has never been
# needed before now. In production the frontend and backend are on
# different domains (e.g. a Vercel URL calling a Render URL), which
# does need it. ALLOWED_ORIGINS lets the deployed frontend's real URL
# be configured without a code change; the dev server origins are
# always allowed so local development keeps working unchanged.

_default_origins = "http://localhost:5173,http://127.0.0.1:5173"
allowed_origins = [
    origin.strip()
    for origin in os.environ.get("ALLOWED_ORIGINS", _default_origins).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# ---------------------------------------------------
# Initialize NLU Models
# ---------------------------------------------------

english_classifier = IntentClassifier()

arabic_pipeline = ArabicPipeline()


# ---------------------------------------------------
# Request Model
# ---------------------------------------------------

class QueryContext(BaseModel):
    """Optional — the previous turn's intent/entities, supplied by the
    frontend so a follow-up like "What about Abu Dhabi?" can inherit
    the topic of the prior message. Absent for a conversation's first
    message, and safely ignored by any caller that doesn't send it.
    mentioned_locations accumulates distinct locations across the last
    few turns (not just the immediately-preceding one), so "Compare
    both" can resolve without re-asking which cities."""
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None
    mentioned_locations: Optional[List[str]] = None


class Query(BaseModel):
    question: str
    context: Optional[QueryContext] = None


# ---------------------------------------------------
# Home Endpoint
# ---------------------------------------------------

@app.get("/")
def home():

    return {

        "message": "Welcome to MANARA 🚀"

    }


@app.get("/health")
def health():
    """Used by the hosting platform's health check, not the frontend
    (which already uses `/` — see useConnectionStatus). Kept separate
    and minimal so it stays fast even if `/` ever grows heavier."""

    return {"status": "ok"}


# ---------------------------------------------------
# Main Query Endpoint
# ---------------------------------------------------

@app.post("/query")
def query(data: Query):

    if not data.question or not data.question.strip():

        raise HTTPException(
            status_code=400,
            detail="Question must not be empty."
        )

    try:

        # ==========================================
        # Step 1 : Detect Language
        # ==========================================

        language = detect_language(data.question)

        # ==========================================
        # Step 2 : NLP
        # ==========================================

        if language == "arabic":

            analysis = arabic_pipeline.analyze(
                data.question
            )

        else:

            analysis = english_classifier.analyze(
                data.question
            )

        intent = analysis["intent"]

        entities = analysis["entities"]

        # ==========================================
        # Step 2a : Follow-up inheritance
        # ==========================================
        # A query the real NLU couldn't place ("general") may still be
        # a continuation of the previous turn ("What about Abu Dhabi?")
        # rather than a genuinely new topic — only tried when the
        # frontend actually sent the prior turn's context.

        if intent == "general" and data.context and is_followup_query(data.question, entities):

            intent, entities = resolve_followup(
                intent,
                entities,
                data.context.model_dump(),
            )

        # ==========================================
        # Step 2b : Vegetation/NDVI short-circuit
        # ==========================================
        # Checked regardless of intent (analytics or comparison both
        # reach here) — the indexed corpus has zero vegetation/NDVI
        # documents, confirmed by direct inspection, so this is always
        # answered honestly rather than risking the LLM fabricating a
        # comparison from irrelevant retrieved context.

        if is_vegetation_query(entities):

            return {
                "question": data.question,
                "language": language,
                "intent": intent,
                "entities": entities,
                "answer": vegetation_response(language),
                "sources": [],
            }

        # ==========================================
        # Step 2c : Chit-chat short-circuit
        # ==========================================
        # Only reachable for queries the real NLU already scored as
        # "general" (no dataset keyword matched) — greetings, thanks,
        # capability questions, and genuine out-of-scope questions never
        # reach FAISS/BM25.

        if intent == "general":

            category = classify_chitchat(data.question, language)

            return {
                "question": data.question,
                "language": language,
                "intent": "general",
                "entities": entities,
                "answer": chitchat_response(category, language),
                "sources": [],
            }

        # ==========================================
        # Step 2d : Comparison routing
        # ==========================================
        # entities["location"]/["satellite"] can only ever hold one
        # value (see nlu.py) — extract_all_locations/satellites scans
        # the raw query independently to find both sides of an actual
        # comparison. Triggered on "2+ real subjects named", not on
        # intent == "comparison" specifically — nlu.py's weighted
        # scoring often classifies "Compare Sentinel-2A and Sentinel-2B"
        # as satellite_search (satellite keywords outweigh the single
        # "compare" word), so gating on the intent label alone would
        # miss it.
        #
        # For locations: retrieve() once against the query with a pool
        # large enough to cover the whole corpus (retriever.py scores
        # every document internally regardless of k — this is free, not
        # k extra work) then geographically filter by real bounding-box
        # overlap (geo_bounds.py), NOT by asking retriever.py's
        # text-based location boost to differentiate — confirmed by
        # direct inspection that only 18 of 1900 road documents
        # literally contain "Dubai" in their text and none contain
        # "Abu Dhabi", so that boost essentially never fires for roads.
        # For satellites, retriever.py's platform-field entity boost is
        # reliable (a structured field, not free text), so two separate
        # retrieve() calls work correctly there.
        #
        # The table itself is built entirely from these real, filtered
        # documents (comparison_engine.py) — never from the LLM
        # recalling/combining numbers itself. "Compare both cities" with
        # nothing nameable still falls through to asking, same as before.

        locations = extract_all_locations(data.question)
        satellites = extract_all_satellites(data.question)

        # "Compare both" names nothing itself — resolve against cities
        # mentioned across the last few turns (frontend-accumulated,
        # not just the immediately-preceding message) before falling
        # back to asking.
        if data.context and data.context.mentioned_locations:

            locations = resolve_comparison_subjects(
                data.question, locations, data.context.mentioned_locations,
            )

        subjects = locations if len(locations) >= 2 else (
            satellites if len(satellites) >= 2 else None
        )

        if subjects is locations:

            pool = retrieve(query=data.question, intent=intent, entities=entities, k=5000)
            docs_a = filter_by_emirate(pool, subjects[0])[:8]
            docs_b = filter_by_emirate(pool, subjects[1])[:8]

        elif subjects is satellites:

            docs_a = retrieve(query=data.question, intent=intent, entities={**entities, "satellite": subjects[0]})
            docs_b = retrieve(query=data.question, intent=intent, entities={**entities, "satellite": subjects[1]})

        else:

            docs_a = docs_b = None

        if subjects:

            label_a = display_name(subjects[0], language)
            label_b = display_name(subjects[1], language)

            table = build_comparison_table(
                label_a, summarize_documents(docs_a),
                label_b, summarize_documents(docs_b),
                language,
            )

            answer = f"{comparison_intro(label_a, label_b, language)}\n\n{table}"

            confidences = [d[0]["confidence"] for d in (docs_a, docs_b) if d]
            if confidences:
                bucket = confidence_bucket(min(confidences))
                label = CONFIDENCE_LABEL[language][bucket]
                explanation = confidence_explanation(bucket, language)
                answer = f"{answer}\n\n*{label} — {explanation}*"

            return {
                "question": data.question,
                "language": language,
                "intent": intent,
                "entities": entities,
                "answer": answer,
                "sources": docs_a + docs_b,
            }

        if intent == "comparison" and needs_clarification(intent, entities):

            return {
                "question": data.question,
                "language": language,
                "intent": intent,
                "entities": entities,
                "answer": clarification_response(language),
                "sources": [],
            }

        # ==========================================
        # Step 2e : Landmark detection
        # ==========================================
        # The indexed corpus has no landmark-level metadata — this only
        # fills in the containing city (for retrieval boosting) when the
        # NLU didn't already extract a location, and flags the landmark
        # name so the answer can be honest about city- vs landmark-level
        # precision instead of silently ignoring it.

        landmark = detect_landmark(data.question)

        if landmark and not entities.get("location"):
            entities["location"] = landmark[1]

        # ==========================================
        # Step 3 : Retrieve Documents
        # ==========================================

        documents = retrieve(

            query=data.question,

            intent=intent,

            entities=entities

        )

        top_confidence = documents[0]["confidence"] if documents else None

        # One geographic conclusion, computed once, not inferred by the
        # LLM mid-answer — this is what was producing self-contradicting
        # responses ("no Sentinel coverage" followed later by "Dubai is
        # covered"). Only meaningful for a known emirate; None otherwise,
        # which generator.py treats as "not applicable" rather than
        # "zero coverage".
        location_coverage = None

        if entities.get("location") and is_known_location(entities["location"]):

            overlapping = len(filter_by_emirate(documents, entities["location"]))

            location_coverage = (entities["location"], overlapping, len(documents))

        # ==========================================
        # Step 4 : Generate Answer
        # ==========================================

        answer = generate_answer(

            question=data.question,

            documents=documents,

            language=language,

            intent=intent,

            entities=entities,

            landmark=landmark[0] if landmark else None,

            confidence=confidence_bucket(top_confidence, len(documents), location_coverage),

            location_coverage=location_coverage,

        )

    except Exception as e:

        # HTTPException is handled by FastAPI's own exception middleware,
        # not the unhandled-exception path Starlette logs by default — so
        # without this, the traceback below would never reach the server
        # console and a failing query would be undebuggable in prod.
        logger.exception("Query failed: %r", data.question)

        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing the query."
        ) from e

    # ==========================================
    # Step 5 : Return Response
    # ==========================================

    return {

        "question": data.question,

        "language": language,

        "intent": intent,

        "entities": entities,

        "answer": answer,

        "sources": documents

    }