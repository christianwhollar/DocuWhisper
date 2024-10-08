import os
from typing import List, Tuple

import psycopg2
from dotenv import load_dotenv


class DocumentLoader:
    """Document Loader for Rag Agent"""

    def __init__(self, directory: str, db_mode: bool = False):
        """
        Initialize Document Loader

        Args:
            directory (str): Set local dir.
            db_mode (bool, optional): Database mode. Defaults to False.
        """
        self.directory = directory
        if db_mode:
            # Load Database Config & Build Database
            self.db_config = self.load_db_config()
            self.build_db()

    def load_documents(self) -> Tuple[List[str], List[str]]:
        """
        Load Local Documents

        Returns:
            Tuple[List[str], List[str]]: Titles of Documents, Documents
        """
        titles, documents = [], []

        for filename in os.listdir(self.directory):

            if filename.endswith(".txt"):

                title = filename.split(".txt")[0]
                title = title.replace("_", " ")
                titles.append(title)

                with open(os.path.join(self.directory, filename), "r") as file:
                    documents.append(file.read())

        return titles, documents

    def load_db_config(self) -> dict:
        """
        Load Database Config

        Returns:
            dict: Database Config Dict
        """
        load_dotenv()
        return {
            "dbname": os.getenv("DB_NAME"),
            "user": os.getenv("DB_USER"),
            "password": os.getenv("DB_PASSWORD"),
            "host": os.getenv("DB_HOST"),
            "port": os.getenv("DB_PORT"),
        }

    def clear_database(self):
        """
        Clear Database
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        cursor.execute("DELETE FROM documents")

        conn.commit()
        cursor.close()
        conn.close()

    def build_db(self):
        """
        Build Database (documents, chunks, embeddings)
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        # Create the documents table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS documents (
                id SERIAL PRIMARY KEY,
                title TEXT UNIQUE,
                content TEXT
            )
        """
        )

        # Create the chunks table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS chunks (
                id SERIAL PRIMARY KEY,
                document_id INTEGER REFERENCES documents(id),
                chunk_text TEXT
            )
        """
        )

        # Create the embeddings table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS embeddings (
                id SERIAL PRIMARY KEY,
                chunk_id INTEGER REFERENCES chunks(id),
                embedding BYTEA
            )
        """
        )

        conn.commit()
        cursor.close()
        conn.close()

    def store_in_db(self, titles: List[str], documents: List[Tuple[str, str]]):
        """
        Store Titles, Documents in Database

        Args:
            titles (List[str]): List of Titles
            documents (List[str]): List of Documents
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        for title, content in zip(titles, documents):
            cursor.execute("SELECT id FROM documents WHERE title = %s", (title,))
            result = cursor.fetchone()
            if not result:
                cursor.execute(
                    """
                    INSERT INTO documents (title, content)
                    VALUES (%s, %s) RETURNING id
                    """,
                    (title, content),
                )

        conn.commit()
        cursor.close()
        conn.close()

    def load_from_db(self) -> Tuple[List[str], List[str]]:
        """
        Load all Documents from Database

        Returns:
            Tuple[List[str], List[str]]: List of Titles, List of Documents
        """
        conn = psycopg2.connect(**self.db_config)
        cursor = conn.cursor()

        cursor.execute("SELECT title, content FROM documents")
        documents_db = cursor.fetchall()

        cursor.close()
        conn.close()

        titles = [doc[0] for doc in documents_db]
        documents = [doc[1] for doc in documents_db]

        return titles, documents
