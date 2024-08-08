import os
import toml
import time
import json
import requests
import pytest
from dotenv import load_dotenv
from src.document_loader import DocumentLoader
from src.embeddings import Embeddings
from src.vector_store import VectorStore
from src.retriever import Retriever
from src.llm import LLM
from src.rag_agent import RAGAgent

load_dotenv()


def check_url_responsive(url):
    try:
        print(url)
        response = requests.get(url.split("/v1")[0])
        return response.status_code == 200
    except requests.RequestException:
        return False


def load_config():
    env = "test"
    with open(f"config/config.{env}.toml", "r") as file:
        return toml.load(file)


# @pytest.mark.skip(reason="Skipping by default. Remove this mark to run the test.")
@pytest.mark.skipif(
    not check_url_responsive(load_config()["llm"]["api_url"]),
    reason="LLM API URL is not responsive",
)
def test_rag_agent_evaluation():
    config = load_config()

    model_id = config["model"]["id"]
    document_directory = config["documents"]["directory"]
    embedding_directory = os.path.join(document_directory, "embeddings")

    loader = DocumentLoader(document_directory)
    titles, documents = loader.load_documents()

    huggingface_api_key = os.getenv("HUGGINGFACE_API_KEY")
    if not huggingface_api_key:
        raise ValueError("HUGGINGFACE_API_KEY not found in environment variables")

    embeddings = Embeddings(model_id=model_id, HUGGINGFACE_API_KEY=huggingface_api_key)
    document_embeddings, chunked_texts_with_titles = embeddings.get_embeddings(
        titles, documents, embedding_directory=embedding_directory
    )

    embedding_dimension = len(document_embeddings[0])
    vector_store = VectorStore(dimension=embedding_dimension)
    vector_store.add_documents(chunked_texts_with_titles, document_embeddings)

    retriever = Retriever(vector_store, embeddings)
    llm = LLM(config["llm"]["api_url"])

    rag_agent = RAGAgent(retriever=retriever, llm=llm)

    queries = [
        "What is the main theme of the book Dracula?",
        "Describe the character of Count Dracula.",
        "What are the major settings in the book Dracula?",
        "What are the significant symbols used in Dracula?",
        "How does the author use foreshadowing in Dracula?",
        "What is the role of Mina Harker in Dracula?",
        "How does Bram Stoker create suspense in Dracula?",
        "What is the significance of blood in Dracula?",
        "How does the setting influence the mood in Dracula?",
        "What are the Gothic elements in Dracula?",
    ]

    average_latencies = []
    output_speeds = []
    times = []
    query_lengths = []
    results = []

    for query in queries:
        prompt = rag_agent.get_prompt(query=query)
        prompt_tokens = len(prompt.split())

        start_time = time.time()
        answer = rag_agent.answer(query=query)
        end_time = time.time()

        response_tokens = len(answer.split())
        time_taken = end_time - start_time
        average_latency = time_taken
        output_speed = response_tokens / time_taken

        average_latencies.append(average_latency)
        output_speeds.append(output_speed)
        times.append(time_taken)
        query_lengths.append(prompt_tokens)

        result = {
            "query": query,
            "prompt_tokens": prompt_tokens,
            "response_tokens": response_tokens,
            "time_taken": time_taken,
            "output_speed": output_speed,
            "average_latency": average_latency,
        }
        results.append(result)

    # Summary statistics
    summary = {
        "average_latency_sec": sum(average_latencies) / len(average_latencies),
        "output_speed_tokens_sec": sum(output_speeds) / len(output_speeds),
        "response_time_vs_query_length": list(zip(times, query_lengths)),
    }

    # Add summary to results
    results.append(summary)

    # Save results to a file
    timestamp = int(time.time())
    output_directory = "evals/" + model_id.split("/")[0]
    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(
        output_directory, f"{model_id.split('/')[-1]}_{timestamp}.json"
    )

    with open(output_file, "w") as file:
        json.dump(results, file, indent=4)
