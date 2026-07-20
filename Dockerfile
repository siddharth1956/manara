# MANARA backend — FastAPI + the retrieval/generation pipeline.
#
# No Ollama here (unlike earlier revisions of this file) — the
# deployed instance uses Groq's free hosted inference API instead
# (app/llm/groq_client.py, selected by router.py when GROQ_API_KEY is
# set) specifically because self-hosting Ollama's multi-GB memory
# footprint doesn't fit any genuinely free, no-card hosting platform.
# Local development is unaffected and keeps using Ollama directly.

FROM python:3.10-slim

WORKDIR /app

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

COPY app/ ./app/

# Only the small runtime-required artifacts — NOT data/processed/manara_dataset.csv
# (937MB, a data-pipeline intermediate never read at request time; see
# CLAUDE.md's data pipeline section).
COPY data/processed/search_corpus.csv ./data/processed/search_corpus.csv
COPY data/embeddings/faiss_index.bin ./data/embeddings/faiss_index.bin
COPY data/embeddings/bm25_index.pkl ./data/embeddings/bm25_index.pkl

EXPOSE 8000

CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
