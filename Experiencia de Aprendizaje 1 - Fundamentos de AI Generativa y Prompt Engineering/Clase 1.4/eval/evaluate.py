import asyncio
import json
import os
import sys
import time
import warnings
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv  # noqa: E402
from openai import AsyncOpenAI  # noqa: E402
from ragas.llms import llm_factory  # noqa: E402
from ragas.embeddings import OpenAIEmbeddings  # noqa: E402
from ragas.metrics.collections import Faithfulness, AnswerRelevancy, ContextPrecision, ContextRecall  # noqa: E402
from prompts.prompt import RAG_SYSTEM_PROMPT  # noqa: E402
from src.generate.generate import RAGGenerator  # noqa: E402

load_dotenv()

DATASET_PATH = os.path.join(os.path.dirname(__file__), "dataset.json")
TOP_K = 5
# Preguntas evaluadas en paralelo. Cada pregunta dispara ~13 llamadas a OpenAI,
# asi que subirlo mucho puede topar con el rate limit de la cuenta.
MAX_CONCURRENT_QUESTIONS = 4


async def evaluate_item(item: dict, rag: RAGGenerator, metrics: dict, semaphore: asyncio.Semaphore) -> dict:
    async with semaphore:
        query = item["question"]
        ground_truth = item["ground_truth"]

        # Un solo retrieve por pregunta: los mismos chunks alimentan la respuesta
        # y las metricas de contexto.
        chunks = await asyncio.to_thread(rag.retriever.retrieve, query, TOP_K)
        context_texts = [chunk["text"] for chunk in chunks]

        # context_precision y context_recall solo dependen del retrieve, no de la
        # respuesta: se lanzan ya y corren mientras el LLM genera.
        pending = {
            "context_precision": asyncio.create_task(metrics["context_precision"].ascore(
                user_input=query, reference=ground_truth, retrieved_contexts=context_texts)),
            "context_recall": asyncio.create_task(metrics["context_recall"].ascore(
                user_input=query, retrieved_contexts=context_texts, reference=ground_truth)),
        }

        response = await asyncio.to_thread(rag.generate, query, [], TOP_K, chunks)
        answer = response["answer"]

        # Las que si necesitan la respuesta, en paralelo con las anteriores.
        pending["faithfulness"] = asyncio.create_task(metrics["faithfulness"].ascore(
            user_input=query, response=answer, retrieved_contexts=context_texts))
        pending["answer_relevancy"] = asyncio.create_task(metrics["answer_relevancy"].ascore(
            user_input=query, response=answer))

        names = list(pending)
        outcomes = await asyncio.gather(*pending.values(), return_exceptions=True)

        scores = {}
        for name, outcome in zip(names, outcomes):
            if isinstance(outcome, BaseException):
                scores[name] = f"error: {outcome}"
            else:
                scores[name] = round(outcome.value, 3)

        # Orden estable para el resumen, independiente de como terminaron las tareas.
        scores = {name: scores[name] for name in metrics}

        return {"question": query, "answer": answer, "scores": scores}


async def run_evaluation_async() -> list[dict]:
    started = time.perf_counter()

    with open(DATASET_PATH, "r", encoding="utf-8") as f:
        dataset = json.load(f)

    rag = RAGGenerator(system_prompt=RAG_SYSTEM_PROMPT)

    openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
    llm = llm_factory("gpt-4o-mini", client=openai_client)
    embeddings = OpenAIEmbeddings(model="text-embedding-3-small", client=openai_client)

    metrics = {
        "faithfulness": Faithfulness(llm=llm),
        "answer_relevancy": AnswerRelevancy(llm=llm, embeddings=embeddings),
        "context_precision": ContextPrecision(llm=llm),
        "context_recall": ContextRecall(llm=llm),
    }

    print(f"Running RAG + evaluation on {len(dataset)} questions "
          f"(hasta {MAX_CONCURRENT_QUESTIONS} en paralelo)...\n")

    semaphore = asyncio.Semaphore(MAX_CONCURRENT_QUESTIONS)
    results = await asyncio.gather(
        *[evaluate_item(item, rag, metrics, semaphore) for item in dataset]
    )

    for result in results:
        print(f"Q: {result['question'][:60]}")
        for k, v in result["scores"].items():
            print(f"  {k}: {v}")
        print()

    print("=== Summary ===")
    for metric_name in metrics:
        values = [r["scores"][metric_name] for r in results if isinstance(r["scores"][metric_name], float)]
        if values:
            print(f"{metric_name}: {round(sum(values)/len(values), 3)}")

    print(f"\nTiempo total: {time.perf_counter() - started:.2f}s")

    return results


def run_evaluation() -> list[dict]:
    """Punto de entrada sincrono (CLI y boton de Streamlit)."""
    try:
        asyncio.get_running_loop()
    except RuntimeError:
        loop_activo = False
    else:
        loop_activo = True

    if loop_activo:
        # Ya hay un event loop corriendo en este hilo (Streamlit / Jupyter):
        # asyncio.run() fallaria, asi que la evaluacion corre en otro hilo.
        with ThreadPoolExecutor(max_workers=1) as pool:
            return pool.submit(asyncio.run, run_evaluation_async()).result()

    # Streamlit deja un loop asociado al hilo aunque no este corriendo, y
    # asyncio.run() lo dejaria en None al terminar: lo guardamos y restauramos.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", DeprecationWarning)
        try:
            loop_previo = asyncio.get_event_loop_policy().get_event_loop()
        except RuntimeError:
            loop_previo = None

    try:
        return asyncio.run(run_evaluation_async())
    finally:
        if loop_previo is not None and not loop_previo.is_closed():
            asyncio.set_event_loop(loop_previo)


if __name__ == "__main__":
    run_evaluation()
