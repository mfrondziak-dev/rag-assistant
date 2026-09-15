from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rag.config import Settings  # noqa: E402
from rag.diagnostics import Status, run_diagnostics, try_start_ollama  # noqa: E402
from rag.factory import build_pipeline  # noqa: E402
from rag.i18n import LANGUAGES, translate  # noqa: E402
from rag.ingest import ingest  # noqa: E402
from rag.ollama_client import OllamaClient  # noqa: E402
from rag.simple import (  # noqa: E402
    SIMPLE_INDEX_DIR,
    UPLOADS_DIR,
    clear_uploads,
    list_uploads,
    save_upload,
)
from rag.store import VectorStore  # noqa: E402
from rag.text import SUPPORTED_SUFFIXES  # noqa: E402

st.set_page_config(page_title="Ask your documents", page_icon="📄", layout="wide")

st.session_state.setdefault("lang", "pl")
st.session_state.setdefault("messages", [])
st.session_state.setdefault("needs_index", False)

BLOCKING_KEYS = {"diag_ollama_installed", "diag_ollama_running", "diag_models"}
ICONS = {Status.OK: "✅", Status.WARN: "⚠️", Status.FAIL: "❌"}


def t(key: str, **fields: object) -> str:
    return translate(st.session_state.lang, key, **fields)


@st.cache_resource(show_spinner=False)
def get_pipeline(index_dir: str, index_mtime: float, top_k: int, mmr: float, rerank: bool):
    settings = Settings()
    settings.index_dir = Path(index_dir)
    settings.top_k = top_k
    settings.mmr_lambda = mmr
    settings.rerank = rerank
    store = VectorStore.load(settings.index_dir)
    return build_pipeline(settings, store)


def render_checklist(checks) -> None:
    for check in checks:
        line = f"{ICONS[check.status]} {t(check.key)}"
        if check.detail:
            line += f" — `{check.detail}`"
        st.markdown(line)


def render_advice(check, ollama_running: bool) -> None:
    if check.status is Status.OK:
        return
    if check.key == "diag_ollama_installed":
        st.write(t("diag_fix_ollama_install"))
    elif check.key == "diag_ollama_running":
        st.write(t("diag_fix_ollama_start"))
    elif check.key == "diag_models":
        if not ollama_running:
            return
        st.write(t("diag_fix_models"))
        st.code("\n".join(f"ollama pull {m.strip()}" for m in check.detail.split(",")))
    elif check.key == "diag_documents":
        st.write(t("diag_fix_documents"))
    elif check.key == "diag_index":
        st.write(t("diag_fix_index"))


settings = Settings()
settings.index_dir = SIMPLE_INDEX_DIR
client = OllamaClient(settings.ollama_host, timeout=settings.request_timeout)
diagnostics = run_diagnostics(settings, client)

with st.sidebar:
    codes = list(LANGUAGES)
    labels = [LANGUAGES[code] for code in codes]
    current = codes.index(st.session_state.lang)
    chosen = st.selectbox(t("language"), labels, index=current)
    new_lang = codes[labels.index(chosen)]
    if new_lang != st.session_state.lang:
        st.session_state.lang = new_lang
        st.rerun()

    with st.expander(t("advanced")):
        top_k = st.slider(t("top_k"), 1, 10, 5)
        mmr = st.slider(t("mmr"), 0.0, 1.0, 0.5, 0.1)
        rerank = st.toggle(t("rerank"), value=False)

    with st.expander(t("diag_title"), expanded=False):
        render_checklist(diagnostics)
        if st.button(t("diag_check_again"), key="diag_sidebar"):
            st.rerun()

st.title("📄 " + t("app_title"))
st.caption(t("app_subtitle"))

blocking = [c for c in diagnostics if c.key in BLOCKING_KEYS and c.status is not Status.OK]
if blocking:
    with st.container(border=True):
        installed = next(c for c in diagnostics if c.key == "diag_ollama_installed")
        running = next(c for c in diagnostics if c.key == "diag_ollama_running")
        ollama_running = running.status is Status.OK

        st.error("⚠️ " + t("diag_title"))
        render_checklist(diagnostics)
        for check in diagnostics:
            render_advice(check, ollama_running)

        columns = st.columns(2)
        with columns[0]:
            if installed.status is Status.OK and running.status is not Status.OK:
                if st.button(t("diag_start_ollama"), type="primary", use_container_width=True):
                    with st.spinner(t("diag_starting_ollama")):
                        try_start_ollama(client)
                    st.rerun()
        with columns[1]:
            if st.button(t("diag_check_again"), key="diag_panel", use_container_width=True):
                st.rerun()
    st.stop()

st.divider()
st.subheader(t("docs_heading"))

uploaded = st.file_uploader(
    t("upload_label"),
    type=sorted(suffix.lstrip(".") for suffix in SUPPORTED_SUFFIXES),
    accept_multiple_files=True,
    help=t("upload_help"),
)
if uploaded:
    for item in uploaded:
        save_upload(UPLOADS_DIR, item.name, item.getvalue())
    st.session_state.needs_index = True

files = list_uploads(UPLOADS_DIR)
if files:
    st.write(t("docs_present", count=len(files)))
    with st.expander("📎", expanded=False):
        for path in files:
            st.write(f"- {path.name}")
else:
    st.info(t("docs_none"))

if st.session_state.needs_index and files:
    st.info(t("needs_index"))

left, right = st.columns([1, 1])
with left:
    if st.button(t("index_button"), type="primary", disabled=not files, use_container_width=True):
        with st.spinner(t("indexing")):
            store = ingest(settings, UPLOADS_DIR)
        st.session_state.needs_index = False
        st.session_state.messages = []
        st.success(t("indexed_ok", chunks=len(store), files=len(files)))
with right:
    if st.button(t("clear_docs_button"), disabled=not files, use_container_width=True):
        clear_uploads(UPLOADS_DIR)
        st.session_state.messages = []
        st.session_state.needs_index = False
        st.rerun()

st.divider()
st.subheader(t("ask_heading"))

vectors_path = SIMPLE_INDEX_DIR / "vectors.npy"
if not vectors_path.exists():
    st.info(t("no_docs_info"))
else:
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
            if message.get("citations"):
                with st.expander(t("sources")):
                    for citation in message["citations"]:
                        st.markdown(
                            f"**[{citation['index']}]** `{Path(citation['source']).name}` "
                            f"— {t('score')} {citation['score']:.2f}"
                        )
                        st.caption(citation["snippet"])

    question = st.chat_input(t("ask_placeholder"))
    if question:
        st.session_state.messages.append({"role": "user", "content": question})
        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner(t("thinking")):
                try:
                    pipeline = get_pipeline(
                        str(SIMPLE_INDEX_DIR),
                        vectors_path.stat().st_mtime,
                        top_k,
                        mmr,
                        rerank,
                    )
                    result = pipeline.answer(question)
                    answer = result.answer
                    citations = [citation.__dict__ for citation in result.citations]
                except Exception:
                    answer = t("error_answer")
                    citations = []
            st.markdown(answer)
            if citations:
                with st.expander(t("sources")):
                    for citation in citations:
                        st.markdown(
                            f"**[{citation['index']}]** `{Path(citation['source']).name}` "
                            f"— {t('score')} {citation['score']:.2f}"
                        )
                        st.caption(citation["snippet"])

        st.session_state.messages.append(
            {"role": "assistant", "content": answer, "citations": citations}
        )
