from langchain_ollama import OllamaEmbeddings

from app.GenAI.rag.chroma_store import ChromaStore
from app.GenAI.rag.rag_answer import RAGAnswer


class RAGService:

    def __init__(self):

        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text"
        )

        self.store = ChromaStore()

        self.answer_generator = RAGAnswer()

    def ask(self, question, top_k=3):

        # Convert question to embedding
        query_vector = self.embeddings.embed_query(question)

        # Retrieve relevant documents
        results = self.store.search(
            query_embedding=query_vector,
            top_k=top_k
        )

        documents = results["documents"][0]

        # Generate answer using retrieved documents
        answer = self.answer_generator.generate_answer(
            question,
            documents
        )

        return answer