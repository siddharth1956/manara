import os

from app.services.language_detector import detect_language

from app.llm.llama_client import LlamaClient
from app.llm.jais_client import JaisClient


class LLMRouter:

    def __init__(self):

        # Local development keeps calling Ollama, unchanged — GROQ_API_KEY
        # is only set in the deployed environment, where self-hosting
        # Ollama's multi-GB memory footprint doesn't fit a free,
        # no-card host (see groq_client.py).
        if os.environ.get("GROQ_API_KEY"):

            from app.llm.groq_client import GroqClient

            self.english_llm = GroqClient()

        else:

            self.english_llm = LlamaClient()

        self.jais = JaisClient()

    def generate(self, question, prompt):

        language = detect_language(question)

        if language == "arabic":

            if self.jais.available:

                return self.jais.generate(prompt)

            # Fallback
            return self.english_llm.generate(prompt)

        return self.english_llm.generate(prompt)