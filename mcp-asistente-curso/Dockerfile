# Imagen del servidor MCP (server/main.py), desplegada en Cloud Run — ver plan.md §5.3.
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8080

# Cloud Run inyecta PORT; el server debe escuchar ahí (no un puerto fijo)
CMD uvicorn server.main:app --host 0.0.0.0 --port ${PORT:-8080}
