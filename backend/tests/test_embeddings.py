# tests/test_embeddings.py
from dotenv import load_dotenv
import os
import numpy as np
from src.document_loader import DocumentLoader
from src.embeddings import Embeddings
import pytest
import toml

@pytest.fixture
def setup_environment():
    load_dotenv()
    env = os.getenv('ENV')
    print(env)
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

def test_get_embeddings(setup_environment, load_documents):
    model_id, _, embedding_directory, huggingface_api_key = setup_environment
    titles, documents = load_documents

    embeddings = Embeddings(model_id=model_id, HUGGINGFACE_API_KEY=huggingface_api_key)
    document_embeddings = embeddings.get_embeddings(titles, documents, embedding_directory=embedding_directory)

    for title, embedding in zip(titles, document_embeddings):
        file_path = os.path.join("tests/test_data/test_embeddings", title.replace(' ', '_') + '.npy')
        expected_embedding = np.load(file_path, allow_pickle=True).tolist()
        assert np.allclose(embedding, expected_embedding, rtol=1e-5, atol=1e-8), f"Embeddings for {title} do not match"