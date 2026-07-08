from fastapi import FastAPI
from pydantic import BaseModel

from app.services.retriever import retrieve
from app.services.generator import generate_answer

from app.services.nlu import IntentClassifier
from app.services.arabic_nlu import ArabicNLU
from app.services.language_detector import detect_language


app = FastAPI(
    title="MANARA API",
    description="Arabic Geospatial Intelligence Assistant",
    version="1.0.0"
)

# ---------------------------------------------------
# Initialize NLU Models
# ---------------------------------------------------

english_classifier = IntentClassifier()

arabic_classifier = ArabicNLU()


# ---------------------------------------------------
# Request Model
# ---------------------------------------------------

class Query(BaseModel):
    question: str


# ---------------------------------------------------
# Home Endpoint
# ---------------------------------------------------

@app.get("/")
def home():

    return {

        "message": "Welcome to MANARA 🚀"

    }


# ---------------------------------------------------
# Main Query Endpoint
# ---------------------------------------------------

@app.post("/query")
def query(data: Query):

    # ==========================================
    # Step 1 : Detect Language
    # ==========================================

    language = detect_language(data.question)

    # ==========================================
    # Step 2 : Select NLU
    # ==========================================

    if language == "arabic":

        intent = arabic_classifier.classify(
            data.question
        )

        # Arabic entity extraction will be added later
        entities = {}

    else:

        analysis = english_classifier.analyze(
            data.question
        )

        intent = analysis["intent"]

        entities = analysis["entities"]

    # ==========================================
    # Step 3 : Retrieve Documents
    # ==========================================

    documents = retrieve(

        query=data.question,

        intent=intent,

        entities=entities

    )

    # ==========================================
    # Step 4 : Generate Answer
    # ==========================================

    answer = generate_answer(

        data.question,

        documents

    )

    # ==========================================
    # Step 5 : Return Response
    # ==========================================

    return {

        "question": data.question,

        "language": language,

        "intent": intent,

        "answer": answer,

        "sources": documents

    }