from .llm import LLM
from .retriever import Retriever


class RAGAgent:
    def __init__(self, retriever: Retriever, llm: LLM):
        """
        RAG Agent

        Args:
            retriever (Retriever):
            llm (LLM): _description_
        """
        self.retriever = retriever
        self.llm = llm

    def get_prompt(self, query: str) -> str:
        """
        Generate Prompt for Query and Embeddings
        Args:
            query (str): User Query

        Returns:
            str: LLM Prompt
        """
        context = self.retriever.retrieve(query, k=2)
        context = " ".join(context)
        prompt = f"Context: {''.join(context)}\n\nQuestion: {query}\n\nAnswer:"
        return prompt

    def answer(self, query: str) -> str:
        """
        Get LLM Response
        Args:
            query (str): User Query

        Returns:
            str: LLM Response
        """
        prompt = self.get_prompt(query)
        return self.llm.generate(prompt)
