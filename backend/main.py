# main.py

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from src.initialize import initialize_rag_agent

app = FastAPI()


class Query(BaseModel):
    text: str


class Response(BaseModel):
    answer: str


rag_agent = initialize_rag_agent()


@app.post("/query", response_model=Response)
async def query(query: Query):
    try:
        answer = rag_agent.answer(query.text)
        return Response(answer=answer)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)
