from app.GenAI.rag.chroma_store import ChromaStore
from langchain_ollama import OllamaEmbeddings

store = ChromaStore()

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

query = "How long does a domestic electricity connection take?"

query_vector = embeddings.embed_query(query)

print("Query embedding dimensions:", len(query_vector))

results = store.search(
    query_embedding=query_vector,
    top_k=3
)

print("\n--- SEARCH RESULTS ---")

print("IDs:", results["ids"])
print("Documents:", results["documents"])
print("Distances:", results["distances"])