from langchain.tools import tool

from app.services.rag_service import RAGService


rag_service = RAGService()


@tool
def search_consumer_policy(question: str):
    """
    Search the consumer electricity policy knowledge base
    and return an answer based on the relevant documents.
    """

    return rag_service.ask(question)