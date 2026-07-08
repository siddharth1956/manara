import re


def detect_language(text):

    """
    Detect whether the query is English or Arabic.
    """

    arabic = re.search(r'[\u0600-\u06FF]', text)

    if arabic:
        return "arabic"

    return "english"