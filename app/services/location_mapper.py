LOCATION_MAP = {

    # UAE

    "دبي": "dubai",
    "ابوظبي": "abu dhabi",
    "أبوظبي": "abu dhabi",
    "أبو ظبي": "abu dhabi",
    "الشارقة": "sharjah",
    "عجمان": "ajman",
    "رأس الخيمة": "ras al khaimah",
    "الفجيرة": "fujairah",
    "أم القيوين": "umm al quwain",

}


def normalize_location(location):

    if location is None:
        return None

    location = location.lower().strip()

    return LOCATION_MAP.get(location, location)