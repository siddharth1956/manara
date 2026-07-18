"""
Pre/post-processing around the existing NLU + retrieval pipeline.

Nothing here touches nlu.py, app/services/arabic/*, or retriever.py —
those stay exactly as they are. This module only adds a routing layer
that decides, using their OUTPUT, whether a query should reach
FAISS/BM25 at all:

- Chit-chat (greeting/farewell/thanks/capability/limitation/out-of-
  scope) is only classified when the existing classifier already
  returned "general" (i.e. no dataset keyword matched) — so this never
  overrides a real dataset intent, it just adds nuance underneath one
  that already fell through to the catch-all bucket.
- Follow-up inheritance and landmark detection likewise only fill in
  gaps (a missing intent/location) rather than override anything the
  existing NLU already found.
"""

import re

# ----------------------------------------------------
# Chit-chat classification (only called when intent == "general")
# ----------------------------------------------------

GREETING_PATTERNS = [
    r"\bhello\b", r"\bhi\b", r"\bhey\b", r"\bgood morning\b",
    r"\bgood afternoon\b", r"\bgood evening\b", r"\bgreetings\b",
    r"\bمرحبا\b", r"\bأهلا\b", r"\bاهلا\b", r"\bالسلام عليكم\b",
    r"\bصباح الخير\b", r"\bمساء الخير\b", r"\bهلا\b",
]

FAREWELL_PATTERNS = [
    r"\bbye\b", r"\bgoodbye\b", r"\bsee you\b", r"\btake care\b",
    r"\bfarewell\b",
    r"\bمع السلامة\b", r"\bوداعا\b", r"\bإلى اللقاء\b", r"\bالى اللقاء\b",
]

THANKS_PATTERNS = [
    r"\bthanks\b", r"\bthank you\b", r"\bthx\b", r"\bappreciate it\b",
    r"\bشكرا\b", r"\bشكراً\b", r"\bمشكور\b",
]

# Checked before CAPABILITY — "what can't you do" contains "can" and
# must not be misread as a capability question.
LIMITATION_PATTERNS = [
    r"what can'?t you do", r"what cant you do", r"what don'?t you (do|support)",
    r"what are your limitations", r"what you cannot do", r"limitations",
    r"ماذا لا (تستطيع|يمكنك)", r"ما هي حدود(ك)?", r"ما لا تستطيع",
]

CAPABILITY_PATTERNS = [
    r"what can you do", r"what do you do", r"what are you capable of",
    r"how can you help", r"your capabilities", r"your features",
    r"ماذا تستطيع", r"ما الذي يمكنك", r"ماذا يمكنك ان تفعل", r"قدراتك",
]


def _matches_any(text, patterns):
    return any(re.search(p, text, re.IGNORECASE) for p in patterns)


def classify_chitchat(text, language):
    """
    Only meaningful when the real NLU already returned "general" for
    this query. Returns one of: greeting, farewell, thanks,
    capability_question, limitation_question, general_out_of_scope.
    """
    lowered = text.lower().strip()

    if _matches_any(lowered, LIMITATION_PATTERNS):
        return "limitation_question"
    if _matches_any(lowered, CAPABILITY_PATTERNS):
        return "capability_question"
    if _matches_any(lowered, GREETING_PATTERNS):
        return "greeting"
    if _matches_any(lowered, FAREWELL_PATTERNS):
        return "farewell"
    if _matches_any(lowered, THANKS_PATTERNS):
        return "thanks"

    return "general_out_of_scope"


CHITCHAT_RESPONSES = {
    "greeting": {
        "english": (
            "Hello! I'm MANARA, a geospatial intelligence assistant for "
            "the UAE. I can help you explore:\n\n"
            "- **Satellite imagery** — Sentinel-2 acquisition metadata, "
            "cloud cover, coverage areas\n"
            "- **Road networks** — OpenStreetMap road types, segment "
            "counts, lengths\n"
            "- **Analytics** — vegetation (NDVI) and cloud coverage "
            "statistics\n"
            "- **Comparisons** — between satellites, cities, or dataset "
            "types\n\n"
            "What would you like to know?"
        ),
        "arabic": (
            "مرحباً! أنا منارة، مساعد استخباراتي جغرافي مختص بدولة "
            "الإمارات. يمكنني مساعدتك في استكشاف:\n\n"
            "- **صور الأقمار الصناعية** — بيانات سنتينل-2 الوصفية، "
            "الغطاء السحابي، مناطق التغطية\n"
            "- **شبكات الطرق** — أنواع الطرق من OpenStreetMap، عدد "
            "الأجزاء، الأطوال\n"
            "- **التحليلات** — الغطاء النباتي (NDVI) وإحصاءات الغطاء "
            "السحابي\n"
            "- **المقارنات** — بين الأقمار الصناعية أو المدن\n\n"
            "كيف يمكنني مساعدتك؟"
        ),
    },
    "farewell": {
        "english": (
            "Goodbye! Feel free to come back anytime you need to explore "
            "UAE satellite or road network data."
        ),
        "arabic": (
            "مع السلامة! لا تتردد في العودة في أي وقت لاستكشاف بيانات "
            "الأقمار الصناعية أو شبكات الطرق في الإمارات."
        ),
    },
    "thanks": {
        "english": (
            "You're welcome! Let me know if you'd like to explore more "
            "satellite, road, or analytics data."
        ),
        "arabic": (
            "على الرحب والسعة! أخبرني إذا أردت استكشاف المزيد من بيانات "
            "الأقمار الصناعية أو الطرق أو التحليلات."
        ),
    },
    "capability_question": {
        "english": (
            "I'm MANARA, a Geospatial Intelligence Assistant for the "
            "UAE. Here's what I can do:\n\n"
            "**Available**\n"
            "- Search Sentinel-2 satellite imagery metadata (acquisition "
            "time, cloud cover, bounding boxes)\n"
            "- Search OpenStreetMap road network data (road types, "
            "segment counts, lengths)\n"
            "- Run analytics — vegetation (NDVI) and cloud coverage "
            "statistics\n"
            "- Compare satellites (e.g. Sentinel-2A vs 2B) or locations\n"
            "- Show retrieval sources and map coverage for every answer\n\n"
            "**Not available**\n"
            "- Rendering or displaying actual satellite images (metadata "
            "only)\n"
            "- Data outside the UAE or outside the indexed date range\n"
            "- Real-time or live satellite feeds\n\n"
            'Try asking things like "Show Dubai roads" or "Analyze cloud '
            'coverage over Abu Dhabi".'
        ),
        "arabic": (
            "أنا منارة، مساعد استخباراتي جغرافي مختص بدولة الإمارات. "
            "إليك ما يمكنني فعله:\n\n"
            "**المتوفر**\n"
            "- البحث في البيانات الوصفية لصور الأقمار الصناعية سنتينل-2 "
            "(وقت الالتقاط، الغطاء السحابي، الحدود الجغرافية)\n"
            "- البحث في بيانات شبكة الطرق من OpenStreetMap (أنواع "
            "الطرق، عدد الأجزاء، الأطوال)\n"
            "- إجراء تحليلات — الغطاء النباتي (NDVI) وإحصاءات الغطاء "
            "السحابي\n"
            "- مقارنة الأقمار الصناعية أو المواقع\n"
            "- عرض مصادر الاسترجاع وتغطية الخريطة لكل إجابة\n\n"
            "**غير المتوفر**\n"
            "- عرض صور الأقمار الصناعية الفعلية (البيانات الوصفية "
            "فقط)\n"
            "- بيانات خارج دولة الإمارات أو خارج النطاق الزمني "
            "المفهرس\n"
            "- بث مباشر أو لحظي للأقمار الصناعية\n\n"
            'جرّب أسئلة مثل "اعرض الطرق في دبي" أو "حلل الغطاء السحابي '
            'في أبوظبي".'
        ),
    },
    "limitation_question": {
        "english": (
            "Here's what I can't do:\n\n"
            "- Render or display actual satellite images — I only have "
            "acquisition metadata (cloud cover, bounding boxes, "
            "timestamps), not pixel data\n"
            "- Cover locations outside the UAE\n"
            "- Access data outside the currently indexed date range\n"
            "- Provide real-time or live satellite feeds\n"
            "- Answer general knowledge questions outside geospatial/UAE "
            "data\n\n"
            "I can show you exactly what metadata is available for a "
            "given location or satellite pass — just ask."
        ),
        "arabic": (
            "إليك ما لا أستطيع فعله:\n\n"
            "- عرض صور الأقمار الصناعية الفعلية — لدي فقط بيانات "
            "الالتقاط الوصفية (الغطاء السحابي، الحدود الجغرافية، "
            "الطوابع الزمنية)، وليس بيانات الصورة نفسها\n"
            "- تغطية مواقع خارج دولة الإمارات\n"
            "- الوصول إلى بيانات خارج النطاق الزمني المفهرس حالياً\n"
            "- تقديم بث مباشر أو لحظي للأقمار الصناعية\n"
            "- الإجابة عن أسئلة عامة خارج نطاق البيانات الجغرافية "
            "الإماراتية\n\n"
            "يمكنني أن أوضح لك بالضبط ما هي البيانات المتوفرة لموقع أو "
            "قمر صناعي معين — فقط اسأل."
        ),
    },
    "general_out_of_scope": {
        "english": (
            "That's outside what I'm built for — I specialize in "
            "geospatial intelligence for the UAE: satellite imagery "
            "metadata, road networks, and related analytics. Try asking "
            'about a location, satellite, or dataset instead — for '
            'example "Show Dubai roads" or "Analyze cloud coverage over '
            'Abu Dhabi".'
        ),
        "arabic": (
            "هذا خارج نطاق تخصصي — أنا مختص باستخبارات جغرافية لدولة "
            "الإمارات: بيانات الأقمار الصناعية الوصفية وشبكات الطرق "
            "والتحليلات المرتبطة بها. جرّب أن تسأل عن موقع أو قمر صناعي "
            'أو بيانات محددة، مثلاً "اعرض الطرق في دبي" أو "حلل الغطاء '
            'السحابي في أبوظبي".'
        ),
    },
}


def chitchat_response(category, language):
    return CHITCHAT_RESPONSES[category][language]


# ----------------------------------------------------
# Follow-up queries — fills gaps in a "general"-intent query using the
# previous turn's intent/entities, supplied by the frontend as `context`.
# ----------------------------------------------------

FOLLOWUP_PHRASE_PATTERNS = [
    r"^what about\b", r"^how about\b", r"^and what about\b", r"^what of\b",
    r"^and\b",
    r"^ماذا عن\b", r"^وماذا عن\b", r"^ماذا بخصوص\b",
]

FOLLOWUP_ELIGIBLE_INTENTS = {
    "road_search", "satellite_search", "analytics", "comparison", "map",
}


def is_followup_query(text, entities):
    """
    True if this looks like it's continuing the previous turn rather
    than starting a new topic — either it matches a follow-up phrase
    ("what about...") or the (intent-independent) entity extraction
    already found something concrete (e.g. a bare "Abu Dhabi").
    """
    lowered = text.lower().strip()
    if _matches_any(lowered, FOLLOWUP_PHRASE_PATTERNS):
        return True
    return any(entities.values())


def resolve_followup(intent, entities, context):
    """
    context is the frontend-supplied {"intent": ..., "entities": ...}
    from the previous turn. Returns (intent, entities) with gaps filled
    from context — new entities this turn always win over inherited ones.
    """
    inherited_intent = context.get("intent")
    if inherited_intent not in FOLLOWUP_ELIGIBLE_INTENTS:
        return intent, entities

    inherited_entities = context.get("entities") or {}
    merged = dict(inherited_entities)
    merged.update({k: v for k, v in entities.items() if v})

    return inherited_intent, merged


# ----------------------------------------------------
# Comparison clarification — never guess which two things to compare.
# ----------------------------------------------------

def needs_clarification(intent, entities):
    if intent != "comparison":
        return False
    return not entities.get("location") and not entities.get("satellite")


CLARIFICATION_RESPONSES = {
    "english": (
        'Which would you like me to compare? For example: "Compare '
        'Dubai and Abu Dhabi" or "Compare Sentinel-2A and Sentinel-2B".'
    ),
    "arabic": (
        "ما الذي تود أن أقارن بينه؟ على سبيل المثال: \"قارن بين دبي "
        "وأبوظبي\" أو \"قارن بين Sentinel-2A و Sentinel-2B\"."
    ),
}


def clarification_response(language):
    return CLARIFICATION_RESPONSES[language]


# ----------------------------------------------------
# Landmark detection — maps a known landmark name to its containing
# city, purely so retrieval can fall back to city-level entity boosting
# and the generated answer can be explicit about what was searched.
# Never used to invent coordinates.
# ----------------------------------------------------

LANDMARKS = {
    "burj khalifa": "dubai",
    "برج خليفة": "dubai",
    "dubai marina": "dubai",
    "دبي مارينا": "dubai",
    "مارينا دبي": "dubai",
    "palm jumeirah": "dubai",
    "نخلة جميرا": "dubai",
    "جزيرة النخلة": "dubai",
    "abu dhabi corniche": "abu dhabi",
    "كورنيش أبوظبي": "abu dhabi",
    "كورنيش ابوظبي": "abu dhabi",
}


def detect_landmark(text):
    lowered = text.lower()
    for landmark, city in sorted(LANDMARKS.items(), key=lambda kv: len(kv[0]), reverse=True):
        if landmark in lowered:
            return landmark, city
    return None


# ----------------------------------------------------
# Confidence bucketing — surfaced in the generated answer, derived from
# the top retrieved document's confidence score (already computed by
# retriever.py; this only labels it).
# ----------------------------------------------------

def confidence_bucket(top_confidence):
    if top_confidence is None:
        return "low"
    if top_confidence >= 70:
        return "high"
    if top_confidence >= 40:
        return "medium"
    return "low"
