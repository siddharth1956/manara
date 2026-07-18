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

            ],

            # Calibrated empirically against this exact model, not
            # guessed: an initial attempt at temperature=0.3 with
            # repeat_penalty=1.1 made responses *worse* — this small
            # (3B) model fell into a degenerate loop repeating the same
            # sentence for 1900+ characters on one real query, and on
            # another incorrectly claimed no road data existed despite
            # it being in context. temperature=0.3 was too deterministic
            # for this model's long, structured prompt, and 1.1 wasn't
            # enough repeat penalty to stop the loop it caused.
            # Re-tested with the values below; verified against the
            # same failing queries before keeping them (see generator.py
            # for the accompanying language-instruction change and
            # project history for the full before/after transcripts).
            options={
                "temperature": 0.4,
                "repeat_penalty": 1.3,
                # Hard ceiling regardless of the above: a single
                # request should never be able to tie up generation
                # indefinitely — this was observed directly (a
                # degenerate response ran past 3 minutes before the
                # client gave up) prior to adding this cap.
                "num_predict": 600,
            }

        )

        return response["message"]["content"]