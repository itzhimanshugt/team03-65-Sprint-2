#!/bin/sh
# Build the vector index from the cached embeddings (no API calls), then serve the API + web UI.
set -e
[ -d data/chroma ] || python -m scripts.build_index || echo "index check failed (see report above); starting anyway"
exec uvicorn app.api.main:app --host 0.0.0.0 --port "${PORT:-7860}"
