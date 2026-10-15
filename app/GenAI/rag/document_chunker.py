from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter

filepath = "data/documents/consumer_policy.txt"

loader = TextLoader(filepath)

documents = loader.load()

text_splitter = RecursiveCharacterTextSplitter(
    chunk_size = 300,
    chunk_overlap = 50
)

chunks = text_splitter.split_documents(documents)

print("Number of chunks:", len(chunks))

for index, chunk in enumerate(chunks, start=1):

    print(f"/n ====== chunk{index}=====/n")
    print(chunk.page_content)
    print("/n Page Meta :/n")
    print(chunk.metadata)