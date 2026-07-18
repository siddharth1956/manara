class ArabicNER:

    def __init__(self):

        self.locations = [
            "دبي",
            "أبوظبي",
            "الشارقة",
            "العين",
            "عجمان",
            "الفجيرة",
            "رأس الخيمة",
            "أم القيوين"
        ]

        self.metrics = [
            "الغطاء السحابي",
            "السحب",
            "النباتات",
            "الغطاء النباتي",
            "ndvi"
        ]

    def extract(self, text):

        entities = {
            "location": None,
            "metric": None
        }

        for location in self.locations:

            if location in text:

                entities["location"] = location

                break

        for metric in self.metrics:

            if metric in text:

                entities["metric"] = metric

                break

        return entities