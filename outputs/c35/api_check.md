# C35 — API live check (uvicorn app.api.main:app)

`GET /health`
```json
{"status":"ok","chunks_indexed":2824}
```

`GET /documents` (first 2)
```json
20 documents
[
 {
  "doc_id": "109cc27312b9",
  "source_name": "client-communication-guidelines.md",
  "title": "Client communication guidelines (simulated internal document)",
  "doc_type": "internal",
  "issuer": "VerifAI Demo Advisory Firm",
  "published_date": "2026-10-01",
  "version": 1,
  "is_latest": true,
  "chunks": 7
 },
 {
  "doc_id": "d15820b5bf72",
  "source_name": "firm-faq.md",
  "title": "Advisor FAQ (simulated internal document)",
  "doc_type": "internal",
  "issuer": "VerifAI Demo Advisory Firm",
  "published_date": "2026-10-01",
  "version": 1,
  "is_latest": true,
  "chunks": 6
 }
]
```

`POST /chat` {"question": "What is the benchmark of Parag Parikh Flexi Cap Fund?"}
```json
{
 "answer": "The benchmark for the Parag Parikh Flexi Cap Fund is the NIFTY 500 (TRI) [1].",
 "standalone_question": "What is the benchmark of Parag Parikh Flexi Cap Fund?",
 "refused": false,
 "refusal": null,
 "citations": [
  {
   "n": 1,
   "source_name": "ppfas-factsheet-2026-09.pdf",
   "page": 2,
   "title": "PPFAS MF Factsheet - September 2026",
   "chunk_id": "6fde0dc4cd3e-0001",
   "text": "Parag Parikh Flexi Cap Fund\nType of Scheme: An open-ended dynamic Equity scheme …"
  }
 ]
}
```

Swagger (`/docs`) lists:
['/chat', '/documents', '/health', '/stats']
(`/stats` is from C39; it was already on the branch when this check ran.)
