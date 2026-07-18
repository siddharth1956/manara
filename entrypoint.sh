#!/bin/sh
set -e

# Explicit stage logging throughout — a first real deploy attempt
# produced a container that failed the health check with zero log
# output, giving no signal on which stage it never got past. Never
# want that again: every stage announces itself before it runs.
echo "[entrypoint] starting ollama serve"
ollama serve &

echo "[entrypoint] waiting for ollama to be reachable"
ready=0
for i in $(seq 1 30); do
    if curl -sf http://127.0.0.1:11434/ > /dev/null 2>&1; then
        ready=1
        break
    fi
    sleep 1
done
if [ "$ready" = "1" ]; then
    echo "[entrypoint] ollama reachable after ${i}s"
else
    echo "[entrypoint] WARNING: ollama not reachable after 30s, proceeding anyway"
fi

echo "[entrypoint] checking for llama3.2:3b"
if ollama list | grep -q "llama3.2:3b"; then
    echo "[entrypoint] model already present"
else
    echo "[entrypoint] model missing, pulling now (this will be slow)"
    ollama pull llama3.2:3b
fi

echo "[entrypoint] starting uvicorn on port ${PORT:-8000}"
exec uvicorn app.main:app --host 0.0.0.0 --port "${PORT:-8000}"
