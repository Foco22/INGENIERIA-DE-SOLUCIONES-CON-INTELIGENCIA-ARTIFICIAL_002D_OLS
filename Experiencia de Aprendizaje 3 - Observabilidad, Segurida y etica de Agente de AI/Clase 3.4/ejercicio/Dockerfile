FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY server.py .
COPY agent_app/__init__.py ./agent_app/__init__.py
COPY agent_app/tools.py ./agent_app/tools.py
COPY agent_app/utils/embeddings.py ./agent_app/utils/embeddings.py

ENV PORT=8080
CMD ["python", "server.py"]
