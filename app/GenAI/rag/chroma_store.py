import chromadb


class ChromaStore:

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path="data/chroma"
        )

        self.collection = self.client.get_or_create_collection(
            name="consumer_policy"
        )

    def add_chunk(self, chunk_id, text, embedding, metadata=None):

        self.collection.add(
            ids=[chunk_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata] if metadata else None
        )

        return {
            "chunk_id": chunk_id,
            "collection": self.collection.name
        }

    def search(self, query_embedding, top_k=3):

        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )

        return results        

    def count(self):

        return self.collection.count()