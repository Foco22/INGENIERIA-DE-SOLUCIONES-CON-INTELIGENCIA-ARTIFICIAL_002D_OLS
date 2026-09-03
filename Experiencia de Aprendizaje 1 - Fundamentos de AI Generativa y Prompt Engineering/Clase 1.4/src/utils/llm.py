import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()


class OpenAILLM:
    def __init__(self, model: str = "gpt-4o-mini"):
        self.model = model
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    def generate(self, system_prompt: str, history: list[dict]) -> dict:
        messages = [{"role": "system", "content": system_prompt}] + history
        response = self.client.chat.completions.create(
            model=self.model,
            messages=messages
        )
        return {
            "answer": response.choices[0].message.content,
            "prompt_tokens": response.usage.prompt_tokens,
            "completion_tokens": response.usage.completion_tokens,
            "total_tokens": response.usage.total_tokens,
        }

