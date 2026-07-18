#!/bin/sh
set -e

ollama serve &

# Wait for the Ollama daemon to actually be reachable before the app
# starts — llama_client.py has no retry/backoff of its own, so a query
# arriving before this is ready would just fail.
for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:11434/ > /dev/null 2>&1; then
        break
    fi
    sleep 1
done

# Defensive re-check: the model should already be baked into the image
# (see Dockerfile), so this is normally a fast no-op verification, not
# a real 2GB download — only pulls for real if that layer was lost.
ollama list | grep -q "llama3.2:3b" || ollama pull llama3.2:3b

# Respect the platform-assigned port (Railway/Render inject $PORT);
# default to 8000 for a local `docker run`.
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
