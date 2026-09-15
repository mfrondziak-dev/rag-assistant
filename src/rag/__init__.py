"""Local, citation-grounded retrieval-augmented generation over your own documents."""

from .config import Settings
from .models import Citation, Document, RAGAnswer, SearchResult
from .pipeline import RagPipeline
from .store import VectorStore

__version__ = "0.1.0"

__all__ = [
    "Settings",
    "Document",
    "SearchResult",
    "Citation",
    "RAGAnswer",
    "RagPipeline",
    "VectorStore",
    "__version__",
]
