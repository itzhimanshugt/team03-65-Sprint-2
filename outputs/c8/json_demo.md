# C8 — Structured JSON output

Context given to the model:

```
[1] chunk_id=abc-fs-0003 source="ABC Flexi Cap Fund Factsheet – Sep 2026.pdf" page=4
Exit load: 1% if redeemed within 365 days from allotment; nil after 365 days.

[2] chunk_id=abc-fs-0004 source="ABC Flexi Cap Fund Factsheet – Sep 2026.pdf" page=4
Total expense ratio (regular plan): 1.72%. Total expense ratio (direct plan): 0.68%.
```

## Q: What is the exit load and the direct-plan expense ratio of ABC Flexi Cap Fund?

```json
{
  "answer": "The ABC Flexi Cap Fund has an exit load of 1% if redeemed within 365 days from allotment, and nil after 365 days [1]. The total expense ratio for the direct plan is 0.68% [2].",
  "citations": [
    {
      "n": 1,
      "chunk_id": "abc-fs-0003",
      "source": "ABC Flexi Cap Fund Factsheet – Sep 2026.pdf",
      "page": 4
    },
    {
      "n": 2,
      "chunk_id": "abc-fs-0004",
      "source": "ABC Flexi Cap Fund Factsheet – Sep 2026.pdf",
      "page": 4
    }
  ],
  "refused": false
}
```

## Q: Who is the fund manager of ABC Flexi Cap Fund?

```json
{
  "answer": "I couldn't find this in the approved documents.",
  "citations": [],
  "refused": true
}
```