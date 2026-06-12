from typing import Any

import requests

from app.config import (
    OLLAMA_BASE_URL,
    OLLAMA_CHAT_MODEL,
    OLLAMA_EMBED_MODEL,
)


class OllamaError(RuntimeError):
    pass


def _post_json(endpoint: str, payload: dict[str, Any], timeout: int = 180) -> dict[str, Any]:
    url = f"{OLLAMA_BASE_URL}{endpoint}"

    try:
        response = requests.post(url, json=payload, timeout=timeout)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.ConnectionError as exc:
        raise OllamaError(
            "Could not connect to Ollama. Make sure Ollama is running on http://localhost:11434."
        ) from exc
    except requests.exceptions.HTTPError as exc:
        raise OllamaError(f"Ollama HTTP error: {response.text}") from exc
    except requests.exceptions.Timeout as exc:
        raise OllamaError("Ollama request timed out.") from exc


def embed_texts(texts: list[str]) -> list[list[float]]:
    payload = {
        "model": OLLAMA_EMBED_MODEL,
        "input": texts,
    }

    data = _post_json("/api/embed", payload)

    embeddings = data.get("embeddings")

    if not embeddings:
        raise OllamaError(f"No embeddings returned by Ollama. Response: {data}")

    return embeddings


def chat(messages: list[dict[str, str]], temperature: float = 0.1) -> str:
    payload = {
        "model": OLLAMA_CHAT_MODEL,
        "messages": messages,
        "stream": False,
        "options": {
            "temperature": temperature,
        },
    }

    data = _post_json("/api/chat", payload)

    try:
        return data["message"]["content"]
    except KeyError as exc:
        raise OllamaError(f"Unexpected Ollama chat response: {data}") from exc