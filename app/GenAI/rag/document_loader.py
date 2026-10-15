from langchain_community.document_loaders import TextLoader

filepath = "data/documents/consumer_policy.txt"

loader = TextLoader(filepath)

documents = loader.load()

for document in documents:

    print("/n Document Contenct",document.page_content)
    print("/n Document Meta Data",document.metadata)