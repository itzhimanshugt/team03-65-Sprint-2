# Mock UX — Annotations, Empty States and Flow (VerifAI)

Companion to [PRD.md](../PRD.md) §8–§9. This file is the spec for the Figma updates requested in review: **annotations**, **empty states** and a **flow diagram**.

Figma file: [team03-sprint2-verifai](https://www.figma.com/design/S3lVpz5bkKkSrrjuv9URYr/team03-sprint2-verifai-?node-id=0-1)

## Status in Figma (done)

The Figma file now contains everything this spec asks for:

| Page | What it contains |
|---|---|
| **01 Screens** | The 8 original screens, each with numbered gold annotation markers (A1.1 …) and an *Annotations* card beside it |
| **02 Empty & error states** | All 11 states below (S1a–S6a), in the file's visual style |
| **03 User flow** | Advisor and compliance lanes with every screen, state and decision |

Spec screen IDs map to the Figma screens like this:

| Spec ID | Figma screen | Annotation prefix |
|---|---|---|
| S1 + S2 | Ask Assistant | A1 |
| S3 | Evidence Dossier | A2 |
| — (KPI dashboard) | Executive Overview | A3 |
| S4 | Prospectus Vault | A4 |
| S5 | Ingest & Certify | A5 |
| S2c / S2d | Zero-Risk Guardrails | A6 |
| — (thresholds and policy) | Governance Mandate | A7 |
| S6 | Audit & Ledger Log | A8 |

## How to apply this in Figma

1. **Pages:** create three pages — `01 Screens`, `02 Empty & error states`, `03 User flow`.
2. **Frame names:** rename frames to the screen IDs below (e.g. `S1 – Chat home`) so they match the PRD.
3. **Annotations:** use Dev Mode → *Annotate* (or a yellow sticky/callout component) and add the numbered notes below next to each element. Number them `S1.1`, `S1.2`, …
4. **Empty states:** duplicate the base frame for each state in the table and swap the content area for the empty-state block (icon + headline + one line + primary button).
5. **Flow diagram:** on `03 User flow`, place small copies of each frame and connect them with arrows (FigJam connectors, or Figma *Prototype* connections with the flow starting point set on S1). Use the Mermaid diagram in PRD §8 as the map.

## Screen inventory

| ID | Screen | User | Linked user stories |
|---|---|---|---|
| S1 | Chat home | Advisor | US-01, US-07 |
| S2 | Answer with citations (streaming) | Advisor | US-01, US-02, US-06, US-08 |
| S3 | Source panel | Advisor | US-03 |
| S4 | Knowledge base (document list) | Compliance | US-09, US-11 |
| S5 | Upload document | Compliance | US-09, US-10, US-11 |
| S6 | Activity log | Compliance | US-12 |

If your Figma has different or fewer screens, keep the IDs and map them to the closest frame.

## Annotations per screen

### S1 — Chat home
| # | Element | Annotation |
|---|---|---|
| S1.1 | Question input | Free text, max 500 chars. Enter = send, Shift+Enter = new line. Disabled when knowledge base is empty. |
| S1.2 | Filter chips (Doc type / Issuer / Date) | Optional. Applied as metadata filters before retrieval (FR-9). Active filters stay visible above the chat. |
| S1.3 | Example questions | 3 clickable examples shown only in the empty state; clicking fills and sends the question. |
| S1.4 | Disclaimer footer | "VerifAI answers only from approved documents and does not give investment advice." Always visible. |
| S1.5 | New chat button | Clears conversation memory (last-4-turn context). |

### S2 — Answer with citations
| # | Element | Annotation |
|---|---|---|
| S2.1 | Streaming answer | Tokens stream in; first token target ≤ 2 s (K8). Typing indicator shown before first token. |
| S2.2 | Citation chip `[1]` | Shows `source_name · p.X`. Every factual sentence has ≥ 1 chip (US-02). Click opens S3. |
| S2.3 | Sources list under answer | Deduplicated list of cited documents with published date and "Latest" badge. |
| S2.4 | Confidence/grounding label | "Grounded in 3 sources" when answered; replaced by S2c when refused. |
| S2.5 | Copy answer | Copies answer text **with** citations, so the advisor can paste into client notes. |
| S2.6 | Follow-up input | Same as S1.1; previous turns are used as context (US-06). |

### S3 — Source panel
| # | Element | Annotation |
|---|---|---|
| S3.1 | Highlighted passage | Exact retrieved chunk, highlighted within surrounding page text. |
| S3.2 | Document meta | Document name, issuer, doc type, page, published date, version, "Latest"/"Superseded" badge. |
| S3.3 | Superseded warning | If `is_latest=false`, yellow banner: "A newer version exists" + link. |
| S3.4 | Close | Returns to S2 with scroll position kept. |

### S4 — Knowledge base
| # | Element | Annotation |
|---|---|---|
| S4.1 | Document table | Columns: Name, Type, Issuer, Published, Version, Status (Indexing / Indexed / Failed), Chunks. |
| S4.2 | Status badge | Indexing = blue, Indexed = green, Failed = red with hover tooltip giving the reason. |
| S4.3 | Upload button | Opens S5. Visible to compliance role only. |
| S4.4 | Version history | Expand row to see older versions (excluded from retrieval by default). |

### S5 — Upload document
| # | Element | Annotation |
|---|---|---|
| S5.1 | Drop zone | Text-based PDF only, ≤ 25 MB. |
| S5.2 | Metadata fields | Doc type (required, dropdown), Issuer (required), Published date (required). |
| S5.3 | "Replaces existing document" toggle | When on, choose the document being replaced; old version is marked not latest (US-11). |
| S5.4 | Progress | Steps: Uploading → Extracting → Chunking → Embedding → Indexed. Target ≤ 60 s for 50 pages (K10). |
| S5.5 | Validation errors | Inline, specific reason (see empty/error states). |

### S6 — Activity log
| # | Element | Annotation |
|---|---|---|
| S6.1 | Log table | Time, question, cited documents, Refused (Y/N), latency. No secrets or keys ever shown. |
| S6.2 | Filter "Refused only" | Lets compliance review refusals to find gaps in the document set. |

## Empty and error states to add

Each needs its own frame on the `02 Empty & error states` page. Copy is final, so use it as written.

| Frame name | Base screen | Headline | Supporting line | Primary action |
|---|---|---|---|---|
| S1a – Empty chat | S1 | Ask anything about your approved documents | Every answer comes with its sources. | 3 example question chips |
| S1b – No documents (advisor) | S1 | No approved documents yet | Ask your compliance team to upload documents. | — (input disabled) |
| S1c – No filter matches | S1 | No documents match these filters | Try removing a filter. | Clear filters |
| S2c – Not enough evidence | S2 | I couldn't find this in the approved documents | So I won't guess. Try rephrasing or check your filters. | Rephrase |
| S2d – Advice request | S2 | I can share facts, not investment advice | Here is what the approved documents say about this fund. | Show related facts |
| S2e – Service error | S2 | Something went wrong | The answer couldn't be generated. Your question is saved. | Retry |
| S3a – Source superseded | S3 | This source has been replaced | A newer version was approved on {date}. | Open latest version |
| S4a – Empty knowledge base | S4 | Upload your first approved document | Advisors can ask questions once it is indexed. | Upload document |
| S5a – Upload failed | S5 | We couldn't index this file | e.g. "This PDF has no selectable text (scanned)." / "File is larger than 25 MB." / "File is password protected." | Choose another file |
| S5b – Duplicate | S5 | This document is already in the knowledge base | Uploaded on {date} by {user}. | View document |
| S6a – Empty log | S6 | No questions asked yet | Activity will appear here. | — |

**Empty-state component (reuse everywhere):** 48 px outline icon → headline (16–18 px semibold) → one supporting line (14 px, muted) → one primary button. Centered in the content area.

## Flow diagram

Use PRD §8 "Flow diagram" as the source. Minimum arrows to draw in Figma:

- S1 → S2 (ask) → S3 (click citation) → S2 (close)
- S2 → S1/S2 (follow-up)
- S1 → S2c (low evidence) → S1 (rephrase)
- S1 → S2d (advice request)
- S2 → S2e (error) → S2 (retry)
- S4 → S5 (upload) → S4 (indexed) | S5a (failed) | S5b (duplicate)
- S4 → S6 (activity log)
- S1 ↔ S1b, S4 ↔ S4a (empty knowledge base)
