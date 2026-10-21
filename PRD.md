# PRD — VerifAI: Financial Advisory Compliance RAG Assistant

| Field | Value |
|---|---|
| Sprint | Sprint 2 — AI Application Development with RAG |
| Squad / Team | 65 / 03 |
| Version | v2.0 (revised after mentor review) |
| Status | Resubmitted for approval |
| Mock UX | [Figma — team03-sprint2-verifai](https://www.figma.com/design/S3lVpz5bkKkSrrjuv9URYr/team03-sprint2-verifai-?node-id=0-1) · annotation spec: [docs/MOCK_UX_ANNOTATIONS.md](docs/MOCK_UX_ANNOTATIONS.md) |

### Revision log (response to review feedback)

| # | Feedback | Where it is addressed |
|---|---|---|
| 1 | Quantify the business problem | §1.2 Problem sizing |
| 1 | Strictly formatted KPIs (metric + measurement + target + timeline) | §4 KPIs |
| 2 | Exact dataset parameters | §6 Dataset specification |
| 2 | Rewrite user journey as formatted user stories | §7 User stories |
| 3 | Add impact to risks | §13 Risk register |
| 3 | Annotations, empty states, flow diagram for Figma | §8 Flow diagram, §9 Empty states, [docs/MOCK_UX_ANNOTATIONS.md](docs/MOCK_UX_ANNOTATIONS.md) |
| — | Align with the Sprint 2 concept roadmap (C1–C40) | §6.2 (OpenAI-compatible API, multi-format intake, hybrid search, caching, Streamlit), §16 Concept map |

---

## 1. Problem

### 1.1 Problem statement

A financial advisory firm maintains market research, fund factsheets, and regulatory disclosures, but advisors risk giving non-compliant guidance because they cannot quickly verify answers against the latest **approved** documents. Today, verification means manually searching a shared drive of long PDFs, so advisors either spend a long time looking or answer from memory — and memory is often based on an older factsheet.

### 1.2 Problem sizing

We size the problem for a representative mid-sized advisory firm. Figures marked *Assumption* are working estimates; they will be validated through a timed manual lookup exercise (10 questions) and short user interviews before final delivery, and the PRD will be updated with measured values.

| Parameter | Baseline value | Basis |
|---|---|---|
| Advisors in firm | 50 | Assumption — mid-sized firm |
| Client questions per advisor per day that need a document check | 8 | Assumption |
| Time to find and verify one answer manually | 12 min (median) | Assumption — to be measured in the timed lookup exercise |
| Approved documents in the shared drive | ~500 PDFs, refreshed monthly (factsheets) | Assumption |
| Share of manual answers that cite an outdated or unapproved document | 10% | Assumption — to be measured in an audit of 50 sample answers |

**Derived impact (baseline):**

- **Time lost:** 50 advisors × 8 checks × 12 min = **80 advisor-hours per day ≈ 1,760 hours per month** (22 working days).
- **Compliance exposure:** 50 × 8 × 22 × 10% ≈ **880 client answers per month** potentially based on outdated or unapproved material. Each one is a possible mis-selling complaint or regulatory finding.
- **Opportunity:** cutting verification time from 12 min to ≤ 1 min frees **~1,600 advisor-hours per month**, and grounding every answer in a cited, approved source targets ≤ 1% outdated-source answers.

### 1.3 Product vision

VerifAI is a Retrieval-Augmented Generation (RAG) assistant that lets advisors ask questions about approved documents and get grounded answers with page-level citations in under 10 seconds. When the approved documents do not contain enough evidence, VerifAI says so instead of inventing an answer.

---

## 2. Target users

| Persona | Role | Core need | Frequency |
|---|---|---|---|
| **Advisor** (primary) | Client-facing financial advisor | Verify a fact (e.g. a fund's expense ratio, exit load, risk category) before telling a client, and show where it came from | 5–15 questions per day |
| **Compliance officer** (secondary) | Maintains the approved document set | Upload, replace and retire documents; check that the assistant only answers from approved sources; review refusals | Weekly / on each monthly factsheet release |

---

## 3. Goals and non-goals

### 3.1 Goals

1. Ingest approved documents (upload → extract → clean → chunk with metadata).
2. Embed chunks and store them in a vector database.
3. Retrieve relevant chunks with top-K semantic search, metadata filters and optional re-ranking.
4. Generate grounded answers with page-level source citations.
5. Refuse or ask for clarification when evidence is insufficient.
6. Support conversational follow-ups.
7. Provide a backend RAG API and a chat UI with streaming.
8. Evaluate retrieval and answer quality against a labelled test set.
9. Deploy and document a reproducible application.

### 3.2 Non-goals

- Autonomous or personalised financial advice (e.g. "should my client buy fund X").
- Trade or investment execution.
- Replacing compliance professionals or guaranteeing legal/regulatory compliance.
- Training a foundation model from scratch.
- Answering from information outside the approved document set (no web search).
- OCR of scanned/image-only PDFs (Sprint 2 supports text-based PDF, HTML, TXT and Markdown).

---

## 4. KPIs

Every KPI below is measured on the evaluation set defined in §6.4 unless stated otherwise. Timelines are dates in the final sprint week (Day 1 = Mon 19 Oct 2026, Day 7 = Sun 25 Oct 2026).

| ID | KPI | Metric (definition) | Measurement method | Target | Timeline |
|---|---|---|---|---|---|
| K1 | Retrieval recall | Recall@5 = share of answerable questions where ≥ 1 labelled relevant chunk is in the top 5 retrieved | Automated script over the 30 answerable eval questions | **≥ 0.85** | 22 Oct 2026 (Day 4) |
| K2 | Retrieval ranking quality | MRR@5 (mean reciprocal rank of first relevant chunk) | Same automated script as K1 | **≥ 0.70** | 22 Oct 2026 (Day 4) |
| K3 | Citation accuracy | % of citations whose cited chunk actually supports the sentence it is attached to | Manual review of all 30 answerable answers against their cited chunks (no LLM judge, to save free-tier quota) | **≥ 90%** | 23 Oct 2026 (Day 5) |
| K4 | Hallucination rate | % of answers containing ≥ 1 claim not supported by retrieved context | Same review as K3 | **≤ 5%** | 23 Oct 2026 (Day 5) |
| K5 | Correct refusal rate | % of the 10 unanswerable/out-of-scope eval questions where the system refuses or asks to clarify | Automated: response flagged `refused=true` by the API | **≥ 90%** | 23 Oct 2026 (Day 5) |
| K6 | False refusal rate | % of the 30 answerable eval questions that are wrongly refused | Automated: `refused=true` on an answerable question | **≤ 10%** | 23 Oct 2026 (Day 5) |
| K7 | Time to verified answer | Median time from typing a question to reading a cited answer | Usability test, 3 participants × 5 tasks, stopwatch; compared with the 12-min manual baseline | **≤ 60 s** (≥ 90% faster than baseline) | 25 Oct 2026 (Day 7) |
| K8 | Response latency | p95 end-to-end API latency; p95 time to first streamed token | API request logs over the full 40-question eval run | **p95 ≤ 8 s; first token p95 ≤ 2 s** | 24 Oct 2026 (Day 6) |
| K9 | Ingestion completeness | % of corpus documents indexed with all required metadata fields (§6.3) populated | Automated validation script over the vector store | **100%** of corpus docs | 20 Oct 2026 (Day 2) |
| K10 | Ingestion speed | Time to index one 50-page text PDF (upload → searchable) | Timed on 5 sample documents, median | **≤ 60 s** | 21 Oct 2026 (Day 3) |
| K11 | Usability | System Usability Scale (SUS) score | SUS questionnaire after the K7 usability test | **≥ 70** | 25 Oct 2026 (Day 7) |

---

## 5. Scope and milestones

One pull request per concept (§16). Several concepts are delivered per day.

| Day | Date | Milestone | Concepts | KPIs due |
|---|---|---|---|---|
| 1 | Mon 19 Oct | Workspace, GitHub workflow, PRD v2, LLM client, prompts, tokens, JSON output | C1–C9 | — |
| 2 | Tue 20 Oct | Multi-format loading, cleaning, chunking, metadata, corpus validation | C10–C15 | K9 |
| 3 | Wed 21 Oct | Embeddings via API, similarity, batching, sanity tests, vector DB + indexing | C16–C22 | K10 |
| 4 | Thu 22 Oct | Top-K search, filters + hybrid search, tuning, re-ranking, retrieval eval | C23–C27 | K1, K2 |
| 5 | Fri 23 Oct | RAG pipeline, context injection, grounded answers, citations, guardrails, follow-ups, eval | C28–C34 | K3–K6 |
| 6 | Sat 24 Oct | FastAPI, upload endpoint, Streamlit UI, streaming, caching/logging | C35–C39 | K8 |
| 7 | Sun 25 Oct | Deployment, documentation, usability test, final KPI report | C40 | K7, K11 |

---

## 6. Dataset specification

### 6.1 Corpus

The firm's "approved document set" is simulated using publicly available Indian mutual-fund and regulatory documents. Each document is tagged as approved at ingestion by the compliance persona.

| Category | Source (public) | # Docs | Format | Pages per doc | Date range |
|---|---|---|---|---|---|
| Fund factsheets | Monthly factsheets published by 5 AMFI-registered AMCs on their websites | 15 | Text-based PDF | 2–60 | Jan–Sep 2026 |
| Scheme disclosures | Scheme Information Documents (SID) and Key Information Memorandums (KIM) from the same AMCs | 10 | Text-based PDF | 20–150 | Latest version available |
| Regulatory circulars | SEBI circulars on mutual funds and investment advisers (sebi.gov.in) | 15 | HTML or PDF | 3–40 | 2023–2026 |
| Market research | AMC market outlook / commentary reports | 7 | Text-based PDF | 5–30 | Jan–Sep 2026 |
| Internal notes | Firm FAQ / product notes written for the simulation | 3 | Markdown / TXT | 1–5 | Oct 2026 |
| **Total** | | **50** | **4 formats** | **~1,500 pages (est.)** | |

**Inclusion rules:** English only; PDF with selectable text, HTML, TXT or Markdown; ≤ 25 MB per file; publicly downloadable or written for the simulation.
**Exclusion rules:** scanned/image-only PDFs, password-protected files, spreadsheets, non-English documents.
**Versioning test:** at least 3 fund factsheets are included in two monthly versions (e.g. August and September) to test that answers cite the latest approved version.

### 6.2 Processing parameters

| Parameter | Value | Rationale |
|---|---|---|
| Loading / extraction | PDF: `pypdf` (per page, page number retained); HTML: `BeautifulSoup` (main text, section headings as positions); TXT/MD: read as UTF-8, headings as positions | One common `Document(pages, metadata)` representation for all four formats |
| Cleaning | Remove repeated headers/footers, page numbers, disclaimer boilerplate repeated on > 50% of pages; normalise whitespace and Unicode (NFKC) | Reduces noise in embeddings |
| Chunking strategy | Recursive split on headings → paragraphs → sentences | Keeps related facts together |
| Chunk size / overlap | **400 tokens / 60 tokens (15%)**, counted with `tiktoken` (`cl100k_base`) | Focused chunks; 5 chunks + prompt fit the 3,000-token context budget |
| Tables | Flattened row-wise to "column: value" text inside the chunk | Factsheet facts (expense ratio, AUM, exit load) live in tables |
| API access | OpenAI Python SDK against an **OpenAI-compatible endpoint**; `base_url`, key and model names set in `.env` | One client for chat and embeddings; provider can be switched without code changes |
| Default provider | Google Gemini via its OpenAI-compatible endpoint, **free tier**. Limits vary by model and tier and are not guaranteed; observed for this project on 19 Oct 2026: 10 requests/minute and 20/day on `gemini-2.5-flash` and `gemini-2.5-flash-lite` (check AI Studio → Rate limits for the current values per model). Alternative: OpenAI | Zero cost; quotas shape the model choice, retries and eval size below |
| Embedding model | `gemini-embedding-001` (default) or OpenAI `text-embedding-3-small` (1,536 dims); the dimension is validated when the collection is created | Hosted API, as required by the sprint roadmap |
| Batch embedding | 64 chunks per request, exponential backoff on 429/5xx (max 5 retries), already-embedded chunks skipped by `chunk_id` | Handles rate limits and keeps re-runs cheap |
| Chat model | `gemini-3.1-flash-lite` (default), falling back to `gemini-2.5-flash-lite` → `gemini-3-flash-preview` → `gemini-2.5-flash` when a model's daily quota is used up; OpenAI `gpt-4o-mini` as alternative. Temperature 0.1, max 600 output tokens, `reasoning_effort=none`: turns thinking off on 2.5 models; Gemini 3 models accept it (verified live) but may still use minimal thinking, so their output budget keeps headroom | Low temperature for consistent facts; fallback multiplies the free daily quota; no hidden thinking tokens eating `max_tokens` |
| Rate limits | Per-minute 429: wait the delay stated in Google's error message ("retry in Ns") and retry, max 3 times. Daily-quota 429 (delay over 90 s) or no stated delay: switch to the next fallback model; with none left, fail with the error | Keeps scripts running inside free-tier limits |
| Output format | JSON `{answer, citations: [{n, chunk_id, source, page}], refused}` validated with Pydantic; one retry on invalid JSON | Reliable parsing for citation chips |
| Vector database | ChromaDB (persistent, cosine distance) | Simple local setup, supports metadata filters |
| Expected index size | ~4,000–5,000 chunks | ~1,500 pages × ~3 chunks/page |
| Retrieval | Hybrid: vector top-20 + BM25 keyword top-20, merged with reciprocal rank fusion → re-rank → **top-5** to the LLM | Keyword search catches exact terms such as circular numbers and fund names |
| Insufficient-evidence threshold | Refuse if best vector similarity < **0.45** (initial value, tuned against K5/K6) | Drives safe refusal |
| Context budget | ≤ 3,000 tokens of retrieved context per answer | Keeps latency and cost bounded |
| Conversation memory | Last 4 turns, trimmed to a 1,500-token budget, condensed into a standalone query before retrieval | Supports follow-ups without drifting |
| Caching | Answers cached by hash of (normalised question + filters + index version) for 24 h | Repeated questions cost nothing and return instantly |
| Chat UI | Streamlit | Python-only, fastest path to a working chat interface |

### 6.3 Chunk metadata schema

| Field | Type | Example | Required |
|---|---|---|---|
| `doc_id` | string (UUID) | `3f2a…` | Yes |
| `source_name` | string | `ABC Flexi Cap Fund Factsheet – Sep 2026.pdf` | Yes |
| `doc_type` | enum: `factsheet`, `sid_kim`, `circular`, `research` | `factsheet` | Yes |
| `issuer` | string | `ABC Mutual Fund` / `SEBI` | Yes |
| `published_date` | date | `2026-09-30` | Yes |
| `version` | integer | `2` | Yes |
| `is_latest` | boolean | `true` | Yes |
| `approved_by` / `approved_at` | string / datetime | `compliance@firm` / `2026-10-02T10:00Z` | Yes |
| `page` | integer (PDF page, or section index for HTML/TXT/MD) | `4` | Yes |
| `chunk_id` / `chunk_index` | string / integer | `3f2a…-0012` / `12` | Yes |
| `token_count` | integer | `388` | Yes |
| `checksum` | string (SHA-256 of file) | `9b1c…` | Yes (duplicate detection) |

### 6.4 Evaluation set

| Slice | # Questions | Example | Label |
|---|---|---|---|
| Single-document factual | 25 | "What is the exit load of ABC Flexi Cap Fund?" | Relevant `chunk_id`s + page + reference answer |
| Multi-document / comparison | 5 | "Compare the expense ratios of the two large-cap funds." | Relevant `chunk_id`s from each doc + reference answer |
| Unanswerable (not in corpus) | 6 | "What is the fund manager's personal portfolio?" | Expected: refusal |
| Out-of-scope / advice-seeking | 4 | "Should my client switch all savings into this fund?" | Expected: refusal with non-advice notice |
| **Total** | **40** | | |

Sized to fit the free-tier quota: one full run is 40 generation calls, at most 80 in the worst case (one corrective retry per answer for invalid JSON). Runs are spread across the fallback models and started early in the day (quotas reset at midnight Pacific). Questions are written from the corpus before retrieval tuning starts. Retrieval metrics (K1, K2) need only embedding calls. Stored as `evaluation/eval_set.jsonl`.

---

## 7. User stories

Priority uses MoSCoW (M = Must, S = Should, C = Could). Acceptance criteria use Given / When / Then.

| ID | User story | Acceptance criteria | Priority |
|---|---|---|---|
| US-01 | **As an** advisor, **I want** to ask a question in plain English, **so that** I can verify a fact before I tell a client. | **Given** the corpus is indexed, **when** I submit a question, **then** I receive an answer within 8 s (p95) that is built only from retrieved approved chunks. | M |
| US-02 | **As an** advisor, **I want** each claim in the answer to show a citation (document, page), **so that** I can prove where the information came from. | **Given** an answer, **when** it is displayed, **then** every factual sentence has ≥ 1 citation chip showing `source_name` and `page`. | M |
| US-03 | **As an** advisor, **I want** to open a citation and see the exact source passage, **so that** I can check the context myself. | **Given** a citation chip, **when** I click it, **then** a source panel opens showing the chunk text highlighted, the document name, page, published date and version. | M |
| US-04 | **As an** advisor, **I want** VerifAI to tell me when it cannot find enough evidence, **so that** I never pass on an invented answer. | **Given** best retrieval score < threshold, **when** I ask, **then** the UI shows the "Not enough evidence" state with suggestions to rephrase or filter, and no answer text is generated. | M |
| US-05 | **As an** advisor, **I want** questions asking for personal investment advice to be declined, **so that** I stay within compliance boundaries. | **Given** an advice-seeking question, **when** I submit it, **then** the system responds with a non-advice notice and offers the related factual information if available. | M |
| US-06 | **As an** advisor, **I want** to ask follow-up questions, **so that** I do not need to repeat context. | **Given** a previous answer about fund X, **when** I ask "and its exit load?", **then** retrieval targets fund X and the answer is cited. | S |
| US-07 | **As an** advisor, **I want** to filter by document type, issuer or date, **so that** I get answers from the right source. | **Given** filters are set, **when** I ask, **then** only chunks matching the filters are retrieved, and active filters are visible above the chat. | S |
| US-08 | **As an** advisor, **I want** to see the answer stream in, **so that** I am not left waiting on a blank screen. | **Given** a question, **when** generation starts, **then** the first token appears within 2 s (p95). | S |
| US-09 | **As a** compliance officer, **I want** to upload an approved document (PDF, HTML, TXT or MD) with its type, issuer and date, **so that** advisors can query it. | **Given** a valid file ≤ 25 MB, **when** I upload it, **then** it is indexed within 60 s (50 pages) and shows status "Indexed" with chunk count. | M |
| US-10 | **As a** compliance officer, **I want** to see why an upload failed, **so that** I can fix it. | **Given** a scanned, encrypted, oversized or unsupported file, **when** I upload it, **then** I see status "Failed" with a specific reason and nothing is added to the index. | M |
| US-11 | **As a** compliance officer, **I want** duplicates detected and new versions to replace old ones, **so that** advisors only get the latest approved information. | **Given** a file with an existing checksum, **then** the upload is rejected as duplicate; **given** a new version of an existing document, **then** the old version is marked `is_latest=false` and excluded from retrieval by default. | M |
| US-12 | **As a** compliance officer, **I want** a log of questions, cited sources and refusals, **so that** I can review how the assistant is being used. | **Given** questions were asked, **when** I open the activity log, **then** I see timestamp, question, cited `doc_id`s, refused flag and latency — with no API keys or secrets logged. | C |

---

## 8. Flow diagram

End-to-end user flow across the Mock UX screens (screen IDs match [docs/MOCK_UX_ANNOTATIONS.md](docs/MOCK_UX_ANNOTATIONS.md)).

```mermaid
flowchart TD
    A([Open VerifAI]) --> B{Role}
    B -->|Advisor| C[S1 Chat home]
    B -->|Compliance| K[S4 Knowledge base]

    C -->|No documents indexed| E1[[Empty state: Knowledge base is empty]]
    C --> D[Type question + optional filters]
    D --> R{Retrieval score >= threshold?}
    R -->|No| E2[[S2c Not enough evidence]]
    E2 -->|Rephrase / change filters| D
    R -->|Advice-seeking question| E3[[S2d Non-advice notice]]
    R -->|Yes| G[S2 Streaming answer with citation chips]
    G -->|Click citation| H[S3 Source panel: highlighted passage]
    H --> G
    G -->|Follow-up question| D
    G -->|LLM / network error| E4[[S2e Error state + Retry]]
    E4 --> D

    K -->|No documents yet| E5[[Empty state: Upload your first approved document]]
    K --> U[S5 Upload document + metadata]
    U --> V{Valid file?}
    V -->|No| E6[[Failed: reason shown]]
    E6 --> U
    V -->|Duplicate| E7[[Duplicate warning]]
    V -->|New version| W[Mark old version not latest]
    V -->|Yes| X[Indexing: extract → chunk → embed]
    W --> X
    X --> Y[Status: Indexed + chunk count]
    Y --> K
    K --> L[S6 Activity log]
```

### System architecture

```mermaid
flowchart LR
    subgraph Ingestion
      P[Upload: PDF / HTML / TXT / MD] --> EX[Load + extract] --> CL[Clean] --> CH[Chunk 400/60 + metadata] --> EM[Batch embed via OpenAI-compatible API]
    end
    EM --> VDB[(ChromaDB)]
    Q[Question + chat history] --> RW[Condense to standalone query] --> QE[Embed query] --> SS[Vector top-20 + BM25 top-20 + metadata filter → RRF]
    VDB --> SS
    SS --> RR[Re-rank → top-5] --> TH{Score ≥ threshold?}
    TH -->|No| RF[Refusal / clarification]
    TH -->|Yes| CA[Assemble context ≤ 3k tokens] --> LLM[LLM with grounded prompt] --> ANS[Answer + citations]
    ANS --> UI[Chat UI / API]
    RF --> UI
```

---

## 9. Empty, error and edge states

| State | Screen | Trigger | Message shown | Primary action |
|---|---|---|---|---|
| No conversation yet | S1 Chat | First visit / new chat | "Ask anything about your approved documents. Every answer comes with sources." + 3 example questions | Click an example question |
| Knowledge base empty (advisor view) | S1 Chat | 0 indexed documents | "No approved documents are available yet. Ask your compliance team to upload them." | — (input disabled) |
| Knowledge base empty (compliance view) | S4 Knowledge base | 0 documents | "Upload your first approved document to get started." | Upload document |
| Not enough evidence | S2 Answer | Score below threshold | "I couldn't find this in the approved documents, so I won't guess." + suggestions | Rephrase / clear filters |
| Advice request | S2 Answer | Advice-seeking question detected | "VerifAI provides facts from approved documents, not investment advice." | Show related facts |
| No matches for filters | S1 Chat | Filters exclude all documents | "No documents match these filters." | Clear filters |
| Upload failed | S5 Upload | Scanned / encrypted / > 25 MB / not PDF | Specific reason, e.g. "This PDF has no selectable text (scanned)." | Choose another file |
| Duplicate upload | S5 Upload | Checksum match | "This document is already in the knowledge base." | View existing document |
| Indexing in progress | S4 / S5 | Upload accepted | Progress: Extracting → Chunking → Embedding | — |
| Service error | S2 Answer | LLM / vector DB timeout | "Something went wrong while generating the answer." | Retry |
| Source unavailable | S3 Source panel | Document retired after answer | "This source has been replaced by a newer version." | Open latest version |
| No activity yet | S6 Activity log | 0 logged questions | "No questions have been asked yet." | — |

---

## 10. Functional requirements

### 10.1 Ingestion
- FR-1 Accept PDF (text-based), HTML, TXT and Markdown uploads ≤ 25 MB with metadata (`doc_type`, `issuer`, `published_date`).
- FR-2 Extract text per page and retain page numbers.
- FR-3 Clean boilerplate, whitespace and encoding as per §6.2.
- FR-4 Chunk using the strategy and sizes in §6.2.
- FR-5 Attach all metadata fields in §6.3 to every chunk.
- FR-6 Reject duplicates by checksum; mark older versions `is_latest=false`.

### 10.2 Embeddings and retrieval
- FR-7 Embed chunks and queries with the same model.
- FR-8 Store vectors, text and metadata in the vector database.
- FR-9 Top-K similarity search with metadata filters (default `is_latest=true`).
- FR-10 Optional re-ranking of top-20 candidates to top-5.
- FR-11 Maintain the labelled evaluation set (§6.4) and a script that reports K1, K2.

### 10.3 Generation and guardrails
- FR-12 Assemble retrieved context within the 3,000-token budget.
- FR-13 Prompt the LLM to answer only from context and cite `[source, page]` per claim.
- FR-14 Refuse or ask for clarification when evidence is below threshold.
- FR-15 Decline personalised investment advice with a non-advice notice.
- FR-16 Support follow-ups using the last 4 turns.

### 10.4 Application
- FR-17 FastAPI REST API: `POST /documents`, `GET /documents`, `POST /chat`, `POST /chat/stream` (server-sent events), `GET /stats`, `GET /health`.
- FR-18 Streamlit chat UI with streaming, citation chips, source panel and filters.
- FR-19 Knowledge base UI with upload, status and versions.
- FR-20 Log requests, retrieved `chunk_id`s, refusals, errors and latency without secrets.
- FR-21 Cache answers for repeated questions (§6.2) and expose usage counts via `GET /stats`.

---

## 11. Non-functional requirements

| Area | Requirement |
|---|---|
| Performance | p95 answer ≤ 8 s, first token ≤ 2 s (K8); 50-page PDF indexed ≤ 60 s (K10) |
| Reliability | Retries with backoff (max 2) on LLM/vector DB errors; a failed upload never leaves partial chunks in the index |
| Traceability | Every answer maps to stored `chunk_id`s |
| Security | Secrets only in environment variables; `.env` git-ignored; `.env.example` provided; no secrets in logs |
| Reproducibility | Pinned `requirements.txt`; setup steps in README; one command to ingest the corpus and run evaluation |
| Maintainability | Separate modules for ingestion, embeddings, retrieval, RAG, API and UI |

---

## 12. Success criteria

Sprint 2 is successful when all **Must** user stories (§7) pass their acceptance criteria **and** KPIs K1, K3, K4, K5, K8 and K9 meet their targets on the final evaluation run, and the application can be deployed from the README by someone outside the team.

---

## 13. Risk register

Likelihood (L) and Impact (I) are scored 1 (low) – 3 (high). Severity = L × I.

| Risk | L | I | Severity | Impact if it happens | Mitigation | Early warning indicator |
|---|---|---|---|---|---|---|
| Hallucinated answers | 2 | 3 | **6 – High** | Advisor passes false information to a client → mis-selling complaint, regulatory exposure, loss of trust in the tool | Grounded prompt, score threshold, citation per claim, refusal handling; measured by K4 | K4 > 5% on review sample |
| Outdated document cited | 2 | 3 | **6 – High** | Client receives superseded fund data (e.g. old expense ratio) → compliance breach | Versioning, `is_latest` filter by default, published date shown on every citation | Answers citing `is_latest=false` chunks |
| Poor retrieval | 2 | 3 | **6 – High** | Correct document exists but is missed → false refusals or wrong answers; advisors stop using the tool | Eval set, tune chunk size/top-K, re-ranking, table flattening; measured by K1/K2 | Recall@5 < 0.85 on Day 4 |
| Over-refusal | 2 | 2 | 4 – Medium | Tool feels useless; advisors fall back to manual search, losing the time saving | Tune threshold against K5 and K6 together | K6 > 10% |
| Table/number extraction errors | 3 | 2 | **6 – High** | Wrong figures (AUM, NAV, exit load) in answers | Row-wise table flattening; spot-check 20 factsheet tables on Day 2 | Mismatch on spot-check |
| Exposed API keys | 1 | 3 | 3 – Medium | Unauthorised usage cost, account suspension, security incident | Env variables, `.gitignore`, secret scan before each PR | Key string found in diff |
| LLM/API outage or rate limit | 2 | 2 | 4 – Medium | Advisors cannot get answers; demo failure | Retries with backoff, clear error state, configurable provider | Error rate > 5% in logs |
| Latency above target | 2 | 2 | 4 – Medium | Slower than asking a colleague → low adoption | Batch embedding at index time, answer cache, top-5 context cap, streaming | p95 > 8 s |
| Duplicate documents | 2 | 1 | 2 – Low | Repeated citations, wasted context budget | SHA-256 checksum dedup | Duplicate checksum on upload |
| Free-tier API quota | 3 | 2 | **6 – High** | Scripts, evaluation or the live demo stop mid-run when per-model daily quotas (observed: 20 requests/day on the 2.5 models; varies by model) are used up | Model fallback chain, answer cache (C39), 40-question eval set, run evals early in the day (quotas reset at midnight Pacific) | 429 errors in logs |
| Team capacity (team reduced from 3 to 1 member) | 3 | 2 | **6 – High** | Scope slips; Should/Could stories may not ship | MoSCoW prioritisation; Must stories first; re-use libraries; weekly scope check | Milestone missed by > 2 days |

---

## 14. Future enhancements

- OCR for scanned documents.
- Role-based access control and SSO.
- Full compliance audit trail and answer approval workflow.
- Larger evaluation set and automated LLM-as-judge grading.
- Monitoring dashboard for KPIs.

---

## 15. Curriculum alignment

| Module | Outcome |
|---|---|
| 3.1 | RAG architecture and milestones |
| 3.2 | Secure LLM workspace |
| 3.3–3.4 | Document processing and embeddings |
| 3.5 | Vector database and retrieval |
| 3.6 | Grounded RAG pipeline |
| 3.7 | Web application and delivery |
| 3.8–3.9 | PRD and Mock UX |
| 3.10–3.11 | Workspace and GitHub workflow |
| 3.19–3.24 | Document ingestion |
| 3.25–3.29 | Embedding generation and quality |
| 3.30–3.36 | Vector search and retrieval evaluation |
| 3.37–3.43 | RAG, citations, guardrails, conversation, evaluation |
| 3.44–3.48 | API, upload, UI, streaming, monitoring |
| 3.49–3.50 | Deployment, documentation and final delivery |

---

## 16. Sprint 2 concept map

Each concept is delivered as one pull request linked to its issue.

| Concept | Name | Issue | PRD reference |
|---|---|---|---|
| C1 | Development Environment & Project Workspace Setup | [#3](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/3) | §11 |
| C2 | GitHub Repository & Team Workflow Setup | [#4](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/4) | — |
| C3 | LLM API Access & First Completion Call | [#5](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/5) | §6.2 |
| C4 | Prompt Construction & System/User Roles | [#6](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/6) | FR-13, FR-15 |
| C5 | Tokens, Tokenization & Cost Estimation | [#7](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/7) | §6.2 |
| C6 | Context Windows & Message History Management | [#8](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/8) | FR-16 |
| C7 | Model Parameters & Output Control | [#9](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/9) | §6.2 |
| C8 | Structured Output & JSON Response Handling | [#10](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/10) | §6.2, US-02 |
| C9 | Prompt Templates & Reusable Prompt Design | [#11](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/11) | FR-13 |
| C10 | Document Loading & Multi-Format Intake | [#12](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/12) | FR-1, FR-2 |
| C11 | Text Extraction & Cleaning Pipeline | [#13](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/13) | FR-3 |
| C12 | Document Chunking Strategies | [#14](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/14) | FR-4 |
| C13 | Chunk Metadata & Source Tracking | [#15](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/15) | §6.3, FR-5 |
| C14 | Token-Aware Chunk Sizing & Overlap | [#16](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/16) | §6.2 |
| C15 | Corpus Preparation & Ingestion Validation | [#17](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/17) | §6.1, K9 |
| C16 | Embeddings Fundamentals & Vector Representation | [#18](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/18) | — |
| C17 | Generating Embeddings via API | [#19](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/19) | FR-7 |
| C18 | Embedding Similarity & Distance Metrics | [#20](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/20) | §6.2 |
| C19 | Batch Embedding & Rate/Cost Management | [#21](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/21) | §6.2 |
| C20 | Embedding Quality Checks & Sanity Tests | [#22](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/22) | — |
| C21 | Vector Database Setup & Collection Design | [#23](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/23) | FR-8 |
| C22 | Indexing Embeddings & Metadata Storage | [#24](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/24) | FR-8, K9 |
| C23 | Similarity Search & Top-K Retrieval | [#25](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/25) | FR-9 |
| C24 | Metadata Filtering & Hybrid Search | [#26](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/26) | FR-9, US-07 |
| C25 | Retrieval Relevance Tuning | [#27](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/27) | K1 |
| C26 | Chunk Re-Ranking for Precision | [#28](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/28) | FR-10, K2 |
| C27 | Retrieval Evaluation & Recall Testing | [#29](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/29) | §6.4, K1, K2 |
| C28 | RAG Pipeline Architecture & Flow Design | [#30](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/30) | §8 |
| C29 | Context Injection & Prompt Augmentation | [#31](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/31) | FR-12 |
| C30 | Grounded Answer Generation | [#32](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/32) | FR-13, US-01 |
| C31 | Source Citation & Attribution | [#33](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/33) | US-02, US-03, K3 |
| C32 | Hallucination Guardrails & Refusal Handling | [#34](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/34) | FR-14, FR-15, K5, K6 |
| C33 | Conversational RAG & Follow-Up Context | [#35](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/35) | FR-16, US-06 |
| C34 | RAG Evaluation & Answer Quality Scoring | [#36](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/36) | K3–K6 |
| C35 | Backend API for the RAG Service | [#37](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/37) | FR-17 |
| C36 | Document Upload & Indexing Endpoint | [#38](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/38) | FR-1, FR-6, US-09–US-11 |
| C37 | Chat Interface & Query UI | [#39](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/39) | FR-18 |
| C38 | Streaming Responses & Citation Display | [#40](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/40) | US-08, K8 |
| C39 | Caching, Logging & Usage Monitoring | [#41](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/41) | FR-20, FR-21, US-12 |
| C40 | Deployment, Documentation & Delivery | [#42](https://github.com/itzhimanshugt/team03-65-Sprint-2/issues/42) | §11, §12 |
