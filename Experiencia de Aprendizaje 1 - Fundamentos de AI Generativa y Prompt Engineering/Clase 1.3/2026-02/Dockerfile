FROM python:3.11-slim

WORKDIR /app

# Dependencias del sistema para markitdown (OCR de PDFs)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libgl1 \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Directorio de salida para el markdown generado por rag_ocr.py
RUN mkdir -p md
