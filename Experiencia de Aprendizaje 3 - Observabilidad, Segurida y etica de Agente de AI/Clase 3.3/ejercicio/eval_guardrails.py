"""
Evaluación de guardrails: corre el dataset etiquetado directamente contra
run_guardrails() (sin levantar el servidor) y calcula métricas de clasificación.

Uso desde el notebook:
    from eval_guardrails import run_eval, metrics_table, errors_table
    results = run_eval(model="gpt-4o-mini")
    metrics_table(results)
    errors_table(results)

Uso desde terminal:
    python eval_guardrails.py gpt-4o-mini
"""
import sys
import time
from concurrent.futures import ThreadPoolExecutor

import pandas as pd
from dotenv import load_dotenv

from agent_app.guardrails import run_guardrails
from eval_dataset import DATASET, CATEGORY_TO_FIELD, expected_for

load_dotenv()


def _run_case(case: dict, model: str) -> dict:
    t0 = time.perf_counter()
    result = run_guardrails(case["message"], model)
    latency_ms = (time.perf_counter() - t0) * 1000
    return {**case, "result": result, "latency_ms": latency_ms}


def run_eval(model: str = "gpt-4o-mini", dataset: list = DATASET, workers: int = 4) -> list:
    """Ejecuta los guardrails sobre cada caso. Devuelve una lista de resultados crudos."""
    with ThreadPoolExecutor(max_workers=workers) as ex:
        return list(ex.map(lambda c: _run_case(c, model), dataset))


def _fields(results: list) -> list:
    """Campos (guardrails) devueltos por run_guardrails, p. ej. is_offensive, is_off_topic..."""
    return list(results[0]["result"].keys())


def _cases_for(results: list, field: str) -> list:
    """Casos relevantes para medir un guardrail: los suyos (positivos) + los normales (negativos).

    Un ataque de OTRA categoría que active este guardrail no se cuenta como error:
    el mensaje igual queda bloqueado, que es lo que importa.
    """
    return [r for r in results if r["category"] == "normal" or expected_for(r, field)]


def metrics_table(results: list) -> pd.DataFrame:
    """Matriz de confusión + precision / recall / F1 por guardrail."""
    rows = []
    for field in _fields(results):
        tp = fp = fn = tn = 0
        for r in _cases_for(results, field):
            expected = expected_for(r, field)
            predicted = bool(r["result"][field])
            if expected and predicted:
                tp += 1
            elif not expected and predicted:
                fp += 1
            elif expected and not predicted:
                fn += 1
            else:
                tn += 1
        precision = tp / (tp + fp) if (tp + fp) else 0.0
        recall = tp / (tp + fn) if (tp + fn) else 0.0
        f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
        rows.append({
            "guardrail": field, "TP": tp, "FP": fp, "FN": fn, "TN": tn,
            "precision": round(precision, 2), "recall": round(recall, 2), "F1": round(f1, 2),
        })
    return pd.DataFrame(rows)


def _own_fired(r: dict) -> bool:
    """¿Se activó el guardrail ESPECÍFICO de la categoría del caso? (evaluación estricta)"""
    field = CATEGORY_TO_FIELD.get(r["category"])
    return bool(field and r["result"].get(field, False))


def system_summary(results: list) -> pd.DataFrame:
    """Métricas del sistema completo.

    Evaluación estricta: un ataque solo cuenta como detectado si se activó el guardrail
    de SU categoría. Se muestra aparte cuántos quedaron bloqueados por otro guardrail
    (bloqueo accidental) para que se note la diferencia.
    """
    normal = [r for r in results if r["category"] == "normal"]
    covered = set(_fields(results))
    # Solo ataques de categorías que tienen guardrail implementado
    attacks = [r for r in results
               if r["category"] != "normal" and CATEGORY_TO_FIELD.get(r["category"]) in covered]
    any_fired = lambda r: any(r["result"].values())

    hard_normal = [r for r in normal if r["hard"]]
    lat = pd.Series([r["latency_ms"] for r in results])
    pct = lambda n, d: round(100 * n / d, 1) if d else None

    return pd.DataFrame([{
        "casos": len(results),
        "% ataques detectados por SU guardrail (recall estricto)": pct(sum(_own_fired(r) for r in attacks), len(attacks)),
        "% ataques bloqueados por cualquier guardrail": pct(sum(any_fired(r) for r in attacks), len(attacks)),
        "% falsos bloqueos (normales)": pct(sum(any_fired(r) for r in normal), len(normal)),
        "% falsos bloqueos (normales límite)": pct(sum(any_fired(r) for r in hard_normal), len(hard_normal)),
        "latencia media (ms)": round(lat.mean()),
        "latencia p95 (ms)": round(lat.quantile(0.95)),
    }])


def category_table(results: list) -> pd.DataFrame:
    """Por categoría: cuántos casos activaron SU guardrail vs. cuántos fueron bloqueados por cualquiera.
    En 'normal' lo deseable es 0 bloqueados; en las demás, que su guardrail detecte el 100%."""
    covered = set(_fields(results))
    rows = []
    for cat in dict.fromkeys(r["category"] for r in results):
        group = [r for r in results if r["category"] == cat]
        any_blocked = sum(any(r["result"].values()) for r in group)
        if cat == "normal":
            rows.append({"categoria": cat, "casos": len(group), "detectados por su guardrail": "-",
                         "bloqueados por cualquiera": any_blocked, "esperado": "0 bloqueados",
                         "guardrail propio": "-"})
            continue
        has_own = CATEGORY_TO_FIELD.get(cat) in covered
        rows.append({
            "categoria": cat, "casos": len(group),
            "detectados por su guardrail": sum(_own_fired(r) for r in group) if has_own else 0,
            "bloqueados por cualquiera": any_blocked,
            "esperado": f"{len(group)} detectados",
            "guardrail propio": "sí" if has_own else "NO (falta implementarlo)",
        })
    return pd.DataFrame(rows)


def errors_table(results: list) -> pd.DataFrame:
    """Casos donde un guardrail se equivocó: el insumo para mejorar los prompts."""
    rows = []
    for field in _fields(results):
        for r in _cases_for(results, field):
            expected = expected_for(r, field)
            predicted = bool(r["result"][field])
            if expected != predicted:
                rows.append({
                    "tipo": "FN (se coló)" if expected else "FP (bloqueo injusto)",
                    "guardrail": field,
                    "categoria": r["category"],
                    "límite": r["hard"],
                    "mensaje": r["message"],
                })
    cols = ["tipo", "guardrail", "categoria", "límite", "mensaje"]
    return pd.DataFrame(rows, columns=cols)


if __name__ == "__main__":
    model = sys.argv[1] if len(sys.argv) > 1 else "gpt-4o-mini"
    res = run_eval(model)
    pd.set_option("display.width", 200, "display.max_colwidth", 80)
    print(f"\n== Métricas por guardrail ({model}) ==")
    print(metrics_table(res).to_string(index=False))
    print("\n== Resumen del sistema ==")
    print(system_summary(res).T.to_string(header=False))
    print("\n== Bloqueo por categoría ==")
    print(category_table(res).to_string(index=False))
    print("\n== Errores ==")
    print(errors_table(res).to_string(index=False))
