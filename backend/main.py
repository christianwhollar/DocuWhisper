# main.py
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
import os
import base64

from src.initialize import initialize_rag_agent
from src.document_loader import DocumentLoader

app = FastAPI()


class Query(BaseModel):
    text: str


class Response(BaseModel):
    answer: str


class FileUpload(BaseModel):
    filename: str
    content: str


rag_agent = initialize_rag_agent()


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.post("/query", response_model=Response)
async def query(query: Query):
    try:
        answer = rag_agent.answer(query.text)
        return Response(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload")
async def upload(file: FileUpload, background_tasks: BackgroundTasks):
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail=f"Only .txt files are allowed. Received: {file.filename}",
        )

    file_location = f"data/test/{file.filename}"
    os.makedirs(os.path.dirname(file_location), exist_ok=True)
    # Decode the base64 string back to bytes
    file_content = base64.b64decode(file.content)
    with open(file_location, "wb") as f:
        f.write(file_content)

    # Add a background task to process the file after the response is sent
    background_tasks.add_task(process_file, file_location, file.filename)

    return {
        "info": f"File '{file.filename}' uploaded successfully. Processing will complete shortly."
    }


async def process_file(file_location: str, filename: str):
    try:
        # Load the new document
        loader = DocumentLoader(os.path.dirname(file_location))
        new_titles, new_documents = loader.load_documents()

        # Get embeddings for the new document
        embeddings = rag_agent.retriever.embeddings
        new_document_embeddings, new_chunked_texts_with_titles = (
            embeddings.get_embeddings(
                new_titles,
                new_documents,
                embedding_directory=os.path.join(
                    os.path.dirname(file_location), "embeddings"
                ),
            )
        )

        # Add the new document to the vector store
        rag_agent.retriever.vector_store.add_documents(
            new_chunked_texts_with_titles, new_document_embeddings
        )

        print(f"File '{filename}' processed and added to RAG agent")
    except Exception as e:
        print(f"Error processing file '{filename}': {str(e)}")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
