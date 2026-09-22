# =============================================================================
# StudyAI Backend — Dockerfile (kehitys)
# =============================================================================
FROM python:3.12-slim

# Estä .pyc-tiedostojen luonti ja bufferointi (selkeämmät lokit)
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /app

# --- Järjestelmäriippuvuudet (mm. PyMuPDF) ---
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# --- Python-riippuvuudet ---
COPY requirements.txt .
RUN pip install --upgrade pip && pip install -r requirements.txt

# --- Sovelluskoodi ---
COPY . .

EXPOSE 8000

# Kehityksessä hot-reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]