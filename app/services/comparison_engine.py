"""
Deterministic comparison synthesis.

Computes comparison tables directly from retrieved documents in code,
never by asking the LLM to recall/combine numbers across several
documents — that's exactly the failure mode fixed in generator.py
(Rules 6/7: a small model asked to synthesize a bounding box or a
total across multiple sources produces plausible-looking but wrong
numbers). This module only reads the output of retriever.py's
`retrieve()` — it doesn't change retrieval or generation, and every
number it produces is traceable to a real field on a real retrieved
document.
"""

import re

# Mirrors the location vocabulary nlu.py/location_mapper.py already
# recognize — not inventing new geography, just scanning for more than
# one match, since entities["location"] can only ever hold one.
KNOWN_LOCATIONS = {
    "dubai": ["dubai", "دبي"],
    "abu dhabi": ["abu dhabi", "أبوظبي", "ابوظبي", "أبو ظبي"],
    "sharjah": ["sharjah", "الشارقة"],
    "ajman": ["ajman", "عجمان"],
    "ras al khaimah": ["ras al khaimah", "رأس الخيمة"],
    "fujairah": ["fujairah", "الفجيرة"],
    "umm al quwain": ["umm al quwain", "أم القيوين"],
}

KNOWN_SATELLITES = ["sentinel-2a", "sentinel-2b"]


def extract_all_locations(text):
    """Every known city mentioned in the query, in order of appearance —
    independent of nlu.py's single-field entities["location"]."""
    lowered = text.lower()
    found = []
    for canonical, synonyms in KNOWN_LOCATIONS.items():
        if any(s.lower() in lowered for s in synonyms) and canonical not in found:
            found.append(canonical)
    return found


def extract_all_satellites(text):
    lowered = text.lower()
    return [s for s in KNOWN_SATELLITES if s in lowered]


_DISPLAY_NAMES = {
    "english": {
        "dubai": "Dubai", "abu dhabi": "Abu Dhabi", "sharjah": "Sharjah",
        "ajman": "Ajman", "ras al khaimah": "Ras Al Khaimah",
        "fujairah": "Fujairah", "umm al quwain": "Umm Al Quwain",
    },
    "arabic": {
        "dubai": "دبي", "abu dhabi": "أبوظبي", "sharjah": "الشارقة",
        "ajman": "عجمان", "ras al khaimah": "رأس الخيمة",
        "fujairah": "الفجيرة", "umm al quwain": "أم القيوين",
    },
}


def display_name(canonical, language):
    """Localized label for a comparison table column/intro sentence —
    Arabic responses get the Arabic city name, not a transliteration."""
    if canonical in KNOWN_LOCATIONS:
        return _DISPLAY_NAMES[language][canonical]
    # Satellites — same display name in both languages.
    return {"sentinel-2a": "Sentinel-2A", "sentinel-2b": "Sentinel-2B"}.get(canonical, canonical)


_SEGMENTS_RE = re.compile(r"Segments:\s*\n?\s*(\d+)")
_LENGTH_RE = re.compile(r"Total Length:\s*\n?\s*([\d.]+)\s*km")
_ROAD_TYPE_RE = re.compile(r"Road Type:\s*\n?\s*([^\n]+)")


def _parse_road_doc(text):
    segments = _SEGMENTS_RE.search(text)
    length = _LENGTH_RE.search(text)
    road_type = _ROAD_TYPE_RE.search(text)
    return {
        "segments": int(segments.group(1)) if segments else None,
        "length_km": float(length.group(1)) if length else None,
        "road_type": road_type.group(1).strip() if road_type else None,
    }


def summarize_documents(documents):
    """Deterministic aggregate stats for one side of a comparison —
    every value is computed from the documents themselves or explicitly
    None (rendered as "Not available in indexed dataset"), never
    guessed."""

    roads = [d for d in documents if d.get("type") == "roads"]
    satellites = [d for d in documents if d.get("type") == "satellite"]

    total_length = 0.0
    total_segments = 0
    road_types = []
    has_length = False
    has_segments = False

    for doc in roads:
        parsed = _parse_road_doc(doc.get("text", ""))
        if parsed["length_km"] is not None:
            total_length += parsed["length_km"]
            has_length = True
        if parsed["segments"] is not None:
            total_segments += parsed["segments"]
            has_segments = True
        if parsed["road_type"]:
            for road_type in parsed["road_type"].split(","):
                road_type = road_type.strip()
                if road_type and road_type not in road_types:
                    road_types.append(road_type)

    cloud_values = [
        d["cloud_cover"] for d in satellites if d.get("cloud_cover") is not None
    ]

    return {
        "road_documents": len(roads) or None,
        "road_total_length_km": round(total_length, 2) if has_length else None,
        "road_total_segments": total_segments if has_segments else None,
        "road_types": ", ".join(road_types) if road_types else None,
        "satellite_documents": len(satellites) or None,
        "avg_cloud_cover": (
            round(sum(cloud_values) / len(cloud_values), 2) if cloud_values else None
        ),
    }


_ROW_LABELS = {
    "english": [
        ("Road documents retrieved", "road_documents"),
        ("Total road length (km)", "road_total_length_km"),
        ("Total road segments", "road_total_segments"),
        ("Road types found", "road_types"),
        ("Satellite scenes retrieved", "satellite_documents"),
        ("Average cloud cover (%)", "avg_cloud_cover"),
    ],
    "arabic": [
        ("عدد وثائق الطرق المسترجعة", "road_documents"),
        ("إجمالي طول الطرق (كم)", "road_total_length_km"),
        ("إجمالي عدد الأجزاء", "road_total_segments"),
        ("أنواع الطرق الموجودة", "road_types"),
        ("عدد مشاهد الأقمار الصناعية المسترجعة", "satellite_documents"),
        ("متوسط الغطاء السحابي (%)", "avg_cloud_cover"),
    ],
}

_NOT_AVAILABLE = {
    "english": "Not available in indexed dataset",
    "arabic": "غير متوفر في البيانات المفهرسة",
}

_METRIC_HEADER = {"english": "Metric", "arabic": "المقياس"}


def _fmt(value, language):
    return _NOT_AVAILABLE[language] if value is None else str(value)


def build_comparison_table(label_a, summary_a, label_b, summary_b, language):
    header = _METRIC_HEADER[language]
    lines = [
        f"| {header} | {label_a} | {label_b} |",
        "|---|---|---|",
    ]
    for row_label, key in _ROW_LABELS[language]:
        lines.append(
            f"| {row_label} | {_fmt(summary_a.get(key), language)} "
            f"| {_fmt(summary_b.get(key), language)} |"
        )
    return "\n".join(lines)


def comparison_intro(label_a, label_b, language):
    if language == "arabic":
        return f"بناءً على البيانات المسترجعة، إليك مقارنة بين {label_a} و{label_b}:"
    return f"Based on the retrieved data, here's a comparison between {label_a} and {label_b}:"
