# RAG DuocUC

A Retrieval-Augmented Generation (RAG) chatbot built for the course **Ingeniería de Soluciones con Inteligencia Artificial** at DuocUC.

## Architecture

```
PDF (GitHub) → Ingestion → MongoDB (embeddings) → Retrieval → LLM → Answer
```

| Component | Technology |
|-----------|-----------|
| Embedding | OpenAI `text-embedding-3-small` |
| Vector DB | MongoDB Atlas (Vector Search) |
| LLM | OpenAI `gpt-4o-mini` |
| UI | Streamlit |
| Observability | LangSmith |
| Evaluation | RAGAS |
| Container | Docker |

## Project Structure

```
├── app.py                  # Streamlit app
├── Dockerfile
├── requirements.txt
├── prompts/
│   └── prompt.py           # System prompts
├── src/
│   ├── ingesta/
│   │   └── ingest.py       # PDF ingestion pipeline
│   ├── retrieval/
│   │   └── retrieval.py    # Vector search retrieval
│   ├── generate/
│   │   └── generate.py     # RAG generation
│   └── utils/
│       ├── embeddings.py   # OpenAI embeddings client
│       ├── llm.py          # OpenAI LLM client
│       └── mongodb.py      # MongoDB client
└── eval/
    ├── dataset.json        # Evaluation questions + ground truth
    └── evaluate.py         # RAGAS evaluation script
```

## Setup

### 1. Environment variables

Create a `.env` file:

```env
OPENAI_API_KEY=your_openai_api_key
MONGODB_CONNECTION_STRING=mongodb+srv://user:password@cluster.mongodb.net/
GITHUB_REPO=https://github.com/your/repo
LANGCHAIN_TRACING_V2=true
LANGCHAIN_API_KEY=your_langsmith_api_key
LANGCHAIN_PROJECT=your_project_name
```

### 2. MongoDB Atlas — Vector Search Index

Before running the app, create the vector search index by running:

```bash
python3 create_vector_index.py
```

Or create it manually in Atlas with:

```json
{
  "fields": [{
    "type": "vector",
    "path": "embedding",
    "numDimensions": 1536,
    "similarity": "cosine"
  }]
}
```

- **Database:** `agent-rag-duoc-uc`
- **Collection:** `embeddings`
- **Index name:** `vector_index`

### 3. Run with Docker

```bash
docker build -t rag-duoc-uc .
docker run --env-file .env -p 8501:8501 rag-duoc-uc
```
or 

```bash
docker build -t rag-duoc-uc .
docker run -p 8501:8501 rag-duoc-uc
```

Open [http://localhost:8501](http://localhost:8501)

### 4. What is it missing?

1. CI/CD for automation.
2. A database for sessions and users. It should store all conversations.
3. User feedback collection.
4. Cost per interaction (this can be stored in the same database).
5. Architecture design diagram.
6. Store environment variables in GitHub.
