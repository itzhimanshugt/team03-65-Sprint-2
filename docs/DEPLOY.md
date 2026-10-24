# Deploying VerifAI (Hugging Face Spaces, free CPU)

The container runs the API and the Streamlit UI together. At start-up it builds the Chroma index from the cached embeddings in `data/processed/`, so deploying costs **no embedding quota**.

1. Create a Space at https://huggingface.co/new-space:
   - SDK: **Docker**
   - Hardware: **CPU basic (free)**
   - Visibility: public
2. In the Space, go to **Settings → Variables and secrets** and add the secret `LLM_API_KEY` (your Gemini key). Never commit it.
3. Push the code together with the cached embeddings. They are git-ignored here, so upload them explicitly:

   ```bash
   pip install -U huggingface_hub
   huggingface-cli login
   huggingface-cli upload <user>/verifai . . --repo-type space --exclude ".env" ".git/*" "data/chroma/*" "data/logs/*" "data/raw/*" ".worktrees/*"
   ```

   `data/processed/` (chunks + vectors, about 15 MB) is included by this upload.
4. Wait for the build (about 5 min), then open `https://huggingface.co/spaces/<user>/verifai`.
5. Put that URL in the README under **Live demo**.

Run the same container locally:

```bash
docker build -t verifai .
docker run -p 7860:7860 --env-file .env verifai
```
