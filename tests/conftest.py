import numpy as np
import pytest


class KeywordEmbedder:
    def __init__(self, keywords):
        self.keywords = [k.lower() for k in keywords]

    def embed(self, texts):
        matrix = np.zeros((len(texts), len(self.keywords)), dtype=np.float32)
        for row, text in enumerate(texts):
            lowered = text.lower()
            for col, keyword in enumerate(self.keywords):
                if keyword in lowered:
                    matrix[row, col] = 1.0
        return matrix


class FakeLLM:
    def __init__(self, reply="Grounded answer [1]."):
        self.reply = reply
        self.calls = []

    def chat(self, messages, **options):
        self.calls.append(messages)
        return self.reply


@pytest.fixture
def make_embedder():
    return KeywordEmbedder


@pytest.fixture
def make_llm():
    return FakeLLM
