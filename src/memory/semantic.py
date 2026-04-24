import chromadb


class SemanticMemory:
    def __init__(self, collection_name: str = "semantic"):
        self._client = chromadb.PersistentClient(path="data/chroma_db")
        self._col = self._client.get_or_create_collection(collection_name)

    def save(self, text: str, doc_id: str) -> None:
        self._col.upsert(documents=[text], ids=[doc_id])

    def retrieve(self, query: str, n_results: int = 3) -> list[str]:
        results = self._col.query(query_texts=[query], n_results=n_results)
        docs = results.get("documents", [[]])[0]
        return docs
