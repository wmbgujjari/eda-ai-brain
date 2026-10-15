from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings

from app.GenAI.rag.chroma_store import ChromaStore


class RAGIngestion:

    def __init__(self):

        self.embeddings = OllamaEmbeddings(
            model="nomic-embed-text"
        )

        self.store = ChromaStore()

    def ingest_document(self, file_path):

        # Load document
        loader = TextLoader(file_path)
        documents = loader.load()

        # Split document
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=300,
            chunk_overlap=50
        )

        chunks = text_splitter.split_documents(documents)

        print("Number of chunks:", len(chunks))

        # Generate embeddings and store chunks
        for index, chunk in enumerate(chunks):

            vector = self.embeddings.embed_query(
                chunk.page_content
            )

            self.store.add_chunk(
                chunk_id=f"policy-{index + 1}",
                text=chunk.page_content,
                embedding=vector,
                metadata={
                    "source": file_path,
                    "chunk_number": index + 1
                }
            )

        return {
            "chunks": len(chunks),
            "collection": self.store.collection.name
        }