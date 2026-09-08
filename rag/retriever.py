"""
RAG retriever — fetches the most relevant knowledge base chunks
for a given query to augment LLM prompts.
"""

from typing import List
from langchain_core.documents import Document
from rag.loader import get_vector_store

_vector_store = None


def _get_store():
    global _vector_store
    if _vector_store is None:
        _vector_store = get_vector_store()
    return _vector_store


def retrieve(query: str, k: int = 4, source_filter: str = None) -> List[Document]:
    """
    Retrieve the top-k most relevant documents for the given query.

    Args:
        query: The search query string.
        k: Number of documents to return.
        source_filter: Optional filename to restrict results to a specific knowledge source
                       (e.g., "technical_questions.txt").

    Returns:
        List of LangChain Document objects with page_content and metadata.
    """
    store = _get_store()

    search_kwargs = {"k": k}
    if source_filter:
        search_kwargs["filter"] = {"source": source_filter}

    results = store.similarity_search(query, **search_kwargs)
    return results


def retrieve_as_text(query: str, k: int = 4, source_filter: str = None) -> str:
    """
    Convenience wrapper — returns retrieved content as a single joined string
    ready to be injected into an LLM prompt.
    """
    docs = retrieve(query, k=k, source_filter=source_filter)
    if not docs:
        return ""
    return "\n\n---\n\n".join(doc.page_content for doc in docs)
