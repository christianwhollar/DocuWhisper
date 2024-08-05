from .retriever import Retriever
from .llm import LLM


class RAGAgent:
    def __init__(self, retriever: Retriever, llm: LLM):
        self.retriever = retriever
        self.llm = llm

    def get_prompt(self, query: str) -> str:
        context = self.retriever.retrieve(query, k=3)
        context = " ".join(context)
        prompt = f"Context: {''.join(context)}\n\nQuestion: {query}\n\nAnswer:"
        return prompt

    def answer(self, query: str) -> str:
        prompt = self.get_prompt(query)
        return self.llm.generate(prompt)
