import os
import re
import html
from typing import Optional
from dotenv import load_dotenv
from langchain_core.documents import Document
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_openai import OpenAIEmbeddings

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
MARKDOWN_DIR = os.path.join(PROJECT_ROOT, "markdown")
VECTORSTORE_PATH = os.path.join(PROJECT_ROOT, "vectorstore", "abastible.json")
EMBEDDING_MODEL = "text-embedding-3-small"

MAX_CHARS = 3000
OVERLAP = 300


def flatten_tables(text: str) -> str:
    """Convierte cada <tr> HTML en 'celda | celda | celda': menos tokens y mejores embeddings."""
    def row(match: re.Match) -> str:
        cells = re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", match.group(0), re.S)
        cells = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip() for c in cells]
        return " | ".join(cells) + "\n"

    text = re.sub(r"<tr>.*?</tr>", row, text, flags=re.S)
    text = re.sub(r"</?(table|thead|tbody)>\s*", "", text)
    text = re.sub(r"<[^>]+>", "", text)          # restos como <u>
    text = re.sub(r"[ \t]+", " ", text)
    return re.sub(r"\n\s*\n+", "\n\n", text).strip()


def split_long(text: str) -> list[str]:
    """Subdivide páginas largas en trozos con solape, cortando en saltos de línea."""
    if len(text) <= MAX_CHARS:
        return [text]
    chunks, start = [], 0
    while start < len(text):
        end = min(start + MAX_CHARS, len(text))
        if end < len(text):
            cut = text.rfind("\n", start + MAX_CHARS // 2, end)
            end = cut if cut != -1 else end
        chunks.append(text[start:end].strip())
        if end == len(text):
            break
        start = end - OVERLAP
    return chunks


SECTION_PATTERN = re.compile(
    r"^#+\s*\**\s*((?:ESTADOS? (?:CONSOLIDADOS?|DE)[^\n]*)|(?:INFORME DEL AUDITOR[^\n]*)|(?:NOTA \d+[^\n]*))",
    re.M | re.I,
)


def find_section(content: str) -> Optional[str]:
    """Primer título de estado financiero, informe del auditor o nota que aparece en la página."""
    match = SECTION_PATTERN.search(content)
    return match.group(1).strip(" *").upper() if match else None


def load_documents() -> list[Document]:
    docs = []
    for file_name in sorted(os.listdir(MARKDOWN_DIR)):
        match = re.match(r"Abastible_(\d{4})\.md$", file_name)
        if not match:
            continue
        year = int(match.group(1))
        with open(os.path.join(MARKDOWN_DIR, file_name), encoding="utf-8") as f:
            raw = f.read()

        section = "Portada"
        # Cada página empieza con <!-- page N -->: la página es la unidad natural de cita.
        for page_match in re.finditer(r"<!-- page (\d+) -->(.*?)(?=<!-- page \d+ -->|\Z)", raw, re.S):
            page = int(page_match.group(1))
            content = flatten_tables(page_match.group(2))
            # La sección se arrastra entre páginas: una tabla que sigue en la página siguiente
            # conserva su título (ej. "ESTADOS CONSOLIDADOS DE RESULTADOS").
            section = find_section(content) or section
            if len(content) < 50:
                continue
            for chunk in split_long(content):
                # El prefijo ayuda al retriever a distinguir años y a preferir los estados principales
                # sobre las notas, donde se repiten filas como "Ingresos de actividades ordinarias".
                docs.append(Document(
                    page_content=f"[Abastible {year} — página {page} — {section}]\n{chunk}",
                    metadata={"year": year, "page": page, "section": section, "source": file_name},
                ))
    return docs


def build_vectorstore() -> None:
    docs = load_documents()
    print(f"Chunks generados: {len(docs)}")
    store = InMemoryVectorStore(OpenAIEmbeddings(model=EMBEDDING_MODEL))
    store.add_documents(docs)
    os.makedirs(os.path.dirname(VECTORSTORE_PATH), exist_ok=True)
    store.dump(VECTORSTORE_PATH)
    print(f"Vector store guardado en {VECTORSTORE_PATH}")


if __name__ == "__main__":
    load_dotenv(os.path.join(PROJECT_ROOT, ".env"))
    build_vectorstore()
