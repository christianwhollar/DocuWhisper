import os
from typing import List, Tuple

import nltk
import numpy as np
import psycopg2
import torch
from dotenv import load_dotenv
from nltk.tokenize import sent_tokenize
from transformers import AutoModel, AutoTokenizer

try:
    nltk.find("punkt")
except LookupError:
    nltk.download("punkt")


class Embeddings:
    """Generate or Load Embeddings"""

    def __init__(self, model_id: str, HUGGINGFACE_API_KEY: str, db_mode: bool = False):
        """
        Initialize Embeddings Object

        Args:
            model_id (str): Model ID to Generate Embeddings
            HUGGINGFACE_API_KEY (str): Huggingface API Key
            db_mode (bool, optional): Database Mode. Defaults to False.
        """
        self.tokenizer = AutoTokenizer.from_pretrained(
            model_id, token=HUGGINGFACE_API_KEY
        )

        self.model = AutoModel.from_pretrained(model_id, token=HUGGINGFACE_API_KEY)

        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

        self.model.to(self.device)

        if db_mode:
            self.db_config = self.load_db_config()

    def load_db_config(self):
        """
        Load Database Config
        """
        load_dotenv()
        return {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }

    def get_embeddings(
        self, titles: List[str], texts: List[str], embedding_directory: str
    ) -> Tuple[List[np.ndarray], List[str]]:
        """
        Load or Generate Embeddings Local

        Args:
            titles (List[str]):
                List of titles for documents.
            texts (List[str]):
                List of texts for documents.
            embedding_directory (str):
                Save directory for generated embeddings.

        Returns:
            Tuple[List[np.ndarray], List[str]]:
                Returns generated embeddings and text chunks.
        """
        os.makedirs(embedding_directory, exist_ok=True)
        embeddings = []
        chunked_texts_with_titles = []

        for title, text in zip(titles, texts):
            sentences = sent_tokenize(text)
            chunked_texts = [
                " ".join(sentences[i : i + 3]) for i in range(0, len(sentences), 3)
            ]

            # Iterate Through Chunk Number, and Chunk
            for idx, chunk in enumerate(chunked_texts):
                chunk_title = f"{title.replace(' ', '_')}_{idx + 1}"
                chunked_text_with_title = f"{title}_Chunk_{idx + 1}: {chunk}"
                chunked_texts_with_titles.append(chunked_text_with_title)

                file_path = os.path.join(embedding_directory, chunk_title + ".npy")

                # Check if Embedding Exists for Chunk
                if os.path.exists(file_path):
                    embedding = np.load(file_path, allow_pickle=True).tolist()
                    embeddings.extend(embedding)

                # Else Generate Embedding
                else:
                    inputs = self.tokenizer(
                        chunk,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512,
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}

                    with torch.no_grad():
                        outputs = self.model(**inputs)

                    last_hidden_state = outputs.last_hidden_state
                    mean_hidden_state = last_hidden_state.mean(dim=1)
                    cpu_mean_hidden_state = mean_hidden_state.cpu()
                    numpy_mean_hidden_state = cpu_mean_hidden_state.numpy()
                    embedding = numpy_mean_hidden_state[0]

                    embeddings.append(embedding.astype(np.float32))

                    # Save Embedding Locally
                    np.save(file_path, [embedding])

        return embeddings, chunked_texts_with_titles

    def get_embeddings_query(self, texts: List[str]) -> List[np.ndarray]:
        """
        Get Embedding for Query

        Args:
            texts (List[str]): Query

        Returns:
            List[np.ndarray]: Embedding for Query
        """
        embeddings = []

        # Iterate through Queries
        for text in texts:
            inputs = self.tokenizer(
                text, return_tensors="pt", padding=True, truncation=True, max_length=512
            )

            inputs = {k: v.to(self.device) for k, v in inputs.items()}

            with torch.no_grad():
                outputs = self.model(**inputs)

            # Generate Embedding
            embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]
            embeddings.append(embedding.astype(np.float32))

        return embeddings

    def get_chunk(self, title: str, chunk_text: str = None) -> List[Tuple[int, str]]:
        """
        Get Chunks from Database

        Args:
            title (str): Title of Parent
            chunk_text (str, optional): Chunk ID. Defaults to None.

        Returns:
            List[Tuple[int, str]]: List of Chunks, IDs
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # If Chunk ID Given
        if chunk_text:
            cursor.execute(
                """
                SELECT id, chunk_text FROM chunks WHERE
                document_id = (SELECT id FROM documents WHERE title = %s)
                AND chunk_text = %s
                """,
                (title, chunk_text),
            )

        # Get All Chunks for Document ID
        else:
            cursor.execute(
                """
                SELECT id, chunk_text FROM chunks WHERE
                document_id = (SELECT id FROM documents WHERE title = %s)
                """,
                (title,),
            )

        chunks = cursor.fetchall()

        cursor.close()
        conn.close()

        return chunks

    def get_embedding(self, chunk_id: int = None) -> List[np.ndarray]:
        """
        Get Embeddings from Database

        Args:
            chunk_id (int, optional): Chunk ID of Embedding. Defaults to None.

        Returns:
            List[np.ndarray]: List of Embeddings
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        if chunk_id:
            cursor.execute(
                """
                SELECT embedding FROM embeddings WHERE
                chunk_id = %s
                """,
                (chunk_id,),
            )

        else:
            cursor.execute("SELECT embedding FROM embeddings")

        embeddings = cursor.fetchall()

        cursor.close()
        conn.close()

        np_embeddings = [
            np.frombuffer(embedding[0], dtype=np.float32) for embedding in embeddings
        ]

        return np_embeddings

    def get_embeddings_db(
        self, titles: List[str], texts: List[str]
    ) -> Tuple[List[np.ndarray], List[str]]:
        """
        Load or Generate Embeddings Database

        Args:
            titles (List[str]):
                List of titles for documents.
            texts (List[str]):
                List of texts for documents.
            embedding_directory (str):
                Save directory for generated embeddings.

        Returns:
            Tuple[List[np.ndarray], List[str]]:
                Returns generated embeddings and text chunks.
        """
        embeddings = []
        chunked_texts_with_titles = []

        for title, text in zip(titles, texts):
            sentences = sent_tokenize(text)
            chunked_texts = [
                " ".join(sentences[i : i + 3]) for i in range(0, len(sentences), 3)
            ]

            # Iterate through Chunk Number, Chunk
            for idx, chunk in enumerate(chunked_texts):
                chunked_text_with_title = f"{title}_Chunk_{idx + 1}: {chunk}"
                chunked_texts_with_titles.append(chunked_text_with_title)

                chunk_result = self.get_chunk(title, chunk)

                # Get Chunk if Exists
                if chunk_result:
                    chunk_id = chunk_result[0][0]

                # Else Add to Database
                else:
                    conn = psycopg2.connect(**self.db_config)
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO chunks (document_id, chunk_text)
                        VALUES ((SELECT id FROM documents
                        WHERE title = %s), %s) RETURNING id
                        """,
                        (title, chunk),
                    )
                    chunk_id = cursor.fetchone()[0]
                    conn.commit()
                    cursor.close()
                    conn.close()

                # Get Chunk Embedding
                embedding_result = self.get_embedding(chunk_id)

                # If Chunk Embedding Exists, Append to Output
                if embedding_result:
                    embedding = np.frombuffer(embedding_result[0][1], dtype=np.float32)
                    embeddings.append(embedding)

                # Else Generate Chunk
                else:
                    inputs = self.tokenizer(
                        chunk,
                        return_tensors="pt",
                        padding=True,
                        truncation=True,
                        max_length=512,
                    )
                    inputs = {k: v.to(self.device) for k, v in inputs.items()}

                    with torch.no_grad():
                        outputs = self.model(**inputs)

                    embedding = outputs.last_hidden_state.mean(dim=1).cpu().numpy()[0]

                    embeddings.append(embedding.astype(np.float32))

                    # Save the embedding in the database
                    conn = psycopg2.connect(**self.db_config)
                    cursor = conn.cursor()
                    cursor.execute(
                        """
                        INSERT INTO embeddings (chunk_id, embedding)
                        VALUES (%s, %s)
                        """,
                        (chunk_id, psycopg2.Binary(embedding.tobytes())),
                    )
                    conn.commit()
                    cursor.close()
                    conn.close()

        return embeddings, chunked_texts_with_titles
