import logging
import os
from typing import Any, Dict, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from app.services.retriever import retrieve
from app.services.generator import generate_answer

from app.services.nlu import IntentClassifier
from app.services.arabic.pipeline import ArabicPipeline
from app.services.language_detector import detect_language
from app.services.conversation_router import (
    classify_chitchat,
    chitchat_response,
    is_followup_query,
    resolve_followup,
    needs_clarification,
    clarification_response,
    detect_landmark,
    confidence_bucket,
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
    message, and safely ignored by any caller that doesn't send it."""
    intent: Optional[str] = None
    entities: Optional[Dict[str, Any]] = None


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
        # Step 2b : Chit-chat short-circuit
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
        # Step 2c : Comparison clarification
        # ==========================================
        # "Compare both cities" names nothing to compare — ask rather
        # than guess.

        if needs_clarification(intent, entities):

            return {
                "question": data.question,
                "language": language,
                "intent": intent,
                "entities": entities,
                "answer": clarification_response(language),
                "sources": [],
            }

        # ==========================================
        # Step 2d : Landmark detection
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

            confidence=confidence_bucket(top_confidence),

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