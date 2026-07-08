from app.llm.router import LLMRouter

# ----------------------------------------
# Initialize Router
# ----------------------------------------

router = LLMRouter()


def generate_answer(question, documents):
    """
    Generate answer using the selected LLM.
    """

    # ----------------------------------------
    # Build Context
    # ----------------------------------------

    context = ""

    for doc in documents:
        context += doc["text"] + "\n\n"

    # ----------------------------------------
    # Prompt
    # ----------------------------------------

    prompt = f"""
You are MANARA, an AI Geospatial Intelligence Assistant.

Answer ONLY using the provided context.

If the context does not contain enough information, reply:

"The available geospatial data does not contain enough information."

Context:
{context}

Question:
{question}

Answer:
"""

    # ----------------------------------------
    # Generate using Router
    # ----------------------------------------

    return router.generate(question, prompt)