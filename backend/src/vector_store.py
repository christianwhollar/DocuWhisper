from typing import List

import faiss
import numpy as np


class VectorStore:
    def __init__(self, dimension: int):
        """
        Store Document and Chunk Embeddings

        Args:
            dimension (int): FAISS Dimension
        """
        self.index = faiss.IndexFlatL2(dimension)
        self.documents = []

    def add_documents(self, documents: List[str], embeddings: List[np.ndarray]):
        """
        Add Documents, Embeddings to Vector Store

        Args:
            documents (List[str]): List of Documents
            embeddings (List[np.ndarray]): List of Document Embeddings
        """
        embeddings_array = np.array(embeddings, dtype=np.float32)

        if embeddings_array.shape[0] > 0:
            self.index.add(embeddings_array)
            self.documents.extend(documents)
        else:
            print("Warning: No embeddings to add to the index.")

    def search(self, query_embedding: np.ndarray, k: int) -> List[str]:
        """
        Search Vector Store via FAISS for Query

        Args:
            query_embedding (np.ndarray): Embedding for Query
            k (int): Number of Chunks to Return

        Returns:
            List[str]: List of Chunks
        """
        query_embedding = query_embedding.astype(np.float32).reshape(1, -1)

        distances, indices = self.index.search(query_embedding.reshape(1, -1), k)

        return [self.documents[i] for i in indices[0]]
