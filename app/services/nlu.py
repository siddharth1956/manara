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

        # Canonical metric categories, checked before self.metrics below —
        # so a synonym like "greener" or "cloud coverage" normalizes to
        # the same value retriever.py's normalize_metric() already
        # recognizes ("vegetation" / "cloud cover"), regardless of which
        # exact word the user used. Kept separate from the aggregation
        # operators in self.metrics (average/highest/...) so that
        # existing behavior for those is untouched.
        self.metric_synonyms = {
            "cloud cover": [
                "cloud", "cloud cover", "cloud coverage", "cloudy", "clouds"
            ],
            "vegetation": [
                "vegetation", "ndvi", "greenery", "green cover", "greener",
                "greenest", "healthier vegetation", "healthy vegetation",
                "vegetation health", "crops", "forest", "forests",
                "ecological", "environmental", "land cover"
            ],
        }

        self.metrics = [
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
            "cloud cover": 4,

            # Vegetation/environmental — routes these to analytics instead
            # of falling through to "general" (see conversation_router.py's
            # vegetation short-circuit: the indexed corpus has zero
            # vegetation/NDVI documents, confirmed by direct inspection,
            # so these always get an honest "not indexed" response rather
            # than a fabricated one — this fix is about routing, not
            # answering).
            "vegetation": 5,
            "ndvi": 6,
            "greenery": 5,
            "green cover": 5,
            "greener": 5,
            "greenest": 5,
            "healthier vegetation": 6,
            "healthy vegetation": 6,
            "vegetation health": 6,
            "crops": 4,
            "forest": 4,
            "forests": 4,
            "ecological": 4,
            "environmental": 4,
            "land cover": 4

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

        metric_found = False

        for canonical, synonyms in self.metric_synonyms.items():

            for synonym in sorted(synonyms, key=len, reverse=True):

                if synonym in q:

                    entities["metric"] = canonical

                    metric_found = True

                    break

            if metric_found:

                break

        if not metric_found:

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