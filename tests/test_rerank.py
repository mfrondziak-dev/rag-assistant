from rag.models import Document, SearchResult
from rag.rerank import LLMReranker, parse_score


class ScriptedLLM:
    def __init__(self, replies):
        self._replies = list(replies)
        self.calls = []

    def chat(self, messages, **options):
        self.calls.append(messages)
        return self._replies.pop(0)


def _result(doc_id, text, score=0.5):
    return SearchResult(document=Document(id=doc_id, text=text, source=f"{doc_id}.md"), score=score)


def test_parse_score_clamps_and_handles_noise():
    assert parse_score("7") == 7.0
    assert parse_score("Score: 8.5") == 8.5
    assert parse_score("42") == 10.0
    assert parse_score("no number here") == 0.0


def test_reranker_reorders_by_llm_score():
    results = [_result("a", "alpha"), _result("b", "beta")]
    reranker = LLMReranker(ScriptedLLM(["2", "9"]), top_n=2)

    reranked = reranker.rerank("question", results)

    assert [r.document.id for r in reranked] == ["b", "a"]


def test_reranker_truncates_to_top_n():
    results = [_result("a", "alpha"), _result("b", "beta"), _result("c", "gamma")]
    reranker = LLMReranker(ScriptedLLM(["3", "9", "5"]), top_n=1)

    reranked = reranker.rerank("question", results)

    assert [r.document.id for r in reranked] == ["b"]
