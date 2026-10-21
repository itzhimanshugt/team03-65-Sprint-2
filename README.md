# Financial Advisory Compliance RAG Assistant

A Retrieval-Augmented Generation (RAG) application for helping financial
advisors verify answers against approved market research, fund
factsheets, and regulatory disclosures.

> **Important:** This application is designed to retrieve and explain
> information from approved documents. It is not a substitute for
> professional compliance review or independent financial/legal advice.

## Problem Statement

A financial advisory firm maintains market research, fund factsheets,
and regulatory disclosures, but advisors risk giving non-compliant
guidance because they cannot verify answers against the latest approved
documents.

The application creates a searchable knowledge base from approved
documents and uses retrieval before answer generation.

## Core Workflow

``` text
Documents
  ↓
Load → Extract → Clean → Chunk + Metadata
  ↓
Embeddings → Vector Database
  ↓
User Question → Query Embedding → Similarity Search
  ↓
Filter / Re-rank → Context Assembly
  ↓
LLM → Grounded Answer + Citations
```

## Core Features

-   Document intake and text extraction
-   Text cleaning and chunking
-   Source/position metadata
-   Embedding generation
-   Vector database storage
-   Semantic top-K retrieval
-   Metadata filtering
-   Optional hybrid search and re-ranking
-   Grounded generation
-   Source citations
-   Hallucination/refusal guardrails
-   Conversational follow-ups
-   Backend RAG API
-   Document upload and indexing
-   Chat UI
-   Streaming responses
-   Logging and usage monitoring
-   Retrieval and answer-quality evaluation

## Target Users

**Financial Advisors:** Verify information from approved documents
before communicating guidance.

**Knowledge/Compliance Teams:** Maintain the approved document knowledge
base.

## Example User Flow

1.  Upload an approved document.
2.  Extract and clean its text.
3.  Split it into chunks.
4.  Attach source metadata.
5.  Generate embeddings.
6.  Index embeddings in the vector database.
7.  Ask a question.
8.  Retrieve relevant chunks.
9.  Filter/re-rank candidates if required.
10. Assemble context.
11. Generate a grounded answer.
12. Display citations.
13. Refuse or ask for clarification when evidence is insufficient.

## Recommended Project Structure

``` text
financial-compliance-rag/
├── app/
│   ├── api/
│   ├── ui/
│   └── main.py
├── ingestion/
│   ├── loaders.py
│   ├── cleaner.py
│   ├── chunker.py
│   └── metadata.py
├── embeddings/
│   ├── embedder.py
│   └── batch.py
├── retrieval/
│   ├── vector_store.py
│   ├── search.py
│   ├── filters.py
│   └── reranker.py
├── rag/
│   ├── pipeline.py
│   ├── prompts.py
│   ├── citations.py
│   └── guardrails.py
├── evaluation/
├── prompts/          # reusable prompt templates
├── outputs/          # eval reports, experiment results
├── tests/
├── data/
│   ├── raw/
│   └── processed/
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## Environment Setup

``` bash
python -m venv .venv
```

macOS/Linux:

``` bash
source .venv/bin/activate
```

Windows:

``` bash
.venv\Scripts\activate
```

Install dependencies:

``` bash
pip install -r requirements-dev.txt   # app + test/lint tools
```

## Environment Variables

Use a local `.env` file for secrets:

``` env
LLM_API_KEY=your_api_key_here
VECTOR_DB_URL=your_vector_database_url
VECTOR_DB_API_KEY=your_vector_database_key
```

Never commit `.env`. Use `.env.example` to document variable names
without real credentials.

## Retrieval

The retrieval flow is:

``` text
Question
  ↓
Query Embedding
  ↓
Vector Similarity Search
  ↓
Top-K Candidates
  ↓
Metadata Filtering
  ↓
Optional Re-ranking
  ↓
Relevant Context
```

Retrieved chunks must retain enough metadata to generate citations.

## Vector Store

ChromaDB, persistent at `CHROMA_PATH` (default `data/chroma`, git-ignored), one collection:

| Setting | Value |
|---|---|
| Collection | `verifai_chunks` |
| Distance | cosine (`hnsw:space = cosine`; Chroma returns distance = 1 − cosine similarity) |
| Vector size | `EMBEDDING_DIMENSIONS` (768), checked when the collection opens |
| Embedding function | none: vectors always come from `embed_texts` (L2-normalised) |
| `id` | `chunk_id` (`{doc_id}-{chunk_index:04d}`) |
| `document` | chunk text |
| `metadata` | `doc_id`, `chunk_index`, `source_name`, `title`, `doc_type`, `issuer`, `family`, `published_date`, `version`, `is_latest`, `page`, `token_count`, `checksum` |

Metadata keeps everything needed to **cite** (source, page, version) and to **filter** (type, issuer, date, latest only), so retrieval never has to reopen the source files.

## Grounded Generation

The generation layer should: - Answer from retrieved evidence. - Avoid
unsupported claims. - Include source references. - Respect context
limits. - Refuse or request clarification when evidence is insufficient.

**Design principle:**

> No reliable retrieved evidence → no invented answer.

## Evaluation

Evaluate retrieval using representative questions and a labelled set of
expected relevant chunks.

Measure: - Recall - Precision - Retrieval relevance

Evaluate generated answers for: - Correctness - Grounding - Citation
quality - Refusal behavior

## Security

``` text
.env         → local secrets
.env.example → safe template
.gitignore   → excludes .env
```

Never commit API keys or expose them in logs.

## Testing

``` bash
pytest
```

Tests should cover document loading, cleaning, chunking, metadata,
embeddings, retrieval, RAG generation, citations, guardrails, and API
endpoints as those components are implemented.

## GitHub Workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for branch naming, PR rules and the protections on `main`. Track work on the [Sprint 2 board](https://github.com/users/itzhimanshugt/projects/2).

``` text
Issue → Feature Branch → Implementation → Testing → Pull Request → Review → Merge
```

Example:

``` bash
git checkout -b feature/document-ingestion
git add .
git commit -m "feat: implement document ingestion"
git push -u origin feature/document-ingestion
```

## Sprint 2 Status

**Status: In Development**

Current focus: - Problem understanding - PRD - Mock UX -
Repository/workflow setup - RAG architecture planning

Upcoming: - Document ingestion - Chunking - Embeddings - Vector
database - Retrieval - Grounded generation - API/UI integration -
Evaluation - Deployment

## Limitations

The quality of the system depends on the completeness and quality of the
approved source documents. Poor documents, weak chunking, embedding
limitations, or missing evidence can reduce retrieval quality. The
system cannot independently guarantee legal or regulatory compliance.

## Team

**Squad:** 65\
**Team:** 03\
**Project:** Financial Advisory Compliance RAG Assistant

Team contributions should be tracked through GitHub issues, branches,
commits, and pull requests.

## License

This project is developed as part of the Kalvium Simulated Work Sprint
2.
