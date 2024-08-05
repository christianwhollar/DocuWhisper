# tests/test_document_loader.py
import pytest
import os
from src.document_loader import DocumentLoader

TEST_FILES = {
    "file_one.txt": "This is the first document.",
    "file_two.txt": "This is the second document.",
    "file_three.txt": "This is third document.",
}


@pytest.fixture(scope="module")
def test_dir():
    dir_name = "test_data"
    os.makedirs(dir_name, exist_ok=True)

    for filename, content in TEST_FILES.items():
        with open(os.path.join(dir_name, filename), "w") as file:
            file.write(content)

    yield dir_name

    for filename in TEST_FILES:
        os.remove(os.path.join(dir_name, filename))
    os.rmdir(dir_name)


def test_load_documents(test_dir):
    loader = DocumentLoader(test_dir)
    titles_actual, documents_actual = loader.load_documents()

    titles_expected = [name.split(".")[0].replace("_", " ") for name in TEST_FILES]
    documents_expected = list(TEST_FILES.values())

    assert set(titles_actual) == set(titles_expected)
    assert set(documents_actual) == set(documents_expected)
