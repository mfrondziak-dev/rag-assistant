# Local RAG Assistant

[![CI](https://github.com/mfrondziak-dev/rag-assistant/actions/workflows/ci.yml/badge.svg)](https://github.com/mfrondziak-dev/rag-assistant/actions/workflows/ci.yml)

A small, dependency-light **retrieval-augmented generation (RAG)** system that runs entirely
on your machine. It indexes your own documents, retrieves the most relevant passages, and
answers questions with **inline citations** — plus a built-in **evaluation harness** for both
retrieval quality and answer grounding.

No API keys, no cloud, no vendor lock-in: embeddings and generation are served locally by
[Ollama](https://ollama.com).

```
             data/raw/*.md | *.txt | *.pdf
                        │  load + chunk (overlap)
                        ▼
     embeddings (Ollama, e.g. nomic-embed-text)
                        │
                        ▼
        vector store (NumPy, cosine, persisted)
                        │  retrieve: top-k + MMR diversity
                        ▼
              optional LLM reranker (relevance judge)
                        │
                        ▼
   prompt with numbered context  ──►  Ollama chat (e.g. llama3.1)
                        │
                        ▼
            answer + sources with citations [1][2]

        exposed through a CLI, a Streamlit UI and a FastAPI service
```

## Why this project

Most "chat with your PDF" demos stop at `chain = RetrievalQA(...)`. This one focuses on the
parts that actually matter in production:

- **Citations** — every answer points back to the source chunk it came from.
- **Refusal** — if retrieval finds nothing relevant, the model says so instead of guessing.
- **Evaluation** — retrieval is measured (hit-rate, recall, MRR) and answers are scored for
  grounding with an LLM-as-judge.
- **MMR retrieval** — optional maximal marginal relevance to trade relevance for diversity
  and avoid five copies of the same paragraph.
- **Optional LLM reranker** — a second-stage relevance judge that reorders candidates and
  measurably improves answer grounding (see the evaluation note below).
- **HTTP API** — a FastAPI service (`GET /health`, `POST /search`, `POST /ask`) with
  dependency-injected, offline-testable endpoints.
- **Easy mode** — a bilingual (PL/EN) browser app for non-technical users: drag in files,
  click, ask. Launched with one command or from the application menu.
- **Multiple formats** — Markdown, text, reStructuredText, PDF and DOCX.
- **Testability** — the retriever, store and pipeline depend on `Embedder`/`LLM` protocols,
  so the whole stack is unit-tested offline with fakes (no network, no Ollama in CI).

## Stack

| Concern      | Choice                                                            |
|--------------|-------------------------------------------------------------------|
| Embeddings   | Ollama `nomic-embed-text` (swappable)                             |
| Generation   | Ollama `llama3.1` (any chat model works)                          |
| Vector store | Custom NumPy cosine index persisted to `.npy` + `.jsonl`          |
| Retrieval    | top-k cosine + optional MMR (`mmr_lambda`)                        |
| Reranking    | optional LLM-as-relevance-judge (`LLMReranker`)                   |
| CLI          | `argparse`                                                        |
| UI           | Streamlit (optional)                                              |
| API          | FastAPI + Uvicorn (optional)                                      |
| Tests        | pytest (offline, dependency-injected fakes)                       |

The hard dependencies are `requests` and `numpy`. `pypdf` (PDF), `python-docx` (DOCX),
`streamlit` (UI) and `fastapi`/`uvicorn` (API) are optional extras.

## Quickstart

```bash
# 1. Ollama with the required models
ollama pull nomic-embed-text
ollama pull llama3.1

# 2. Install
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Put your documents in data/raw (md, txt, rst, pdf, docx).
#    Keep private files in data/raw/private/ (gitignored).

# 4. Build the index
make ingest

# 5. Ask
make ask Q="How much does the Team plan cost per month?"

# 6. Evaluate
make eval
```

Streamlit UI:

```bash
make serve        # http://localhost:8501
```

HTTP API:

```bash
make api          # http://localhost:8000

curl localhost:8000/health
curl -X POST localhost:8000/ask \
  -H 'Content-Type: application/json' \
  -d '{"question": "What encryption is used for data at rest?"}'
curl -X POST localhost:8000/search \
  -H 'Content-Type: application/json' \
  -d '{"question": "pricing", "top_k": 3}'
```

Enable the LLM reranker for any command with `RERANK=1` (or `--rerank`):

```bash
RERANK=1 make ask Q="Do discounts stack with promotional credits?"
```

## Easy mode (for non-technical users)

A friendly, bilingual (PL/EN) browser app: drag in documents **or point at a folder** on your
computer (with a native **folder picker** button), click *Add to the library*, and ask
questions. No terminal, no commands. It shows a **progress bar** while indexing, **skips
unreadable files** instead of failing, **suggests follow-up questions**, and includes a
built-in **troubleshooting panel** that checks Ollama, the models, your documents and the
index, and can start Ollama for you.

```bash
make easy        # or: ./start.sh
```

`start.sh` creates the environment, starts Ollama if needed, downloads the missing models
once, and opens the app. To launch it from the application menu with a single click:

```bash
make desktop     # or: bash scripts/install-desktop.sh
```

See [`docs/EASY_MODE.md`](docs/EASY_MODE.md) for the full walkthrough.

## Configuration

All settings come from environment variables (see `.env.example`):

| Variable        | Default                  | Meaning                          |
|-----------------|--------------------------|----------------------------------|
| `OLLAMA_HOST`   | `http://localhost:11434` | Ollama endpoint                  |
| `EMBED_MODEL`   | `nomic-embed-text`       | Embedding model                  |
| `CHAT_MODEL`    | `llama3.1`               | Generation model                 |
| `CHUNK_SIZE`    | `900`                    | Max characters per chunk         |
| `CHUNK_OVERLAP` | `150`                    | Overlap between chunks           |
| `TOP_K`         | `5`                      | Retrieved chunks per question    |
| `MMR_LAMBDA`    | `0.5`                    | 1.0 = relevance, 0.0 = diversity |
| `RERANK`        | `0`                      | Enable the LLM reranker (0/1)    |
| `RERANK_CANDIDATES` | `20`                 | Candidates retrieved before rerank |
| `FOLLOWUPS`     | `3`                      | Suggested follow-up questions (0 disables) |

## Evaluation

`data/eval/questions.jsonl` labels each question with the source file that should be
retrieved. The harness reports:

```
Retrieval @ k=5 on 8 questions
  hit-rate : 1.000
  recall   : 1.000
  MRR      : 1.000
```

With `--judge` it also asks the LLM whether each produced answer is grounded in the
retrieved context and averages the result.

> **A finding, not a caveat.** On the sample corpus, retrieval is perfect, yet a small 8B
> model still stated that discounts "stack" when the document says the opposite. Retrieval
> quality and answer faithfulness are *different* problems — which is exactly why the
> judge step exists. Turning on the reranker (`RERANK=1`) pulls the exact clause to the top
> and the same model then answers correctly ("Discounts do not stack with promotional
> credits"). That before/after is the point: measure, then improve the right stage.

## Project layout

```
rag-assistant/
├── src/rag/
│   ├── config.py         # Settings from env
│   ├── models.py         # Document, SearchResult, Citation, RAGAnswer
│   ├── interfaces.py     # Embedder / LLM protocols (for testability)
│   ├── text.py           # loading + sentence-aware chunking
│   ├── ollama_client.py  # embeddings + chat (batch with fallback)
│   ├── store.py          # NumPy vector store with persistence
│   ├── retriever.py      # top-k + MMR (+ optional reranker)
│   ├── rerank.py         # LLM-as-relevance-judge reranker
│   ├── pipeline.py       # prompt construction, citations, refusal
│   ├── evaluate.py       # retrieval metrics + LLM-as-judge
│   ├── ingest.py         # build the index
│   ├── factory.py        # wire components from Settings
│   ├── api.py            # FastAPI service (/health, /search, /ask)
│   ├── i18n.py           # PL/EN strings for the easy-mode UI
│   ├── simple.py         # safe upload storage + library helpers
│   └── cli.py            # ingest / ask / eval / models / serve / api
├── app/
│   ├── streamlit_app.py  # technical UI (sliders, context)
│   └── simple_app.py     # bilingual easy-mode UI (upload + chat)
├── start.sh              # one-command launcher
├── rag.sh                # CLI wrapper that works from any directory
├── scripts/              # install-desktop.sh (menu shortcut)
├── data/raw/             # sample documents (fictional "Aurora Cloud")
│   └── private/          # your own documents (gitignored)
├── data/uploads/         # easy-mode uploads (gitignored)
├── data/eval/            # labelled evaluation set
└── tests/                # offline unit tests
```

## Testing

```bash
make test      # 74 tests, no network required
```

For a hands-on end-to-end walkthrough (CLI, reranker comparison, evaluation, API, UI and
using your own documents), see [`docs/TESTING.md`](docs/TESTING.md).

## License

MIT
