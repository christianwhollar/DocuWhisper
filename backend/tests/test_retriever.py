# tests/test_vector_store.py
import pytest
from dotenv import load_dotenv
from src.document_loader import DocumentLoader
from src.embeddings import Embeddings
from src.vector_store import VectorStore
from src.retriever import Retriever
import toml
import os

@pytest.fixture
def setup_environment():
    load_dotenv()

    env = os.getenv('ENV')

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

@pytest.fixture
def get_embeddings(setup_environment, load_documents):
    model_id, _, embedding_directory, huggingface_api_key = setup_environment
    titles, documents = load_documents

    embeddings = Embeddings(model_id=model_id, HUGGINGFACE_API_KEY=huggingface_api_key)
    document_embeddings = embeddings.get_embeddings(titles, documents, embedding_directory=embedding_directory)

    return documents, embeddings, document_embeddings

def test_retrieve(get_embeddings):
    documents, embeddings, document_embeddings = get_embeddings
    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(documents, document_embeddings)

    query = "This is the first document."
    k = 3

    retriever = Retriever(vector_store, embeddings)
    context = retriever.retrieve(query, k=3)

    assert context[0] == query
