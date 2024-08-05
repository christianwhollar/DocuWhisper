# src/initialize.py
import os
import toml
from dotenv import load_dotenv
from .document_loader import DocumentLoader
from .embeddings import Embeddings
from .vector_store import VectorStore
from .retriever import Retriever
from .llm import LLM
from .rag_agent import RAGAgent


def initialize_rag_agent():
    # Load environment variables
    load_dotenv()

    env = os.getenv("ENV", "development")

    # Load configuration
    with open(f"config/config.{env}.toml", "r") as file:
        config = toml.load(file)

    model_id = config["model"]["id"]
    document_directory = config["documents"]["directory"]
    embedding_directory = os.path.join(document_directory, "embeddings")

    # Initialize components
    loader = DocumentLoader(document_directory)
    titles, documents = loader.load_documents()

    huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not huggingface_api_key:
        raise ValueError(
            "HUGGINGFACE_API_KEY not found in environment variables")

    embeddings = Embeddings(
        model_id=model_id,
        HUGGINGFACE_API_KEY=huggingface_api_key)
    document_embeddings = embeddings.get_embeddings(
        titles, documents, embedding_directory=embedding_directory
    )

    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(documents, document_embeddings)

    retriever = Retriever(vector_store, embeddings)
    llm = LLM(config["llm"]["api_url"])

    return RAGAgent(retriever=retriever, llm=llm)
