# tests/test_vector_store.py
from src.vector_store import VectorStore

def test_vector_store(get_embeddings):
    documents, embeddings, document_embeddings = get_embeddings

    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(documents, document_embeddings)

    query = "This is the first document."
    k = 3
    query_embedding = embeddings.get_embeddings_query([query])[0]
    results = vector_store.search(query_embedding, k)

    assert vector_store.documents == documents
    assert len(results) == k
    assert documents[0] in results
