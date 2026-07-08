import re


class ArabicNLU:

    def preprocess(self, text):

        text = text.strip()

        text = re.sub(r"\s+", " ", text)

        return text

    def classify(self, query):

        query = self.preprocess(query)

        if any(word in query for word in [
            "قارن",
            "مقارنة",
            "فرق"
        ]):
            return "comparison"

        if any(word in query for word in [
            "متوسط",
            "أعلى",
            "أقل",
            "عدد",
            "إحصائيات"
        ]):
            return "analytics"

        if any(word in query for word in [
            "طريق",
            "طرق",
            "شارع"
        ]):
            return "road_search"

        if any(word in query for word in [
            "قمر",
            "صورة",
            "ساتل",
            "Sentinel",
            "سينتينل"
        ]):
            return "satellite_search"

        if any(word in query for word in [
            "أين",
            "خريطة",
            "موقع"
        ]):
            return "map"

        return "general"