import ollama

from app.llm.base import BaseLLM


class LlamaClient(BaseLLM):

    def __init__(self):

        self.model = "llama3.2:3b"

    def generate(self, prompt):

        response = ollama.chat(

            model=self.model,

            messages=[

                {
                    "role": "user",
                    "content": prompt
                }

            ]

        )

        return response["message"]["content"]