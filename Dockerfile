# One container: FastAPI on :8000 (internal) + Streamlit on :7860 (public, Hugging Face Spaces port).
FROM python:3.11-slim
RUN useradd -m -u 1000 user
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=user . .
USER user
EXPOSE 7860
CMD ["sh", "start.sh"]
