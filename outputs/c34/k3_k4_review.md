# C34 — K3 citation accuracy and K4 hallucination review

Source: `outputs/c34/review_sheet.md` (40-question run with re-ranking and same-page neighbours, 24 Oct 2026).

**Method:**
- Every `[n]` citation in the 30 answerable answers was checked against the full text of the cited page in the latest document version.
- A citation is supported if that page states the fact in the sentence it is attached to.
- Different date formats count as a match. The snapshot tables write `08-Jan-10` for `08 January 2010`, and the four such cases were verified by hand.

| Result | Count |
|---|---|
| Citations checked | 47 |
| Supported | **47** |
| Unsupported | 0 |
| **K3 citation accuracy** | **100%** (target ≥ 90%) ✅ |
| Answers with a factual claim | 29 (q26 is a soft refusal with no claims) |
| Answers with ≥ 1 claim not in the retrieved context | **0** |
| **K4 hallucination rate** | **0%** (target ≤ 5%) ✅ |

**Notes:**
- Extra claims beyond the reference answer were checked too, and both are supported:
  - q18 names the CIO-Debt (Tejas Soman), which appears on PPFAS p.2.
  - q23 adds the NISM V-A exemption, which appears in the SIF circular p.2.
- Several answers also cite the fund snapshot tables (HSBC p.156–160, p.171–172). Those pages repeat the same benchmark, allotment date and fund manager, so the citations are valid second sources.
- The one remaining miss is q26, a two-fund comparison. It is a recall problem (the chunk was not retrieved), not a grounding problem: the model said it could not find the answer instead of inventing one.
