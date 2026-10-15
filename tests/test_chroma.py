from langchain_ollama import OllamaEmbeddings
from app.GenAI.rag.chroma_store import ChromaStore


# Create Chroma store
store = ChromaStore()

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

text = """
The standard processing time for a new domestic electricity connection
is 7 working days after all required documents have been submitted.
"""

vector = embeddings.embed_query(text)

print("\nEmbedding generated successfully")
print("Vector dimensions:", len(vector))


# Store chunk + embedding
result = store.add_chunk(
    chunk_id="policy-001",
    text=text,
    embedding=vector,
    metadata={
        "source": "consumer_policy.txt"
    }
)


print("\nChunk stored successfully")
print("Chunk ID:", result["chunk_id"])
print("Collection:", result["collection"])
print("Embedding dimensions:", len(vector))
print("Total chunks:", store.count())