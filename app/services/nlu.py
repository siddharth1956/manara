import re


class IntentClassifier:

    def __init__(self):

        self.locations = [
            "dubai",
            "abu dhabi",
            "sharjah",
            "ajman",
            "uae",
            "bur dubai"
        ]

        self.satellites = [
            "sentinel-2a",
            "sentinel-2b",
            "sentinel-2",
            "sentinel",
            "copernicus"
        ]

        self.metrics = [
            "cloud",
            "cloud cover",
            "average",
            "highest",
            "lowest",
            "minimum",
            "maximum"
        ]

    # ----------------------------------------------------
    # Text Preprocessing
    # ----------------------------------------------------

    def preprocess(self, query):

        query = query.lower()

        query = re.sub(
            r"[^a-z0-9\- ]",
            "",
            query
        )

        return query

    # ----------------------------------------------------
    # Intent Classification (Weighted Scoring)
    # ----------------------------------------------------

    def classify(self, query):

        q = self.preprocess(query)

        scores = {

            "analytics": 0,
            "satellite_search": 0,
            "road_search": 0,
            "comparison": 0,
            "map": 0,
            "general": 0

        }

        # ====================================
        # Analytics
        # ====================================

        analytics_keywords = {

            "average": 5,
            "mean": 5,
            "highest": 5,
            "lowest": 5,
            "minimum": 5,
            "maximum": 5,
            "statistics": 5,
            "analytics": 5,
            "analysis": 5,
            "analyze": 5,
            "distribution": 4,
            "count": 5,
            "number": 5,
            "how many": 6,
            "total": 5,
            "cloud cover": 4

        }

        for word, weight in analytics_keywords.items():

            if word in q:
                scores["analytics"] += weight

        # ====================================
        # Satellite
        # ====================================

        satellite_keywords = {

            "satellite": 3,
            "sentinel": 4,
            "sentinel-2": 5,
            "sentinel-2a": 5,
            "sentinel-2b": 5,
            "image": 2,
            "images": 2,
            "imagery": 3,
            "scene": 2,
            "scenes": 2,
            "copernicus": 3

        }

        for word, weight in satellite_keywords.items():

            if word in q:
                scores["satellite_search"] += weight

        # ====================================
        # Roads
        # ====================================

        road_keywords = {

            "road": 4,
            "roads": 4,
            "street": 3,
            "traffic": 3,
            "route": 3,
            "highway": 3,
            "motorway": 3

        }

        for word, weight in road_keywords.items():

            if word in q:
                scores["road_search"] += weight

        # ====================================
        # Comparison
        # ====================================

        comparison_keywords = {

            "compare": 6,
            "comparison": 6,
            "difference": 6,
            "versus": 6,
            "vs": 6

        }

        for word, weight in comparison_keywords.items():

            if word in q:
                scores["comparison"] += weight

        # ====================================
        # Map
        # ====================================

        map_keywords = {

            "map": 4,
            "location": 4,
            "where": 3,
            "near": 3,
            "nearby": 3,
            "coordinates": 4

        }

        for word, weight in map_keywords.items():

            if word in q:
                scores["map"] += weight

        best_intent = max(
            scores,
            key=scores.get
        )

        if scores[best_intent] == 0:
            return "general"

        return best_intent

    # ----------------------------------------------------
    # Entity Extraction
    # ----------------------------------------------------

    def extract_entities(self, query):

        q = self.preprocess(query)

        entities = {}

        # Location

        for location in sorted(
            self.locations,
            key=len,
            reverse=True
        ):

            if location in q:

                entities["location"] = location

                break

        # Satellite

        for satellite in sorted(
            self.satellites,
            key=len,
            reverse=True
        ):

            if satellite in q:

                entities["satellite"] = satellite

                break

        # Metric

        for metric in sorted(
            self.metrics,
            key=len,
            reverse=True
        ):

            if metric in q:

                entities["metric"] = metric

                break

        # Date

        if "today" in q:

            entities["date"] = "today"

        elif "yesterday" in q:

            entities["date"] = "yesterday"

        elif "last week" in q:

            entities["date"] = "last_week"

        elif "last month" in q:

            entities["date"] = "last_month"

        return entities

    # ----------------------------------------------------
    # Complete Analysis
    # ----------------------------------------------------

    def analyze(self, query):

        return {

            "intent": self.classify(query),

            "entities": self.extract_entities(query)

        }