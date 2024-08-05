# tests/test_retriever.py
from src.retriever import Retriever


def test_retrieve(get_vector_store):
    vector_store, embeddings = get_vector_store

    query = "This is the first document."
    k = 3

    retriever = Retriever(vector_store, embeddings)
    context = retriever.retrieve(query, k=k)
    print(context)
    assert query in context[0]
