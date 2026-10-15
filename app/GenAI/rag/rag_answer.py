from langchain_ollama import ChatOllama


class RAGAnswer:

    def __init__(self):

        self.llm = ChatOllama(
            model="llama3.2",
            temperature=0
        )

    def generate_answer(self, question, documents):

        context = "\n\n".join(documents)

        prompt = f"""
Answer the question using only the context provided below.

Context:
{context}

Question:
{question}

Answer:
"""

        response = self.llm.invoke(prompt)

        return response.content