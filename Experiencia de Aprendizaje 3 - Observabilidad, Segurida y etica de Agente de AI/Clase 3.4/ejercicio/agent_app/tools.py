from pymongo import MongoClient
from agent_app.utils.embeddings import EmbeddingClient
import os
from dotenv import load_dotenv

load_dotenv()

embedder = EmbeddingClient()
mongo_client = MongoClient(os.getenv("MONGODB_CONNECTION_STRING"))
collection = mongo_client["agent-rag-duoc-uc"]["embeddings"]


def retrieve(query: str, top_k: int = 5) -> list[dict]:
    query_embedding = embedder.get_embedding(query)

    results = collection.aggregate([
        {
            "$vectorSearch": {
                "index": "vector_index",
                "path": "embedding",
                "queryVector": query_embedding,
                "numCandidates": top_k * 10,
                "limit": top_k,
            }
        },
        {
            "$project": {
                "_id": 0,
                "text": 1,
                "metadata": 1,
                "score": {"$meta": "vectorSearchScore"},
            }
        }
    ])

    return list(results)
