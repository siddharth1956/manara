from app.services.language_detector import detect_language

from app.llm.llama_client import LlamaClient
from app.llm.jais_client import JaisClient


class LLMRouter:

    def __init__(self):

        self.llama = LlamaClient()

        self.jais = JaisClient()

    def generate(self, question, prompt):

        language = detect_language(question)

        if language == "arabic":

            if self.jais.available:

                return self.jais.generate(prompt)

            # Fallback
            return self.llama.generate(prompt)

        return self.llama.generate(prompt)