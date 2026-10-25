# Deploying VerifAI (Render, free)

One Docker container runs FastAPI, which serves both the API and the web UI. At start-up it builds the Chroma index from the committed embedding cache (`data/processed/`, about 15 MB), so deploying makes **no embedding API calls**.

1. Sign in at https://render.com with GitHub.
2. Click **New → Blueprint**, pick `itzhimanshugt/team03-65-Sprint-2` and branch `main`. Render reads `render.yaml`, which defines one free Docker web service called `verifai`.
3. When asked for **`LLM_API_KEY`**, paste your Gemini key. It is stored only in Render.
4. Click **Apply**. The first build takes about 5–10 min.
5. Open `https://verifai-XXXX.onrender.com` and ask one question.
6. Send the URL, so it can go into the README under **Live demo**.

Notes:
- The free plan sleeps after 15 min idle. The first visit after that takes about 30–60 s.
- The free plan has 512 MB of RAM. If the logs show "out of memory", the index needs a smaller footprint; report it.

Run the same container locally:

```bash
docker build -t verifai .
docker run -p 7860:7860 --env-file .env verifai
```
