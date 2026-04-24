import os
import requests
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam
from dotenv import load_dotenv

load_dotenv()


def chat(messages: list[ChatCompletionMessageParam]) -> str:
    provider = os.getenv("AI_PROVIDER", "9router")

    if provider == "openai":
        client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        model = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        response = client.chat.completions.create(model=model, messages=messages)
        return response.choices[0].message.content or ""

    # 9router — dùng requests để handle wrapper response
    base_url = os.getenv("NINEROUTER_BASE_URL", "http://localhost:20128/v1")
    api_key = os.getenv("NINEROUTER_API_KEY", "")
    model = os.getenv("NINEROUTER_MODEL", "cx/gpt-5.2")

    res = requests.post(
        f"{base_url}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={"model": model, "messages": messages, "stream": False},
        timeout=30,
    )
    res.raise_for_status()
    data = res.json()
    choices = data.get("body", data).get("choices")
    if not choices:
        raise ValueError(f"Unexpected response format: {data}")
    return choices[0]["message"]["content"]
