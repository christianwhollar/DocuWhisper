from typing import List
from .vector_store import VectorStore
from .embeddings import Embeddings

class Retriever:
    def __init__(self, vector_store: VectorStore, embeddings: Embeddings):
        self.vector_store = vector_store
        self.embeddings = embeddings

    def retrieve(self, query:str, k: int) -> List[str]:
        query_embedding = self.embeddings.get_embeddings_query([query])[0]
        return self.vector_store.search(query_embedding, k)
