import os

from googleapiclient.discovery import build
from langchain.tools import tool


@tool
def sumar(a: float, b: float) -> float:
    """Suma dos números y retorna el resultado."""
    return a + b


@tool
def restar(a: float, b: float) -> float:
    """Resta b de a y retorna el resultado."""
    return a - b


@tool
def multiplicar(a: float, b: float) -> float:
    """Multiplica dos números y retorna el resultado."""
    return a * b


@tool
def dividir(a: float, b: float) -> float:
    """Divide a entre b y retorna el resultado. No se puede dividir entre cero."""
    if b == 0:
        raise ValueError("No se puede dividir entre cero.")
    return a / b


@tool
def buscar_en_internet(consulta: str) -> str:
    """Busca en internet con Google y retorna los 5 primeros resultados (titulo, enlace y resumen).
    Usala para informacion actual o que no sea una operacion matematica."""
    api_key = os.getenv("GOOGLE_API_KEY")
    cse_id = os.getenv("GOOGLE_CSE_ID")
    if not api_key or not cse_id:
        raise RuntimeError("Faltan GOOGLE_API_KEY o GOOGLE_CSE_ID en el .env.")
    service = build("customsearch", "v1", developerKey=api_key)
    response = service.cse().list(q=consulta, cx=cse_id, num=5).execute()
    items = response.get("items", [])
    if not items:
        return "No se encontraron resultados."
    return "\n\n".join(
        f"{i}. {item['title']}\n{item['link']}\n{item.get('snippet', '')}"
        for i, item in enumerate(items, 1)
    )