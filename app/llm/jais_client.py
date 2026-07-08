from app.llm.base import BaseLLM


class JaisClient(BaseLLM):

    def __init__(self):

        self.available = False

    def generate(self, prompt):

        if not self.available:

            return (
                "JAIS model is not available on the local machine. "
                "Arabic requests should be executed on the configured "
                "GPU deployment during evaluation."
            )

        # Future implementation
        pass