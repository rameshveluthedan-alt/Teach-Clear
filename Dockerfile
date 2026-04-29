# Dockerfile
# ----------
# Uses gunicorn to serve the Flask webhook app on Cloud Run.
# Cloud Run always expects the app to listen on port 8080.

FROM python:3.11-slim

WORKDIR /app

# Install dependencies first (cached layer)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Cloud Run sets PORT=8080 automatically
ENV PORT=8080

# gunicorn serves Flask — 1 worker is enough for a Telegram bot
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "1", "--timeout", "120", "TeachClear:app"]
