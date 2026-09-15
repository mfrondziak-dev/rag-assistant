from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.config import Settings  # noqa: E402
from rag.factory import build_pipeline  # noqa: E402
from rag.store import VectorStore  # noqa: E402

st.set_page_config(page_title="Local RAG Assistant", page_icon="🔎", layout="wide")


@st.cache_resource(show_spinner=False)
def load_pipeline(index_dir: str, top_k: int, mmr_lambda: float):
    settings = Settings()
    settings.index_dir = Path(index_dir)
    settings.top_k = top_k
    settings.mmr_lambda = mmr_lambda
    store = VectorStore.load(settings.index_dir)
    return build_pipeline(settings, store)


st.title("🔎 Local RAG Assistant")
st.caption("Retrieval-augmented generation over your own documents. Runs fully on your machine via Ollama.")

with st.sidebar:
    st.header("Settings")
    index_dir = st.text_input("Index directory", value=str(ROOT / "data" / "index"))
    top_k = st.slider("Top-k chunks", 1, 10, 5)
    mmr_lambda = st.slider("MMR lambda (1.0 = relevance, 0.0 = diversity)", 0.0, 1.0, 0.5)
    show_context = st.toggle("Show retrieved context", value=True)

question = st.text_input("Ask a question about your documents", placeholder="e.g. What is the Team plan price?")

if question:
    try:
        pipeline = load_pipeline(index_dir, top_k, mmr_lambda)
    except FileNotFoundError as exc:
        st.error(str(exc))
        st.stop()

    with st.spinner("Thinking ..."):
        result = pipeline.answer(question, top_k=top_k)

    if result.used_context:
        st.success(result.answer)
    else:
        st.warning(result.answer)

    if result.citations:
        st.subheader("Sources")
        for citation in result.citations:
            with st.expander(f"[{citation.index}] {Path(citation.source).name}  ·  score {citation.score:.3f}"):
                st.write(citation.snippet)

    if show_context and result.contexts:
        st.subheader("Retrieved context")
        for i, context in enumerate(result.contexts, start=1):
            st.markdown(f"**[{i}]** `{Path(context.document.source).name}` — {context.score:.3f}")
            st.text(context.document.text)
