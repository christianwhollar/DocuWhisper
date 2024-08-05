# tests/test_embeddings.py
import os
import numpy as np
from src.embeddings import Embeddings


def test_get_embeddings(setup_environment, get_document_loader):
    model_id, _, embedding_directory, huggingface_api_key = setup_environment
    titles, documents = get_document_loader

    embeddings = Embeddings(model_id=model_id, HUGGINGFACE_API_KEY=huggingface_api_key)
    document_embeddings, _ = embeddings.get_embeddings(
        titles, documents, embedding_directory=embedding_directory
    )

    for title, embedding in zip(titles, document_embeddings):
        file_path = os.path.join(
            "tests/test_data/test_embeddings", title.replace(" ", "_") + "_1.npy"
        )
        expected_embeddings = np.load(file_path, allow_pickle=True).reshape(-1)

        assert np.allclose(
            embedding, expected_embeddings, atol=1e-4
        ), f"Embeddings for {title} do not match"
