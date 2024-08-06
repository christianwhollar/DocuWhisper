# conftest.py
import os

import pytest
import toml
from dotenv import load_dotenv

from src.document_loader import DocumentLoader
from src.embeddings import Embeddings
from src.llm import LLM
from src.retriever import Retriever
from src.vector_store import VectorStore


@pytest.fixture
def setup_environment():
    load_dotenv()

    env = os.getenv("ENV")
    env = "test"
    with open(f"config/config.{env}.toml", "r") as file:
        config = toml.load(file)

    model_id = config["model"]["id"]
    document_directory = config["documents"]["directory"]
    embedding_directory = os.path.join(document_directory, "embeddings")

    huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not huggingface_api_key:
        raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

    return (model_id, document_directory, embedding_directory, huggingface_api_key)


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
    document_embeddings, chunked_texts_with_titles = embeddings.get_embeddings(
        titles, documents, embedding_directory=embedding_directory
    )

    return embeddings, document_embeddings, chunked_texts_with_titles


@pytest.fixture
def get_vector_store(get_embeddings):
    """_summary_

    Args:
        get_embeddings (_type_): _description_

    Returns:
        _type_: _description_
    """
    embeddings, document_embeddings, chunked_texts_with_titles = get_embeddings
    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(chunked_texts_with_titles, document_embeddings)
    return vector_store, embeddings


@pytest.fixture
def get_retriever(get_vector_store):
    """_summary_

    Args:
        get_vector_store (_type_): _description_

    Returns:
        _type_: _description_
    """
    vector_store, embeddings = get_vector_store
    retriever = Retriever(vector_store, embeddings)
    return retriever


@pytest.fixture
def get_llm():
    """_summary_

    Returns:
        _type_: _description_
    """
    return LLM(base_url="http://test.com")


@pytest.fixture(scope="session", autouse=True)
def mock_psycopg2():
    from tests.utils import mock_psycogp2

    mock_psycogp2
