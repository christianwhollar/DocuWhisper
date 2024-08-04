# tests/test_rag_agent.py
from src.rag_agent import RAGAgent

def test_rag_agent(get_retriever, get_llm):
    retriever = get_retriever
    llm = get_llm

    rag_agent = RAGAgent(retriever=retriever, llm=llm)

    query = "Test Question"
    prompt = rag_agent.get_prompt(query=query)

    assert f"Question: {query}" in prompt
    assert "Context:" in prompt and "This is the first document." in prompt