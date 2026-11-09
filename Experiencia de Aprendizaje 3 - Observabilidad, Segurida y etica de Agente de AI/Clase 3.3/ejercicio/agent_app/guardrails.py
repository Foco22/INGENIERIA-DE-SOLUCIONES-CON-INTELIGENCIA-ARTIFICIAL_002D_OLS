import os
from concurrent.futures import ThreadPoolExecutor
from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from agent_app.prompts import (
    OFFENSIVE_GUARDRAIL_PROMPT,
    PROMPT_INJECTION_GUARDRAIL_PROMPT,
    OFF_TOPIC_GUARDRAIL_PROMPT,
    ACADEMIC_DISHONESTY_GUARDRAIL_PROMPT,
    PII_GUARDRAIL_PROMPT,
)


def _evaluate(prompt: str, message: str, model: str) -> bool:
    """Call the LLM with a guardrail prompt and return True/False."""
    llm = ChatOpenAI(
        model=model,
        temperature=0,
        api_key=os.getenv("OPENAI_API_KEY"),
        base_url="https://api.openai.com/v1",
    )
    result = llm.invoke([
        SystemMessage(content=prompt),
        HumanMessage(content=message),
    ])
    return result.content.strip().lower() == "true"


def run_guardrails(message: str, model: str) -> dict:
    """
    Run all 5 guardrail evaluators in parallel using threads.

    Returns:
        {
            "is_offensive": bool,
            "is_prompt_injection": bool,
            "is_off_topic": bool,
            "is_academic_dishonesty": bool,
            "is_pii": bool,
        }
    """
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_offensive = executor.submit(
            _evaluate, OFFENSIVE_GUARDRAIL_PROMPT, message, model
        )
        future_injection = executor.submit(
            _evaluate, PROMPT_INJECTION_GUARDRAIL_PROMPT, message, model
        )
        future_off_topic = executor.submit(
            _evaluate, OFF_TOPIC_GUARDRAIL_PROMPT, message, model
        )

        future_dishonesty = executor.submit(
            _evaluate, ACADEMIC_DISHONESTY_GUARDRAIL_PROMPT, message, model
        )
        future_pii = executor.submit(
            _evaluate, PII_GUARDRAIL_PROMPT, message, model
        )

        is_offensive = future_offensive.result()
        is_prompt_injection = future_injection.result()
        is_off_topic = future_off_topic.result()
        is_academic_dishonesty = future_dishonesty.result()
        is_pii = future_pii.result()

    return {
        "is_offensive": is_offensive,
        "is_prompt_injection": is_prompt_injection,
        "is_off_topic": is_off_topic,
        "is_academic_dishonesty": is_academic_dishonesty,
        "is_pii": is_pii,
    }