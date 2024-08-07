# main.py
import os

from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel

from src.initialize import initialize_rag_agent

app = FastAPI()


class Query(BaseModel):
    text: str


class Response(BaseModel):
    answer: str


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
async def upload(file: UploadFile = File(...)):
    if not file.filename.endswith(".txt"):
        raise HTTPException(status_code=400, detail="Only .txt files are allowed")

    file_location = f"data/test/{file.filename}"

    try:
        with open(file_location, "wb") as f:
            f.write(file.file.read())
        return {"info": f"file '{file.filename}' saved at '{file_location}'"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
