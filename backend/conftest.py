# conftest.py
import pytest
from dotenv import load_dotenv
import toml
import os
import pytest
from src.document_loader import DocumentLoader
from src.embeddings import Embeddings
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.llm import LLM

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
def get_document_loader(setup_environment):
    _, document_directory, _, _ = setup_environment
    loader = DocumentLoader(document_directory)
    return loader.load_documents()

@pytest.fixture
def get_embeddings(setup_environment, get_document_loader):
    model_id, _, embedding_directory, huggingface_api_key = setup_environment
    titles, documents = get_document_loader

    embeddings = Embeddings(model_id=model_id, HUGGINGFACE_API_KEY=huggingface_api_key)
    document_embeddings = embeddings.get_embeddings(titles, documents, embedding_directory=embedding_directory)

    return documents, embeddings, document_embeddings

@pytest.fixture
def get_vector_store(get_embeddings):
    documents, embeddings, document_embeddings = get_embeddings
    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(documents, document_embeddings)
    return vector_store, embeddings

@pytest.fixture
def get_retriever(get_vector_store):
    vector_store, embeddings = get_vector_store
    retriever = Retriever(vector_store, embeddings)
    return retriever

@pytest.fixture
def get_llm():
    return LLM(base_url="http://test.com")