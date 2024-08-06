import os

import toml
from dotenv import load_dotenv

from src.document_loader import DocumentLoader
from src.embeddings import Embeddings
from src.llm import LLM
from src.rag_agent import RAGAgent
from src.retriever import Retriever
from src.vector_store import VectorStore


def main():
    # load env vars
    load_dotenv()

    env = os.getenv("ENV")

    # load config vars
    with open(f"config/config.{env}.toml", "r") as file:
        config = toml.load(file)

    model_id = config["model"]["id"]

    # directory to load documents from
    document_directory = "data/test"

    # create document loader
    loader = DocumentLoader(document_directory)
    titles, documents = loader.load_documents()

    # get embeddings for loaded documents
    HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

    # save directory for embeddings
    embedding_directory = document_directory + "/embeddings"

    # generate or load embeddings
    embeddings = Embeddings(model_id=model_id, HUGGINGFACE_API_KEY=HUGGINGFACE_API_KEY)

    document_embeddings, chunked_texts_with_titles = embeddings.get_embeddings(
        titles, documents, embedding_directory=embedding_directory
    )

    # vector storage
    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(chunked_texts_with_titles, document_embeddings)

    # retriever and llm
    retriever = Retriever(vector_store, embeddings)
    llm = LLM(config['llm']['api_url'])

    # rag agent
    rag_agent = RAGAgent(retriever=retriever, llm=llm)

    while True:
        query = input("Query:")

        if query.lower() == "exit":
            break

        answer = rag_agent.answer(query)
        print(answer)


if __name__ == "__main__":
    main()
