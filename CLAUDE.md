# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project overview

MANARA is a bilingual (Arabic/English) Retrieval-Augmented Generation assistant for UAE geospatial data — Sentinel-2 satellite imagery (via Copernicus), OpenStreetMap road networks, and derived analytics. It has two independently-run halves:

- **`app/`** — FastAPI backend exposing a single RAG query endpoint.
- **`frontend/`** — Streamlit multi-page dashboard that calls the backend over HTTP.

## Running the app

Backend (from repo root, so `app.*` imports resolve):
```
uvicorn app.main:app --reload
```
The backend requires the local FAISS index and embeddings to already exist (see Data pipeline below) and expects [Ollama](https://ollama.com) running locally with `llama3.2:3b` pulled — `app/llm/llama_client.py` calls `ollama.chat()` directly.

Frontend (must run from inside `frontend/`, since its modules use bare imports like `from views.dashboard import ...` rather than package-relative ones):
```
cd frontend && streamlit run app.py
```
The frontend talks to the backend at a hardcoded `http://127.0.0.1:8000/query` (see `frontend/views/ai_chat.py`), so the backend must be running first.

Copernicus credentials for `app/services/copernicus_service.py` and the `scripts/download_*` scripts are read from `.env` (`COPERNICUS_USERNAME` / `COPERNICUS_PASSWORD`, loaded via `python-dotenv`).

## Data pipeline

The retriever depends on prebuilt artifacts under `data/`. The `scripts/` directory rebuilds them in this order:

1. `download_osm.py`, `download_sentinel.py`, `download_data.py` — pull raw OSM/Copernicus data into `data/raw/`.
2. `process_osm.py`, `process_stac_metadata.py`, `extract_metadata.py` — normalize raw data into `data/processed/*.csv`.
3. `merge_datasets.py`, `prepare_dataset.py` — combine processed sources into `data/processed/manara_dataset.csv`.
4. `build_search_corpus.py` — flattens metadata into `data/processed/search_corpus.csv` (one text document per row; this is what gets embedded and returned as a retrieval "source").
5. `build_embeddings.py` — encodes the corpus with `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2` into `data/embeddings/embeddings.npy`.
6. `build_faiss.py` — builds `data/embeddings/faiss_index.bin` from those embeddings.

Run any script as a module from repo root (e.g. `python -m scripts.build_faiss`) so `app.core.config` imports resolve.

## Backend request flow

`app/main.py` wires the full pipeline for `POST /query`:

1. **Language detection** — `app/services/language_detector.py` regex-matches Arabic Unicode ranges.
2. **NLU** — English queries go through `app/services/nlu.py` (`IntentClassifier`: keyword-weighted intent scoring + regex entity extraction for location/satellite/metric/date). Arabic queries go through `app/services/arabic/pipeline.py` (`ArabicPipeline`: normalizer → tokenizer → NER → intent classifier, each a separate module under `app/services/arabic/`). These two pipelines are independent implementations, not shared code — intent label sets and entity shapes differ between them.
3. **Retrieval** — `app/services/retriever.py` embeds the query with the same sentence-transformers model used at index time, does a FAISS top-`k*3` search, filters by intent (`road_search`/`satellite_search` restrict to matching `type` rows), applies entity-match score boosts, then re-ranks and truncates to `k`. Location entities are normalized via `app/services/location_mapper.py` (Arabic place names → canonical English).
4. **Generation** — `app/services/generator.py` builds a context-stuffed prompt and delegates to `app/llm/router.py` (`LLMRouter`), which sends Arabic queries to `JaisClient` (`app/llm/jais_client.py` — currently a stub that always reports unavailable and falls through) and everything else to `LlamaClient` (Ollama `llama3.2:3b`). Both clients implement `app/llm/base.py`'s `BaseLLM.generate()`.

The FAISS index, embedding model, and search corpus are loaded once at import time in `retriever.py` (module-level globals), not per-request.

## Known dead/legacy code

Not imported by the running app — don't assume these are part of the live request path:
- `app/services/model_router.py`, `app/services/jais_generator.py` (empty), `app/services/arabic_nlu.py` — superseded by `app/llm/router.py` and `app/services/arabic/`, respectively.
- `frontend/utils/api.py` is empty; the frontend calls the backend directly with `requests` from within each view (see `frontend/views/ai_chat.py`).

## Tests

There is no pytest suite/config. Files named `test_*.py` (under `app/services/`, `app/services/arabic/`, and `scripts/`) are standalone scripts that print output for manual inspection rather than asserting — some (e.g. `scripts/test_retriever.py`) block on `input()`. Run them individually as modules from repo root, e.g.:
```
python -m app.services.test_nlu
python -m app.services.arabic.test_intent
```

## Repo layout note

`manara/` at the repo root is a stale nested git checkout (its own `.git`, several commits behind — missing `app/services/arabic/`, `location_mapper.py`, etc.). Do not edit files under `manara/`; make changes in the top-level `app/`, `frontend/`, and `scripts/` instead.
