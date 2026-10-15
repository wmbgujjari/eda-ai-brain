from app.GenAI.rag.rag_ingestion import RAGIngestion


ingestion = RAGIngestion()

result = ingestion.ingest_document(
    "data/documents/consumer_policy.txt"
)

print("\n--- INGESTION RESULT ---")
print("Chunks:", result["chunks"])
print("Collection:", result["collection"])
print("\nTotal chunks in Chroma:", ingestion.store.count())

results = ingestion.store.collection.get()

print("\n--- STORED CHUNKS ---")

for chunk_id in results["ids"]:
    print(chunk_id)