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


def _build_pdf(text: str) -> bytes:
    content = f"BT /F1 24 Tf 72 720 Td ({text}) Tj ET".encode("latin-1")
    objects = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 792] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(content)).encode() + b" >>\nstream\n" + content + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    out = bytearray(b"%PDF-1.4\n")
    offsets = []
    for index, obj in enumerate(objects, start=1):
        offsets.append(len(out))
        out += f"{index} 0 obj\n".encode() + obj + b"\nendobj\n"
    xref_position = len(out)
    out += f"xref\n0 {len(objects) + 1}\n".encode()
    out += b"0000000000 65535 f \n"
    for offset in offsets:
        out += f"{offset:010d} 00000 n \n".encode()
    out += (
        f"trailer\n<< /Size {len(objects) + 1} /Root 1 0 R >>\n"
        f"startxref\n{xref_position}\n%%EOF"
    ).encode()
    return bytes(out)


@pytest.fixture
def build_pdf():
    return _build_pdf
