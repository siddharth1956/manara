# MANARA backend — FastAPI + the retrieval/generation pipeline, with
# Ollama running as a second process in the same container (see
# entrypoint.sh). Single container by design: Ollama has to be
# reachable at low latency from app/llm/llama_client.py, and running
# them as one Railway service avoids inter-service networking config
# for what is, on this model size, a genuinely single-workload deploy.
#
# NOT build-tested locally — Docker isn't installed in the dev
# environment this was written in. Railway (or `docker build .`
# wherever Docker is available) will be the first real build; see the
# deployment guide for what to check if it fails.

FROM python:3.10-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL https://ollama.com/install.sh | sh

WORKDIR /app

COPY requirements-prod.txt .
RUN pip install --no-cache-dir -r requirements-prod.txt

# Bake the model into the image so a fresh container starts fast and
# doesn't depend on network access at runtime — entrypoint.sh also
# checks for it defensively in case a platform strips this layer.
RUN (ollama serve &) && \
    sleep 5 && \
    ollama pull llama3.2:3b && \
    (pkill ollama || true)

COPY app/ ./app/

# Only the small runtime-required artifacts — NOT data/processed/manara_dataset.csv
# (937MB, a data-pipeline intermediate never read at request time; see
# CLAUDE.md's data pipeline section).
COPY data/processed/search_corpus.csv ./data/processed/search_corpus.csv
COPY data/embeddings/faiss_index.bin ./data/embeddings/faiss_index.bin
COPY data/embeddings/bm25_index.pkl ./data/embeddings/bm25_index.pkl

COPY entrypoint.sh .
RUN chmod +x entrypoint.sh

ENV OLLAMA_HOST=127.0.0.1:11434
EXPOSE 8000

ENTRYPOINT ["./entrypoint.sh"]
