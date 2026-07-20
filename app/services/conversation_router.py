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
# Vegetation/NDVI queries — deterministic short-circuit, not a prompt
# rule. Confirmed by direct inspection that the indexed corpus (Sentinel-2
# metadata + OpenStreetMap roads) contains zero documents mentioning
# "vegetation" or "ndvi" — there is no data to ground an answer in, ever,
# for this query type. Handling it as a hard short-circuit (like
# chit-chat) rather than trusting the LLM to stay honest when handed
# semantically-similar-but-irrelevant satellite/road context removes
# the fabrication risk entirely rather than mitigating it.
# ----------------------------------------------------

VEGETATION_METRIC_VALUES = {"vegetation", "النباتات", "الغطاء النباتي"}


def is_vegetation_query(entities):
    return entities.get("metric") in VEGETATION_METRIC_VALUES


VEGETATION_RESPONSES = {
    "english": (
        "The current indexed dataset does not contain NDVI or vegetation "
        "metrics, so I cannot accurately compare or assess vegetation "
        "health. What's indexed instead is Sentinel-2 acquisition "
        "metadata (cloud cover, capture dates, coverage areas) and "
        "OpenStreetMap road network data — I can help with those, e.g. "
        '"Show Dubai roads" or "Analyze cloud coverage over Abu Dhabi".'
    ),
    "arabic": (
        "لا تحتوي البيانات المفهرسة حالياً على مؤشر NDVI أو مقاييس "
        "الغطاء النباتي، لذا لا يمكنني تقييم أو مقارنة صحة الغطاء "
        "النباتي بدقة. البيانات المتوفرة بدلاً من ذلك هي البيانات "
        "الوصفية لصور الأقمار الصناعية سنتينل-2 (الغطاء السحابي، تواريخ "
        "الالتقاط، مناطق التغطية) وبيانات شبكة الطرق من OpenStreetMap — "
        'يمكنني مساعدتك بهذه البيانات، مثلاً "اعرض الطرق في دبي" أو '
        '"حلل الغطاء السحابي في أبوظبي".'
    ),
}


def vegetation_response(language):
    return VEGETATION_RESPONSES[language]


# ----------------------------------------------------
# Referential comparisons — "Compare both", "Which city has better
# coverage?", "Which one is greener?" — none name two subjects
# themselves, but all refer back to whatever the conversation was
# already comparing. Resolved against locations mentioned earlier,
# supplied by the frontend as context.mentioned_locations (accumulated
# across the last few turns, not just the immediately-preceding one —
# see web/src/pages/chat-page.tsx). Only used as a fallback: a query
# that already names two subjects itself is never overridden.
# ----------------------------------------------------

BOTH_PATTERN = re.compile(
    r"\bboth\b|\bthem\b|\bthese two\b"
    r"|\bwhich (city|one|area)\b|\bwhich of (them|these)\b"
    r"|كلاهما|كلتا|كلا|أيهما|أي (مدينة|منطقة)",
    re.IGNORECASE,
)


def is_both_reference(text):
    return bool(BOTH_PATTERN.search(text))


def resolve_comparison_subjects(question, locations, mentioned_locations):
    """Returns (possibly-expanded) locations for the comparison engine
    to use. Only touches `locations` when the query itself named fewer
    than two and the query text refers back to "both"/"them"."""

    if len(locations) >= 2:
        return locations

    if is_both_reference(question) and mentioned_locations and len(mentioned_locations) >= 2:
        return mentioned_locations[:2]

    return locations


# ----------------------------------------------------
# Confidence bucketing — the retrieval score alone is a weak signal in
# isolation: a document can score well on text/semantic relevance while
# being geographically the wrong place entirely (see main.py's
# location_coverage check) or while being the only document found.
# document_count and location_coverage are optional so existing call
# sites (e.g. the comparison engine, which already reasons about
# per-side confidence separately) keep working unchanged.
# ----------------------------------------------------

def confidence_bucket(top_confidence, document_count=None, location_coverage=None):
    if top_confidence is None:
        return "low"

    score = top_confidence

    if document_count is not None:
        if document_count <= 1:
            score -= 15
        elif document_count < 3:
            score -= 5

    if location_coverage:
        _, overlapping, total = location_coverage
        if total and overlapping == 0:
            score -= 30
        elif total and overlapping < total:
            score -= 10

    if score >= 70:
        return "high"
    if score >= 40:
        return "medium"
    return "low"


CONFIDENCE_EXPLANATIONS = {
    "english": {
        "high": "strong retrieval match across multiple confirmed documents",
        "medium": "moderate retrieval match — some fields or geographic coverage may be incomplete",
        "low": "weak or geographically unconfirmed retrieval match",
    },
    "arabic": {
        "high": "تطابق استرجاع قوي عبر عدة وثائق مؤكدة",
        "medium": "تطابق استرجاع متوسط — قد تكون بعض الحقول أو التغطية الجغرافية غير مكتملة",
        "low": "تطابق استرجاع ضعيف أو غير مؤكد جغرافياً",
    },
}


def confidence_explanation(bucket, language):
    return CONFIDENCE_EXPLANATIONS[language][bucket]
