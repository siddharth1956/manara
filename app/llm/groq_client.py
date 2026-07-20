import os

from groq import Groq

from app.llm.base import BaseLLM


class GroqClient(BaseLLM):
    """
    Free hosted inference, used in place of local Ollama specifically
    for deployment — self-hosted Ollama needs several GB of RAM
    resident (model + runtime), which no genuinely free, no-card
    hosting platform provides. Groq's free tier needs no card and its
    rate limits (30 req/min, 14,400/day) are well beyond what a
    single-instance demo app generates. See router.py for how this is
    selected only when configured — local development keeps using
    Ollama unchanged.
    """

    def __init__(self):

        self.client = Groq(api_key=os.environ["GROQ_API_KEY"])

        self.model = "llama-3.1-8b-instant"

    def generate(self, prompt):

        response = self.client.chat.completions.create(

            model=self.model,

            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            # Matches the temperature/repeat-loop calibration done for
            # the local model (see llama_client.py) — kept the same
            # rather than re-tuned, since this is a deployment-driven
            # swap, not a quality pass. num_predict's Ollama name is
            # max_tokens on Groq's OpenAI-compatible API.
            temperature=0.4,
            max_tokens=600,

        )

        return response.choices[0].message.content
