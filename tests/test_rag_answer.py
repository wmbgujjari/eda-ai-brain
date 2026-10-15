from langchain_ollama import OllamaEmbeddings
from langchain_ollama import ChatOllama

from app.GenAI.rag.chroma_store import ChromaStore


# Create embedding model
embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

# Create LLM
llm = ChatOllama(
    model="llama3.2",
    temperature=0
)

# Create Chroma store
store = ChromaStore()


# User question
question = "How long does a domestic electricity connection take?"


# Convert question to vector
query_vector = embeddings.embed_query(question)


# Retrieve relevant chunks
results = store.search(
    query_embedding=query_vector,
    top_k=3
)


# Get retrieved text
documents = results["documents"][0]

context = "\n\n".join(documents)


# Create RAG prompt
prompt = f"""
Answer the question using only the context provided below.

Context:
{context}

Question:
{question}

Answer:
"""


# Ask LLM
response = llm.invoke(prompt)


print("\n--- RAG ANSWER ---")
print(response.content)