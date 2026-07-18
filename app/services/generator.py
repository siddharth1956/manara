from app.llm.router import LLMRouter

# ----------------------------------------
# Initialize Router
# ----------------------------------------

router = LLMRouter()

# ----------------------------------------
# Language Instruction
# ----------------------------------------
# Written IN Arabic, not just about Arabic — the tokens immediately
# preceding generation are themselves Arabic, which primes the model
# toward Arabic continuations far more reliably than an English
# instruction asking for Arabic output. Small instruction-tuned models
# (this deployment runs llama3.2:3b) drift into other languages
# without an explicit, emphatic constraint like this — see the
# accompanying test notes for reproduced examples of the failure mode
# this addresses (fragments of French/Spanish/Vietnamese/Italian
# appearing mid-sentence in Arabic answers).
#
# The exception clause is deliberately general rather than a fixed
# list of two names: the retrieved context is largely English field
# labels and OSM highway-taxonomy values (motorway, trunk, secondary,
# tertiary...). Naming only "Sentinel-2"/"OpenStreetMap" left the model
# to improvise Arabic transliterations for everything else it
# encountered, producing corrupted hybrid words (observed: "مotosway",
# "سegmentًا") — the model has no reliable Arabic vocabulary for these
# terms, so telling it to keep ALL such English technical terms as-is
# removes the need to improvise at all.

ARABIC_LANGUAGE_INSTRUCTION = (
    "يجب أن تكون إجابتك بالكامل باللغة العربية الفصحى فقط. "
    "لا تستخدم أي كلمات أو عبارات من الإنجليزية أو الفرنسية أو الإسبانية "
    "أو الإيطالية أو أي لغة أخرى، باستثناء المصطلحات والأسماء التقنية "
    "الظاهرة بالإنجليزية في السياق المسترجع أدناه (مثل Sentinel-2 أو "
    "OpenStreetMap أو أنواع الطرق مثل motorway أو trunk أو secondary أو "
    "tertiary أو residential، أو مصطلحات مثل segment أو segments) — "
    "يجب كتابة هذه المصطلحات كما وردت بالضبط "
    "بالإنجليزية، ولا تحاول أبداً ترجمتها أو تحويل حروفها إلى العربية، "
    "لأن ذلك ينتج كلمات مشوهة. افصل دائماً بين الكلمة الإنجليزية وأي "
    "بادئة أو كلمة عربية بمسافة — لا تدمجهما أبداً في كلمة واحدة "
    "(مثال خاطئ: مotorway، البounding box | مثال صحيح: motorway، "
    "bounding box)."
)

ENGLISH_LANGUAGE_INSTRUCTION = "Respond entirely in English."

CONFIDENCE_LABEL = {
    "english": {"high": "High confidence", "medium": "Medium confidence", "low": "Low confidence"},
    "arabic": {"high": "ثقة عالية", "medium": "ثقة متوسطة", "low": "ثقة منخفضة"},
}


def generate_answer(
    question,
    documents,
    language,
    intent,
    entities,
    landmark=None,
    confidence=None,
):
    """
    Generate answer using the selected LLM.
    """

    # ----------------------------------------
    # Build Context
    # ----------------------------------------

    context = ""

    for doc in documents:

        context += doc["text"] + "\n\n"

    entity_summary = ", ".join(
        f"{key}={value}" for key, value in entities.items() if value
    ) or "none"

    language_instruction = (
        ARABIC_LANGUAGE_INSTRUCTION
        if language == "arabic"
        else ENGLISH_LANGUAGE_INSTRUCTION
    )

    # Landmark grounding is checked here, not asked of the model — a
    # small LLM guessing whether "Burj Khalifa" appears in its own
    # context is exactly the kind of judgment call it gets wrong under
    # pressure to be helpful. A plain substring check is deterministic.
    landmark_note = ""

    if landmark:

        landmark_grounded = any(
            landmark.lower() in doc["text"].lower() for doc in documents
        )

        if not landmark_grounded:

            landmark_note = (
                f'\nThe user asked about "{landmark}" specifically. The '
                "indexed corpus has no landmark-level metadata for it — "
                "only city-level coverage. Say plainly that this "
                "landmark was searched but couldn't be grounded in the "
                "indexed metadata, and describe the city-level data "
                "shown in the context instead. Never invent coordinates "
                "or metadata specific to the landmark itself."
            )

    # Told explicitly, not left for the model to infer: an earlier
    # version of this prompt only mentioned satellite imagery in its
    # rules, and the model then described EVERY query — including
    # pure road-network ones with zero satellite documents in
    # context — as a satellite-imagery search. Computing the real
    # type(s) present and stating it plainly removed that failure
    # mode in testing (see llama_client.py for the accompanying
    # generation-parameter tuning that fixed a related regression).
    retrieved_types = {doc.get("type") for doc in documents}

    if retrieved_types == {"satellite"}:
        dataset_description = "Sentinel-2 satellite imagery metadata"
    elif retrieved_types == {"roads"}:
        dataset_description = "OpenStreetMap road network data"
    elif retrieved_types:
        dataset_description = "a mix of Sentinel-2 satellite imagery metadata and OpenStreetMap road network data"
    else:
        dataset_description = "no matching data"

    # ----------------------------------------
    # Prompt
    # ----------------------------------------

    prompt = f"""
You are MANARA, a Geospatial Intelligence Assistant for the UAE, grounded in an indexed corpus of Sentinel-2 satellite metadata and OpenStreetMap road network data.

{language_instruction}

Tone: concise, professional, domain-aware — like a GIS analyst briefing a colleague. No generic chatbot filler ("I'm an AI assistant..."). No unsolicited textbook explanations.

Detected intent: {intent}
Detected entities: {entity_summary}
The context retrieved for THIS question is: {dataset_description}.

Rules:
1. Base your answer strictly on the retrieved context below — describe what is ACTUALLY there, not what you'd expect this system to contain. Never invent facts, figures, or dataset names.
2. This system stores metadata only (acquisition time, cloud cover, bounding boxes, road segment counts/lengths) — never rendered images. Only mention that distinction if the user is specifically asking to view or see satellite pictures; do not bring it up for road or analytics questions.
3. If the context doesn't fully answer the question, say specifically what was searched, what's available, what's missing, and why — never a bare "not enough information".
4. If the question is broad (e.g. no location specified), answer with what's available, then suggest one or two sharper example queries this corpus can answer.
5. Prefer short bullet points over long paragraphs when listing more than one fact (road types, dates, cloud cover values, comparisons). Keep prose sections brief.
6. Never combine numeric values (bounding boxes, cloud cover, counts) from DIFFERENT documents into one synthesized range or total unless the context explicitly states that combined figure. List each document's own values separately instead.
7. Bounding boxes are [min_longitude, min_latitude, max_longitude, max_latitude] in decimal degrees. Reproduce them exactly as given in the context, attributed to their specific document — never paraphrase them into a prose geographic description (distances, compass directions, city extents), and never re-derive or estimate a bounding box that isn't literally present in the context.
{landmark_note}
-----------------------------------------------------
Retrieved context ({len(documents)} source(s)):

{context if documents else "(no matching documents were retrieved)"}
-----------------------------------------------------

Question: {question}
-----------------------------------------------------

Answer:
"""

    # ----------------------------------------
    # Generate using Router
    # ----------------------------------------

    answer = router.generate(

        question,

        prompt

    )

    # Confidence is computed deterministically in main.py from the
    # actual top retrieval score, then appended here rather than
    # asked of the model — see the landmark-grounding comment above
    # for why an LLM's own self-assessment isn't trusted for this.
    if confidence:

        label = CONFIDENCE_LABEL[language][confidence]

        answer = f"{answer}\n\n*{label}*"

    return answer