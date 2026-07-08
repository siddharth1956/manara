from app.services.language_detector import detect_language


class ModelRouter:

    def __init__(self):

        self.english_model = "llama3.2:3b"

        self.arabic_model = "llama3.2:3b"

    def get_model(self, question):

        language = detect_language(question)

        if language == "arabic":

            return self.arabic_model

        return self.english_model