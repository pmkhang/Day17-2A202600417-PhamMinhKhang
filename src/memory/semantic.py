try:
    import chromadb as _chromadb
except ImportError:
    _chromadb = None  # type: ignore


class SemanticMemory:
    def __init__(self, collection_name: str = "semantic"):
        try:
            if _chromadb is None:
                raise ImportError("chromadb not installed")
            self._client = _chromadb.PersistentClient(path="data/chroma_db")
            self._col = self._client.get_or_create_collection(collection_name)
        except Exception:
            self._col = None

    def save(self, text: str, doc_id: str) -> None:
        if self._col is None:
            return
        self._col.upsert(documents=[text], ids=[doc_id])

    def retrieve(self, query: str, n_results: int = 3) -> list[str]:
        if self._col is None:
            return []
        results = self._col.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        return docs
