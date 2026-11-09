from fastapi import FastAPI
from pydantic import BaseModel
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from agent_app.agent import app as agent
import uuid

app = FastAPI()


class Message(BaseModel):
    role: str  # "user" | "assistant" | "system"
    content: str


class ChatRequest(BaseModel):
    model: str
    conversation: list[Message]
    question: str


class ChatResponse(BaseModel):
    answer: str
    prompt_tokens: int
    completion_tokens: int
    is_offensive: bool
    is_prompt_injection: bool
    is_off_topic: bool
    is_academic_dishonesty: bool
    is_pii: bool
    blocked: bool


def to_lc_message(m: Message):
    if m.role == "assistant":
        return AIMessage(content=m.content)
    if m.role == "system":
        return SystemMessage(content=m.content)
    return HumanMessage(content=m.content)


@app.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    config = {
        "configurable": {
            "thread_id": str(uuid.uuid4()),
            "model": request.model,
        }
    }

    messages = [to_lc_message(m) for m in request.conversation]
    messages.append(HumanMessage(content=request.question))

    result = agent.invoke({"messages": messages}, config=config)

    answer = result["messages"][-1].content

    is_offensive = bool(result.get("is_offensive", False))
    is_prompt_injection = bool(result.get("is_prompt_injection", False))
    is_off_topic = bool(result.get("is_off_topic", False))
    is_academic_dishonesty = bool(result.get("is_academic_dishonesty", False))
    is_pii = bool(result.get("is_pii", False))
    blocked = (
        is_offensive
        or is_prompt_injection
        or is_off_topic
        or is_academic_dishonesty
        or is_pii
    )

    prompt_tokens = 0
    completion_tokens = 0
    for msg in result["messages"]:
        usage = getattr(msg, "usage_metadata", None)
        if usage:
            prompt_tokens += usage.get("input_tokens", 0)
            completion_tokens += usage.get("output_tokens", 0)

    return ChatResponse(
        answer=answer,
        prompt_tokens=prompt_tokens,
        completion_tokens=completion_tokens,
        is_offensive=is_offensive,
        is_prompt_injection=is_prompt_injection,
        is_off_topic=is_off_topic,
        is_academic_dishonesty=is_academic_dishonesty,
        is_pii=is_pii,
        blocked=blocked,
    )