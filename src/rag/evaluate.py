from __future__ import annotations

import json
import re
from dataclasses import dataclass
from pathlib import Path

from .models import SearchResult
from .pipeline import RagPipeline
from .retriever import Retriever

JUDGE_PROMPT = (
    "You are a strict evaluator. Given a question, the retrieved context, and an answer, "
    "decide whether every factual claim in the answer is supported by the context. "
    'Respond with a single JSON object: {"grounded": true|false, "score": <0.0-1.0>}. '
    "score is 1.0 when fully supported and 0.0 when not supported at all."
)


@dataclass
class RetrievalMetrics:
    questions: int
    hit_rate: float
    recall: float
    mrr: float


@dataclass
class JudgementResult:
    grounded: bool
    score: float


def load_dataset(path: str | Path) -> list[dict]:
    items = []
    with Path(path).open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if line:
                items.append(json.loads(line))
    if not items:
        raise RuntimeError(f"Evaluation dataset {path} is empty")
    return items


def _is_relevant(result: SearchResult, item: dict) -> bool:
    relevant_ids = set(item.get("relevant_ids", []))
    relevant_sources = item.get("relevant_sources", [])
    if result.document.id in relevant_ids:
        return True
    source = result.document.source.replace("\\", "/")
    return any(source.endswith(name) for name in relevant_sources)


def evaluate_retrieval(retriever: Retriever, dataset: list[dict], k: int = 5) -> RetrievalMetrics:
    hits = 0
    reciprocal_ranks = 0.0
    recalls = 0.0
    for item in dataset:
        results = retriever.retrieve(item["question"])[:k]
        relevant_flags = [_is_relevant(r, item) for r in results]
        if any(relevant_flags):
            hits += 1
            reciprocal_ranks += 1.0 / (relevant_flags.index(True) + 1)
        expected = len(item.get("relevant_ids", [])) or len(item.get("relevant_sources", [])) or 1
        recalls += sum(relevant_flags) / expected
    n = len(dataset)
    return RetrievalMetrics(
        questions=n,
        hit_rate=hits / n,
        recall=min(1.0, recalls / n),
        mrr=reciprocal_ranks / n,
    )


def judge_answer(pipeline: RagPipeline, question: str, context: str, answer: str) -> JudgementResult:
    prompt = f"Question: {question}\n\nContext:\n{context}\n\nAnswer:\n{answer}"
    raw = pipeline.llm.chat(
        [
            {"role": "system", "content": JUDGE_PROMPT},
            {"role": "user", "content": prompt},
        ]
    )
    return _parse_judgement(raw)


def _parse_judgement(raw: str) -> JudgementResult:
    match = re.search(r"\{.*\}", raw, re.DOTALL)
    if match:
        try:
            payload = json.loads(match.group(0))
            return JudgementResult(
                grounded=bool(payload.get("grounded", False)),
                score=float(payload.get("score", 0.0)),
            )
        except (ValueError, TypeError):
            pass
    grounded = "true" in raw.lower() and "false" not in raw.lower()
    return JudgementResult(grounded=grounded, score=1.0 if grounded else 0.0)


def evaluate_answers(pipeline: RagPipeline, dataset: list[dict]) -> dict:
    scores = []
    grounded = 0
    for item in dataset:
        response = pipeline.answer(item["question"])
        context = "\n\n".join(r.document.text for r in response.contexts)
        verdict = judge_answer(pipeline, item["question"], context, response.answer)
        scores.append(verdict.score)
        grounded += int(verdict.grounded)
    n = len(dataset)
    return {
        "answers": n,
        "grounded_rate": grounded / n,
        "avg_groundedness": sum(scores) / n,
    }
