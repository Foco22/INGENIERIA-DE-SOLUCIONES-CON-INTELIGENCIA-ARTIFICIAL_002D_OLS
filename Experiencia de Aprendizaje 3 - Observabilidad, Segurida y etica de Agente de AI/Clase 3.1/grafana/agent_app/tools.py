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
        return "Error: no se puede dividir entre cero."
    return a / b