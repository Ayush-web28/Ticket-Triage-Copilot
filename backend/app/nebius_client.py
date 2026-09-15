"""Thin wrapper around the Nebius Token Factory OpenAI-compatible API."""
import json
import time
from functools import lru_cache

from openai import OpenAI

from .config import settings


@lru_cache
def get_client() -> OpenAI:
    return OpenAI(base_url=settings.nebius_base_url, api_key=settings.nebius_api_key)


def chat(model: str, system: str, user: str, temperature: float = 0.2, json_mode: bool = False) -> tuple[str, int]:
    """Returns (content, latency_ms)."""
    client = get_client()
    kwargs = {}
    if json_mode:
        kwargs["response_format"] = {"type": "json_object"}

    start = time.perf_counter()
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        temperature=temperature,
        **kwargs,
    )
    latency_ms = int((time.perf_counter() - start) * 1000)
    return response.choices[0].message.content or "", latency_ms


def chat_json(model: str, system: str, user: str, temperature: float = 0.2) -> tuple[dict, int]:
    content, latency_ms = chat(model, system, user, temperature=temperature, json_mode=True)
    try:
        return json.loads(content), latency_ms
    except json.JSONDecodeError:
        start = content.find("{")
        end = content.rfind("}")
        if start != -1 and end != -1:
            try:
                return json.loads(content[start : end + 1]), latency_ms
            except json.JSONDecodeError:
                pass
        raise ValueError(f"Model did not return valid JSON: {content[:200]!r}")


def embed(texts: list[str], model: str | None = None) -> list[list[float]]:
    client = get_client()
    response = client.embeddings.create(model=model or settings.model_embedding, input=texts)
    return [item.embedding for item in response.data]
