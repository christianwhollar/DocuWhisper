# tests/test_vector_store.py
import pytest
from src.document_loader import DocumentLoader
from src.embeddings import Embeddings
from src.vector_store import VectorStore
import toml
import os

@pytest.fixture
def setup_environment():
    env = 'test'

    with open(f'config/config.{env}.toml', 'r') as file:
        config = toml.load(file)

    model_id = config['model']['id']
    document_directory = config['documents']['directory']
    embedding_directory = os.path.join(document_directory, "embeddings")
    
    huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not huggingface_api_key:
        raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")
    
    return model_id, document_directory, embedding_directory, huggingface_api_key

@pytest.fixture
def load_documents(setup_environment):
    _, document_directory, _, _ = setup_environment
    loader = DocumentLoader(document_directory)
    return loader.load_documents()

def test_vector_store(setup_environment, load_documents):
    model_id, _, embedding_directory, huggingface_api_key = setup_environment
    titles, documents = load_documents

    embeddings = Embeddings(model_id=model_id, HUGGINGFACE_API_KEY=huggingface_api_key)
    document_embeddings = embeddings.get_embeddings(titles, documents, embedding_directory=embedding_directory)

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
