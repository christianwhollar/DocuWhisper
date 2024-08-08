from typing import List

from .embeddings import Embeddings
from .vector_store import VectorStore


class Retriever:
    def __init__(self, vector_store: VectorStore, embeddings: Embeddings):
        """
        Retrive Embeddings from Vector Store

        Args:
            vector_store (VectorStore): Vector Store Object
            embeddings (Embeddings): Embeddings Object
        """
        self.vector_store = vector_store
        self.embeddings = embeddings

    def retrieve(self, query: str, k: int) -> List[str]:
        query_embedding = self.embeddings.get_embeddings_query([query])[0]
        return self.vector_store.search(query_embedding, k)
