"""Lee interacciones no evaluadas de Supabase, corre el LLM-as-judge (DeepSeek),
escribe los scores de vuelta. Corrido por eval-judge.yml (cron diario, §5.5).
"""

from __future__ import annotations

from utils.llm import evaluar_interaccion
from utils.supabase import get_pendientes_de_evaluar, update_scores


def run(limit: int = 50) -> int:
    """Evalúa hasta `limit` interacciones pendientes. Devuelve cuántas procesó."""
    pendientes = get_pendientes_de_evaluar(limit=limit)
    for fila in pendientes:
        fragmentos_texto = [f["texto"] for f in fila["fragmentos"]]
        relevancia, fundamentacion = evaluar_interaccion(
            query=fila["query"], fragmentos_texto=fragmentos_texto, respuesta=fila.get("respuesta")
        )
        update_scores(fila["id"], relevancia_score=relevancia, fundamentacion_score=fundamentacion)
    return len(pendientes)


if __name__ == "__main__":
    n = run()
    print(f"{n} interacciones evaluadas.")
