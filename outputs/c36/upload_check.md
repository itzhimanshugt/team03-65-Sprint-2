# C36 — Upload & indexing, live via POST /documents

1. Upload v1 (`office-hours.md`, version 1):

   `{"doc_id":"bccd2aab3431","status":"Indexed","chunks":2,"superseded_chunks":0} (HTTP 201)`

2. Ask "What are the compliance desk hours?":

   The compliance desk is available to answer advisor questions from 9:30 am to 6:00 pm IST, Monday to Friday [1]. | cited: [('office-hours.md', 2)]

3. Upload the same file again:

   `{"detail":"This exact file is already indexed (duplicate checksum)."} (HTTP 409)`

4. Upload v2 (`office-hours-v2.md`, version 2):

   `{"doc_id":"d67e8dcc76cf","status":"Indexed","chunks":2,"superseded_chunks":2} (HTTP 201)`

5. Ask again (v1 is now superseded, so it is excluded):

   From 1 November 2026, the compliance desk is available to answer advisor questions from 9:00 am to 7:00 pm IST, Monday to Saturday [1]. | cited: [('office-hours-v2.md', 2)]

6. Upload an unsupported file:

   `{"detail":"Unsupported file type .exe. Use PDF, HTML, TXT or MD."} (HTTP 400)`


Note: the first run of step 5 returned the stale v1 answer from the C39 query cache. Fix: `POST /documents` now clears the cache (tested in `test_upload_clears_query_cache`). Step 5 was then re-run.
