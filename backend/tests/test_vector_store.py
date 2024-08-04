# tests/test_vector_store.py
from src.vector_store import VectorStore

def test_vector_store(get_embeddings):
    embeddings, document_embeddings, chunked_texts_with_titles  = get_embeddings

    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(chunked_texts_with_titles, document_embeddings)

    query = "This is the first document."
    k = 3
    query_embedding = embeddings.get_embeddings_query([query])[0]
    results = vector_store.search(query_embedding, k)

    assert vector_store.documents == chunked_texts_with_titles
    assert len(results) == k
    assert chunked_texts_with_titles[0] in results
