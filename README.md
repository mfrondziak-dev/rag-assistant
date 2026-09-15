# Local RAG Assistant

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
   prompt with numbered context  ──►  Ollama chat (e.g. llama3.1)
                        │
                        ▼
            answer + sources with citations [1][2]
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
- **Testability** — the retriever, store and pipeline depend on `Embedder`/`LLM` protocols,
  so the whole stack is unit-tested offline with fakes (no network, no Ollama in CI).

## Stack

| Concern      | Choice                                                            |
|--------------|-------------------------------------------------------------------|
| Embeddings   | Ollama `nomic-embed-text` (swappable)                             |
| Generation   | Ollama `llama3.1` (any chat model works)                          |
| Vector store | Custom NumPy cosine index persisted to `.npy` + `.jsonl`          |
| Retrieval    | top-k cosine + optional MMR (`mmr_lambda`)                        |
| CLI          | `argparse`                                                        |
| UI           | Streamlit (optional)                                              |
| Tests        | pytest (offline, dependency-injected fakes)                       |

The only hard dependencies are `requests` and `numpy`. `pypdf` (PDF) and `streamlit` (UI)
are optional extras.

## Quickstart

```bash
# 1. Ollama with the required models
ollama pull nomic-embed-text
ollama pull llama3.1

# 2. Install
python3 -m venv --system-site-packages .venv
source .venv/bin/activate
pip install -r requirements.txt

# 3. Put your documents in data/raw (md, txt, rst, pdf)

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
> judge step exists. Try `--judge` and a larger chat model to see the difference.

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
│   ├── retriever.py      # top-k + MMR
│   ├── pipeline.py       # prompt construction, citations, refusal
│   ├── evaluate.py       # retrieval metrics + LLM-as-judge
│   ├── ingest.py         # build the index
│   ├── factory.py        # wire components from Settings
│   └── cli.py            # ingest / ask / eval / models / serve
├── app/streamlit_app.py  # optional UI
├── data/raw/             # sample documents (fictional "Aurora Cloud")
├── data/eval/            # labelled evaluation set
└── tests/                # offline unit tests
```

## Testing

```bash
make test      # 19 tests, no network required
```

## License

MIT
