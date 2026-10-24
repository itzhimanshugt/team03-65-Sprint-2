#!/bin/sh
# Build the vector index from the cached embeddings (no API calls), then start API + UI.
set -e
[ -d data/chroma ] || python -m scripts.build_index || echo "index check failed (see report above); starting anyway"
uvicorn app.api.main:app --host 127.0.0.1 --port 8000 &
exec streamlit run app/ui/streamlit_app.py --server.port "${PORT:-7860}" --server.address 0.0.0.0 --server.headless true
