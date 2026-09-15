from __future__ import annotations

import numpy as np
import requests


class OllamaError(RuntimeError):
    pass


class OllamaClient:
    def __init__(self, host: str = "http://localhost:11434", timeout: float = 120.0) -> None:
        self.host = host.rstrip("/")
        self.timeout = timeout
        self._session = requests.Session()

    def _post(self, path: str, payload: dict) -> dict:
        url = f"{self.host}{path}"
        try:
            response = self._session.post(url, json=payload, timeout=self.timeout)
        except requests.RequestException as exc:
            raise OllamaError(f"Cannot reach Ollama at {self.host}: {exc}") from exc
        if response.status_code >= 400:
            raise OllamaError(f"Ollama {path} returned {response.status_code}: {response.text[:300]}")
        return response.json()

    def health(self) -> bool:
        try:
            response = self._session.get(f"{self.host}/api/tags", timeout=5)
            return response.status_code == 200
        except requests.RequestException:
            return False

    def list_models(self) -> list[str]:
        response = self._session.get(f"{self.host}/api/tags", timeout=self.timeout)
        response.raise_for_status()
        return [m["name"] for m in response.json().get("models", [])]

    def embed(self, texts: list[str], model: str) -> np.ndarray:
        if not texts:
            return np.zeros((0, 0), dtype=np.float32)
        try:
            data = self._post("/api/embed", {"model": model, "input": texts})
            vectors = data.get("embeddings")
        except OllamaError:
            vectors = None
        if vectors is None:
            vectors = [self._embed_single(text, model) for text in texts]
        array = np.asarray(vectors, dtype=np.float32)
        if array.ndim != 2:
            raise OllamaError("Ollama returned embeddings with unexpected shape")
        return array

    def _embed_single(self, text: str, model: str) -> list[float]:
        data = self._post("/api/embeddings", {"model": model, "prompt": text})
        embedding = data.get("embedding")
        if embedding is None:
            raise OllamaError("Ollama returned no embedding")
        return embedding

    def chat(
        self,
        messages: list[dict[str, str]],
        model: str,
        temperature: float = 0.1,
        num_ctx: int = 8192,
    ) -> str:
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {"temperature": temperature, "num_ctx": num_ctx},
        }
        data = self._post("/api/chat", payload)
        message = data.get("message") or {}
        content = message.get("content")
        if content is None:
            raise OllamaError("Ollama returned an empty chat response")
        return content.strip()


class OllamaEmbedder:
    def __init__(self, client: OllamaClient, model: str) -> None:
        self._client = client
        self._model = model

    def embed(self, texts: list[str]) -> np.ndarray:
        return self._client.embed(texts, self._model)


class OllamaLLM:
    def __init__(self, client: OllamaClient, model: str, temperature: float = 0.1) -> None:
        self._client = client
        self._model = model
        self._temperature = temperature

    def chat(self, messages: list[dict[str, str]], **options: object) -> str:
        temperature = float(options.pop("temperature", self._temperature))
        num_ctx = int(options.pop("num_ctx", 8192))
        return self._client.chat(messages, self._model, temperature=temperature, num_ctx=num_ctx)
