# RAG Demo - Clase 1.3: Fundamentos de AI Generativa

## Objetivo pedagogico

Demostrar dos estrategias distintas de **Retrieval-Augmented Generation (RAG)** sobre el mismo
documento PDF, para que los estudiantes comprendan como la calidad del texto recuperado impacta
directamente la calidad de la respuesta generada.

---

## Arquitectura general

```
PDF de entrada
    |
    +---> [Script 1] Extraccion directa con pypdf
    |         |
    |         v
    |     chunks de texto plano
    |
    +---> [Script 2] OCR con markitdown -> Markdown -> chunks semanticos
              |
              v
          chunks enriquecidos con estructura

Ambos scripts comparten el mismo pipeline aguas abajo:
    chunks --> embeddings (OpenAI) --> FAISS --> reranking (Cohere / cross-encoder)
           --> top-k contexto --> OpenAI GPT --> respuesta final
```

---

## Scripts

| Archivo | Descripcion |
|---|---|
| `rag_pypdf.py` | Retrieval con extraccion de texto via **pypdf** (metodo simple) |
| `rag_ocr.py` | Retrieval con **markitdown** (OCR) que convierte PDF a Markdown, luego chunking semantico |

---

## Stack tecnico

| Componente | Herramienta |
|---|---|
| Extraccion simple | `pypdf` |
| OCR / PDF-to-Markdown | `markitdown` (Microsoft) |
| Chunking | `langchain_text_splitters.RecursiveCharacterTextSplitter` |
| Embeddings | `text-embedding-3-small` (OpenAI) |
| Vector store | `faiss-cpu` + `numpy` |
| Reranking | `sentence-transformers` cross-encoder (`ms-marco-MiniLM-L-6-v2`) |
| Generacion | `gpt-4o-mini` (OpenAI) |
| Config | `python-dotenv` (OPENAI_API_KEY en `.env`) |

---

## Flujo detallado de cada script

### Script 1 — `rag_pypdf.py`

1. Leer PDF con `pypdf.PdfReader`
2. Concatenar texto de todas las paginas
3. Chunking con overlap
4. Generar embeddings OpenAI para cada chunk
5. Indexar en FAISS
6. Recibir query del usuario
7. Embedding de la query -> busqueda FAISS top-20
8. Reranking con cross-encoder -> top-5
9. Construir prompt con contexto + query
10. Llamar `gpt-4o-mini` y mostrar respuesta

### Script 2 — `rag_ocr.py`

1. Convertir PDF a Markdown con `markitdown` (preserva titulos, tablas, listas)
2. Chunking semantico respetando headers Markdown
3. Pasos 4-10 identicos al Script 1

---

## Diferencias clave a mostrar en clase

- **Calidad del texto**: pypdf puede perder formato; markitdown preserva estructura semantica
- **Chunking**: texto plano vs chunks conscientes de secciones Markdown
- **Impacto en recuperacion**: el reranker favorece chunks con contexto estructural claro
- **Conclusion**: mejor extraccion = mejor RAG, aunque el pipeline sea el mismo

---

## Setup

```bash
pip install pypdf markitdown langchain-text-splitters openai faiss-cpu \
            sentence-transformers numpy python-dotenv
```

Crear `.env` en la raiz del proyecto:
```
OPENAI_API_KEY=sk-...
```

PDF de prueba: `input/Experiencia de Aprendizaje 1 - Fundamentos de AI Generativa y Prompt Engineering.pdf`

---

## Proximos pasos

- [ ] Implementar `rag_pypdf.py`
- [ ] Implementar `rag_ocr.py`
- [ ] Comparar resultados con la misma query sobre ambos scripts
