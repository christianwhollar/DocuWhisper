from .retriever import Retriever
from .llm import LLM

class RAGAgent:
    def __init__(self, retriever: Retriever, llm: LLM):
        self.retriever = retriever
        self.llm = llm

    def answer(self, query:str) -> str:
        context = self.retriever.retrieve(query, k=3)
        context = ' '.join(context)
        context = context[:100]
        prompt = f"Context: {' '.join(context)}\n\nQuestion: {query}\n\nAnswer:"
        print(prompt)
        return self.llm.generate(prompt)