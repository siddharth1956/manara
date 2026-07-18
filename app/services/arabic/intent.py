class ArabicIntentClassifier:

    def __init__(self):

        self.intents = {

            "analytics": [
                "الغطاء السحابي",
                "السحب",
                "غيوم",
                "النباتات",
                "الغطاء النباتي",
                "ndvi"
            ],

            "road_search": [
                "الطرق",
                "طرق",
                "طريق",
                "شارع",
                "شوارع",
                "المرور",
                "شبكه الطرق"
            ],

            "satellite_search": [
                "قمر",
                "اقمار",
                "الاقمار",
                "الاقمار الصناعيه",
                "صوره",
                "صور",
                "ساتلايت",
                "سنتينل"
            ],

            "comparison": [
                "قارن",
                "يقارن",
                "مقارنه",
                "المقارنه",
                "الفرق",
                "الاختلاف",
                "مقابل"
            ],

            "map": [
                "خريطه",
                "الخريطه",
                "اين",
                "موقع",
                "قريب",
                "بالقرب",
                "احداثيات"
            ]

        }

    def classify(self, text):

        scores = {}

        for intent, keywords in self.intents.items():

            scores[intent] = 0

            for keyword in keywords:

                if keyword in text:

                    scores[intent] += 1

        best_intent = max(scores, key=scores.get)

        if scores[best_intent] == 0:

            return "general"

        return best_intent