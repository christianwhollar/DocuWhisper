# main.py
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import base64

from src.initialize import initialize_rag_agent

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
async def upload(file: FileUpload):
    if not file.filename.endswith(".txt"):
        raise HTTPException(
            status_code=400,
            detail=f"Only .txt files are allowed. Received: {file.filename}",
        )
    file_location = f"data/test/{file.filename}"
    try:
        os.makedirs(os.path.dirname(file_location), exist_ok=True)
        # Decode the base64 string back to bytes
        file_content = base64.b64decode(file.content)
        with open(file_location, "wb") as f:
            f.write(file_content)
        return {"info": f"file '{file.filename}' saved at '{file_location}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
