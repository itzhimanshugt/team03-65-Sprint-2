# One container: FastAPI serves the API and the web UI on :7860 (PORT on Render).
FROM python:3.11-slim
RUN useradd -m -u 1000 user
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY --chown=user . .
RUN mkdir -p outputs data/logs && chown -R user:user /app  # boot writes the index, logs and reports
USER user
EXPOSE 7860
CMD ["sh", "start.sh"]
