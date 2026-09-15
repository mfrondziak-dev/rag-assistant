# Manual testing scenario

A step-by-step scenario to verify `rag-assistant` end to end on your own machine.
Expected outputs are included so you can tell success from failure.

## 0. One-time session setup

```bash
cd ~/code_projects/rag-assistant
source .venv/bin/activate
export PYTHONPATH=src
```

From here `python -m rag.cli ...` and `pytest` work. Alternatively use `make`, which sets
`PYTHONPATH` for you.

## 1. Check Ollama

```bash
python -m rag.cli models
```

Expected: the host, the configured `embed_model` / `chat_model`, and a list of installed
Ollama models including `nomic-embed-text` and `llama3.1`.

## 2. Build the index

```bash
make ingest
```

Expected: `Indexed 7 chunks -> .../data/index`.

Inspect the artifacts:

```bash
ls data/index          # vectors.npy  documents.jsonl
```

`vectors.npy` holds the normalized embeddings; `documents.jsonl` is a human-readable dump
of the chunks.

## 3. Ask questions

```bash
make ask Q="How much does the Team plan cost per month?"
make ask Q="Which regions does Aurora Cloud operate in?"
make ask Q="Who won the 2026 FIFA World Cup?"
```

Expected for the first two: a short answer followed by cited sources.

Expected for the third (out of corpus): the exact refusal
`I don't have enough information in the provided documents to answer that.`

> **Nuance worth understanding.** For the out-of-corpus question the sources are still
> listed. Embeddings of any two texts have a positive cosine similarity (~0.45 here), which
> is above the `min_score` gate (0.15), so the LLM is called and refuses per the system
> prompt — it is the model, not the `min_score` filter, that refuses. Raise `min_score` in
> `RagPipeline` to make the gate itself refuse.

## 4. Compare the reranker

```bash
make ask Q="Do discounts stack with promotional credits?"
RERANK=1 make ask Q="Do discounts stack with promotional credits?"
```

Without the reranker the small model sometimes claims discounts stack; with the reranker the
exact clause ("Discounts do not stack with promotional credits") is pulled to the top and the
answer is correct. Temperature is 0.1, so results can occasionally vary — that is expected.

## 5. Evaluation

```bash
make eval                 # hit-rate, recall, MRR  -> expect 1.000
make eval RERANK=1        # same with reranker (slower)
python -m rag.cli eval --judge    # adds LLM-as-judge grounding
```

## 6. Unit tests

```bash
make test
```

Expected: `74 passed`. The suite is offline — it needs neither Ollama nor the network.

## 7. Experiments (this is where the learning is)

Change behaviour with environment variables:

```bash
TOP_K=3 make ask Q="What encryption is used for data at rest?"
MMR_LAMBDA=0.0 make ask Q="pricing"        # maximum diversity
CHUNK_SIZE=400 make ingest                 # smaller chunks -> more of them
python -m rag.cli ask "your question" --json   # raw JSON with citations
```

## 8. HTTP API (two terminals)

Terminal A:

```bash
make api        # http://localhost:8000
```

Terminal B:

```bash
curl localhost:8000/health
curl -X POST localhost:8000/ask -H 'Content-Type: application/json' \
  -d '{"question":"What encryption is used for data at rest?"}'
curl -X POST localhost:8000/search -H 'Content-Type: application/json' \
  -d '{"question":"pricing","top_k":3}'
```

## 9. Streamlit UI

```bash
make serve      # http://localhost:8501
```

Use the sidebar sliders for `top-k` and `MMR lambda`, and toggle the context view.

## 10. Easy mode (browser upload + chat)

```bash
make easy       # or ./start.sh
```

A bilingual (PL/EN) app opens. Upload a document, click **Add to the library**, then ask a
question in the box at the bottom. Switch the language in the sidebar. This is the flow a
non-technical user sees. See [`EASY_MODE.md`](EASY_MODE.md).

To see the troubleshooting panel without touching your real Ollama, point the app at a dead
address (one line, nothing is broken):

```bash
make demo-error
```

The app then shows the ❌ diagnostics panel; use **Check again** to refresh.

## 11. The most important test: your own documents

1. Drop a `.md`, `.txt`, `.pdf` or `.docx` file into `data/raw/` — or, for anything
   private, into `data/raw/private/` (gitignored). This can be your notes, part of your CV,
   a manual, anything.
2. `make ingest` (rebuilds the index from scratch).
3. `make ask Q="..."` about something only in your file and confirm the citation points to
   the right source.

## Troubleshooting

| Symptom | Cause / fix |
|---|---|
| `ModuleNotFoundError: No module named 'rag'` | Missing `PYTHONPATH=src` — use `make` |
| `Cannot reach Ollama at ...` | Ollama not running: `ollama serve`, or check `curl localhost:11434/api/tags` |
| `No index found in ...` | Run `make ingest` first |
| Answers are slow | CPU inference; use a smaller `CHAT_MODEL` or lower `TOP_K` |
| Reranker very slow | It calls the LLM once per candidate; lower `RERANK_CANDIDATES` |
| `make ask` prints `Usage: make ask Q="your question"` | You passed no question (or only spaces). Pass `Q="..."` (both `Q=` and `q=` work) |
| `rag ask ""` fails immediately | By design — empty questions are rejected with exit code 2 |
