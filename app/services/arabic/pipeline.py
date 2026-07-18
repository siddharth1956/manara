from app.services.arabic.normalizer import ArabicNormalizer
from app.services.arabic.tokenizer import ArabicTokenizer
from app.services.arabic.ner import ArabicNER
from app.services.arabic.intent import ArabicIntentClassifier


class ArabicPipeline:

    def __init__(self):

        self.normalizer = ArabicNormalizer()

        self.tokenizer = ArabicTokenizer()

        self.ner = ArabicNER()

        self.intent = ArabicIntentClassifier()

    def analyze(self, text):

        # Step 1
        normalized = self.normalizer.normalize(text)

        # Step 2
        tokens = self.tokenizer.tokenize(normalized)

        # Step 3
        entities = self.ner.extract(normalized)

        # Step 4
        intent = self.intent.classify(normalized)

        return {

            "normalized": normalized,

            "tokens": tokens,

            "intent": intent,

            "entities": entities

        }