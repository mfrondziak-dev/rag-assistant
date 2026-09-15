from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from .config import PROJECT_ROOT, Settings
from .evaluate import evaluate_answers, evaluate_retrieval, load_dataset
from .factory import build_ollama, build_pipeline
from .ingest import ingest
from .store import VectorStore


def _settings_from_args(args: argparse.Namespace) -> Settings:
    settings = Settings()
    if getattr(args, "index", None):
        settings.index_dir = Path(args.index)
    if getattr(args, "top_k", None):
        settings.top_k = args.top_k
    if getattr(args, "rerank", False):
        settings.rerank = True
    return settings


def _cmd_ingest(args: argparse.Namespace) -> int:
    settings = _settings_from_args(args)
    raw_dir = Path(args.raw)
    print(f"Ingesting documents from {raw_dir} ...")
    store = ingest(settings, raw_dir)
    print(f"Indexed {len(store)} chunks -> {settings.index_dir}")
    return 0


def _cmd_ask(args: argparse.Namespace) -> int:
    question = args.question.strip()
    if not question:
        print("error: question must not be empty", file=sys.stderr)
        return 2
    settings = _settings_from_args(args)
    store = VectorStore.load(settings.index_dir)
    pipeline = build_pipeline(settings, store)
    result = pipeline.answer(question)

    if args.json:
        print(
            json.dumps(
                {
                    "question": result.question,
                    "answer": result.answer,
                    "used_context": result.used_context,
                    "citations": [c.__dict__ for c in result.citations],
                },
                ensure_ascii=False,
                indent=2,
            )
        )
        return 0

    print("\nAnswer:")
    print(result.answer)
    if result.citations:
        print("\nSources:")
        for citation in result.citations:
            print(f"  [{citation.index}] {citation.source} (score {citation.score:.3f})")
    if args.show_context:
        print("\nContext:")
        for citation in result.citations:
            print(f"\n  [{citation.index}] {citation.snippet}")
    return 0


def _cmd_eval(args: argparse.Namespace) -> int:
    settings = _settings_from_args(args)
    store = VectorStore.load(settings.index_dir)
    pipeline = build_pipeline(settings, store)
    dataset = load_dataset(args.dataset)
    if args.limit:
        dataset = dataset[: args.limit]

    metrics = evaluate_retrieval(pipeline.retriever, dataset, k=args.k)
    print(f"Retrieval @ k={args.k} on {metrics.questions} questions")
    print(f"  hit-rate : {metrics.hit_rate:.3f}")
    print(f"  recall   : {metrics.recall:.3f}")
    print(f"  MRR      : {metrics.mrr:.3f}")
    if args.judge:
        answers = evaluate_answers(pipeline, dataset)
        print(f"Answer grounding on {answers['answers']} answers")
        print(f"  grounded rate    : {answers['grounded_rate']:.3f}")
        print(f"  avg groundedness : {answers['avg_groundedness']:.3f}")
    return 0


def _cmd_models(args: argparse.Namespace) -> int:
    settings = _settings_from_args(args)
    client = build_ollama(settings)
    if not client.health():
        print(f"Ollama is not reachable at {settings.ollama_host}", file=sys.stderr)
        return 1
    print(f"Ollama at {settings.ollama_host}")
    print(f"  embed model: {settings.embed_model}")
    print(f"  chat model : {settings.chat_model}")
    print("  available models:")
    for name in client.list_models():
        print(f"    - {name}")
    return 0


def _cmd_serve(args: argparse.Namespace) -> int:
    import subprocess

    app_path = PROJECT_ROOT / "app" / "streamlit_app.py"
    return subprocess.call(
        [sys.executable, "-m", "streamlit", "run", str(app_path), "--server.port", str(args.port)]
    )


def _cmd_api(args: argparse.Namespace) -> int:
    import uvicorn

    from .api import app

    uvicorn.run(app, host=args.host, port=args.port)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="rag", description="Local RAG over your documents")
    parser.add_argument("--version", action="version", version="rag-assistant 0.1.0")
    sub = parser.add_subparsers(dest="command", required=True)

    p_ingest = sub.add_parser("ingest", help="build the vector index from data/raw")
    p_ingest.add_argument("--raw", default="data/raw")
    p_ingest.add_argument("--index", default=None)
    p_ingest.set_defaults(func=_cmd_ingest)

    p_ask = sub.add_parser("ask", help="ask a question against the index")
    p_ask.add_argument("question")
    p_ask.add_argument("--top-k", type=int, default=None)
    p_ask.add_argument("--show-context", action="store_true")
    p_ask.add_argument("--rerank", action="store_true")
    p_ask.add_argument("--json", action="store_true")
    p_ask.add_argument("--index", default=None)
    p_ask.set_defaults(func=_cmd_ask)

    p_eval = sub.add_parser("eval", help="evaluate retrieval and answer grounding")
    p_eval.add_argument("--dataset", default="data/eval/questions.jsonl")
    p_eval.add_argument("-k", type=int, default=5)
    p_eval.add_argument("--limit", type=int, default=None)
    p_eval.add_argument("--judge", action="store_true")
    p_eval.add_argument("--rerank", action="store_true")
    p_eval.add_argument("--index", default=None)
    p_eval.set_defaults(func=_cmd_eval)

    p_models = sub.add_parser("models", help="list available Ollama models")
    p_models.set_defaults(func=_cmd_models)

    p_serve = sub.add_parser("serve", help="launch the Streamlit UI")
    p_serve.add_argument("--port", type=int, default=8501)
    p_serve.set_defaults(func=_cmd_serve)

    p_api = sub.add_parser("api", help="run the FastAPI service")
    p_api.add_argument("--host", default="127.0.0.1")
    p_api.add_argument("--port", type=int, default=8000)
    p_api.set_defaults(func=_cmd_api)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
