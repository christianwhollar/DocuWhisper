from typing import List
import numpy as np
import faiss

class VectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def add_documents(self, documents: List[str], embeddings: List[np.ndarray]):
        embeddings_array = np.array(embeddings, dtype=np.float32)

        if embeddings_array.shape[0] > 0:
            self.index.add(embeddings_array)
            self.documents.extend(documents)
        else:
            print("Warning: No embeddings to add to the index.")

    def search(self, query_embedding: np.ndarray, k: int) -> List[str]:
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)
        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)
        return [self.documents[i] for i in indices[0]]
