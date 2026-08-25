"""
RAG Script 2 — Extraccion con OCR (LlamaParse -> Markdown)
===========================================================
Pipeline:
  PDF -> LlamaParse (OCR cloud) -> Markdown limpio -> chunks semanticos
       -> embeddings OpenAI -> FAISS
       -> reranking (cross-encoder) -> gpt-4o-mini -> respuesta

Diferencia clave vs rag_pypdf.py:
  LlamaParse produce Markdown de alta calidad preservando titulos, tablas
  y estructura del documento, lo que mejora significativamente la recuperacion.

Uso:
  python rag_ocr.py
"""

import os
import numpy as np
import faiss
from dotenv import load_dotenv
from llama_parse import LlamaParse
from langchain_text_splitters import MarkdownTextSplitter
from openai import OpenAI
from sentence_transformers import CrossEncoder

load_dotenv()

# ---------------------------------------------------------------------------
# Configuracion
# ---------------------------------------------------------------------------
PDF_PATH = "input/Experiencia de Aprendizaje 1 - Fundamentos de AI Generativa y Prompt Engineering.pdf"
MD_OUTPUT = "md/documento_ocr.md"   # opcional: guarda el MD para inspeccion en clase
EMBED_MODEL = "text-embedding-3-small"
CHAT_MODEL  = "gpt-4o-mini"
CHUNK_SIZE  = 1000
CHUNK_OVERLAP = 200
FAISS_TOP_K = 40
RERANK_TOP_K = 8
DEBUG = True   # True: muestra contenido de chunks recuperados

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
reranker = CrossEncoder("cross-encoder/ms-marco-MiniLM-L-6-v2")


# ---------------------------------------------------------------------------
# PASO 1 — Extraccion con LlamaParse (OCR cloud -> Markdown)
# ---------------------------------------------------------------------------
def extract_markdown_ocr(pdf_path: str) -> str:
    print(f"[llamaparse] Procesando: {pdf_path}")
    parser = LlamaParse(
        api_key=os.getenv("LLAMA_CLOUD_API_KEY"),
        result_type="markdown",
        verbose=False,
    )
    documents = parser.load_data(pdf_path)
    markdown_text = "\n\n".join(doc.text for doc in documents)
    print(f"[llamaparse] Markdown generado: {len(markdown_text)} caracteres")

    # Guardar MD para que los estudiantes lo puedan comparar con el texto plano
    os.makedirs(os.path.dirname(MD_OUTPUT), exist_ok=True)
    with open(MD_OUTPUT, "w", encoding="utf-8") as f:
        f.write(markdown_text)
    print(f"[llamaparse] Guardado en: {MD_OUTPUT}\n")

    return markdown_text


# ---------------------------------------------------------------------------
# PASO 2 — Chunking semantico respetando estructura Markdown
# ---------------------------------------------------------------------------
def split_into_chunks(markdown_text: str) -> list[str]:
    # MarkdownTextSplitter intenta no cortar en medio de secciones
    splitter = MarkdownTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    chunks = splitter.split_text(markdown_text)
    print(f"[chunking] {len(chunks)} chunks semanticos (size={CHUNK_SIZE}, overlap={CHUNK_OVERLAP})")

    # Vista previa de los primeros chunks para clase
    print("\n--- Vista previa de los primeros 2 chunks ---")
    for i, chunk in enumerate(chunks[:2]):
        preview = chunk[:200].replace("\n", " ")
        print(f"  Chunk {i}: \"{preview}...\"")
    print()
    return chunks


# ---------------------------------------------------------------------------
# PASO 3 — Embeddings con OpenAI
# ---------------------------------------------------------------------------
def embed_texts(texts: list[str]) -> np.ndarray:
    # Eliminar surrogates invalidos que rompen el encoder UTF-8 de la API
    texts = [t.encode("utf-8", errors="ignore").decode("utf-8") for t in texts]
    print(f"[embeddings] Generando embeddings para {len(texts)} chunks...")
    response = client.embeddings.create(model=EMBED_MODEL, input=texts)
    vectors = [item.embedding for item in response.data]
    matrix = np.array(vectors, dtype="float32")
    print(f"[embeddings] Matriz: {matrix.shape}\n")
    return matrix


# ---------------------------------------------------------------------------
# PASO 4 — Indexar en FAISS
# ---------------------------------------------------------------------------
def build_faiss_index(matrix: np.ndarray) -> faiss.IndexFlatIP:
    faiss.normalize_L2(matrix)
    dim = matrix.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(matrix)
    print(f"[faiss] Indice construido con {index.ntotal} vectores (dim={dim})\n")
    return index


# ---------------------------------------------------------------------------
# PASO 5 — Busqueda FAISS
# ---------------------------------------------------------------------------
def faiss_search(query: str, index: faiss.IndexFlatIP, top_k: int) -> list[int]:
    q_vec = embed_texts([query])
    faiss.normalize_L2(q_vec)
    scores, indices = index.search(q_vec, top_k)
    print(f"[faiss] Top-{top_k} candidatos: {indices[0].tolist()}")
    return indices[0].tolist()


# ---------------------------------------------------------------------------
# PASO 6 — Reranking con cross-encoder
# ---------------------------------------------------------------------------
def rerank(query: str, candidates: list[str], top_k: int) -> list[str]:
    pairs = [(query, chunk) for chunk in candidates]
    scores = reranker.predict(pairs)
    ranked = sorted(zip(scores, candidates), reverse=True)

    print(f"[rerank] Scores top-{top_k}: {[round(float(s), 3) for s, _ in ranked[:top_k]]}")

    if DEBUG:
        print("\n--- Chunks seleccionados para el LLM ---")
        for i, (score, chunk) in enumerate(ranked[:top_k]):
            preview = chunk[:300].replace("\n", " ")
            print(f"  [{i}] score={round(float(score), 3)} | {preview}...")
        print()

    return [chunk for _, chunk in ranked[:top_k]]


# ---------------------------------------------------------------------------
# PASO 7 — Generacion con OpenAI
# ---------------------------------------------------------------------------
def generate_answer(query: str, context_chunks: list[str], history: list[dict]) -> str:
    context = "\n\n---\n\n".join(context_chunks)
    system_prompt = """\
Eres un asistente academico amable y conversacional.

Tienes tres fuentes de informacion disponibles:
1. El HISTORIAL DE CONVERSACION (mensajes anteriores entre el usuario y tu).
2. El CONTEXTO DEL DOCUMENTO (fragmentos recuperados del PDF).
3. Tu conocimiento general para respuestas de cortesia.

REGLAS:
- Si la pregunta es de saludo, cortesia o conversacion general (ej: "hola", "como estas", "gracias"), responde de forma natural y amable. No menciones el contexto.
- Si la pregunta se puede responder con el historial de conversacion (ej: el usuario te dijo su nombre antes), responde usando ese historial.
- Si la pregunta es sobre el documento, usa el contexto proporcionado. Lee TODOS los fragmentos antes de responder. Si hay tablas en Markdown, reproducilas completas.
- SOLO di que no tienes la informacion si no esta ni en el historial ni en el contexto del documento.
- Responde siempre en el mismo idioma de la pregunta.
- No inventes informacion del documento."""
    user_prompt = f"Contexto (revisa todos los fragmentos):\n\n{context}\n\nPregunta: {query}"

    messages = [{"role": "system", "content": system_prompt}]
    messages += history
    messages.append({"role": "user", "content": user_prompt})

    response = client.chat.completions.create(
        model=CHAT_MODEL,
        messages=messages,
        temperature=0.2,
    )
    return response.choices[0].message.content


# ---------------------------------------------------------------------------
# Pipeline principal
# ---------------------------------------------------------------------------
def build_pipeline(pdf_path: str):
    markdown = extract_markdown_ocr(pdf_path)
    chunks   = split_into_chunks(markdown)
    matrix   = embed_texts(chunks)
    index    = build_faiss_index(matrix)
    return chunks, index


def query_pipeline(query: str, chunks: list[str], index: faiss.IndexFlatIP, history: list[dict]) -> str:
    print(f"\n{'='*60}")
    print(f"Query: {query}")
    print('='*60)

    candidate_ids = faiss_search(query, index, FAISS_TOP_K)
    candidates    = [chunks[i] for i in candidate_ids if i < len(chunks)]
    top_chunks    = rerank(query, candidates, RERANK_TOP_K)
    answer        = generate_answer(query, top_chunks, history)
    return answer


# ---------------------------------------------------------------------------
# Main interactivo
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    print("="*60)
    print("  RAG con OCR (LlamaParse -> Markdown)")
    print("="*60 + "\n")

    chunks, index = build_pipeline(PDF_PATH)
    history: list[dict] = []

    print("\nIndexacion completa. Escribe tu pregunta (o 'salir' para terminar).\n")

    while True:
        query = input("Pregunta: ").strip()
        if not query or query.lower() in ("salir", "exit", "quit"):
            break
        answer = query_pipeline(query, chunks, index, history)
        print(f"\nRespuesta:\n{answer}\n")
        history.append({"role": "user",      "content": query})
        history.append({"role": "assistant", "content": answer})
