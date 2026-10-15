from langchain_ollama import OllamaEmbeddings
from sklearn.metrics.pairwise import cosine_similarity


embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)


text_a = "How long does a domestic electricity connection take?"

text_b = "A domestic electricity connection takes 7 working days."

text_c = "The electricity bill depends on recorded consumption and tariff."


vector_a = embeddings.embed_query(text_a)
vector_b = embeddings.embed_query(text_b)
vector_c = embeddings.embed_query(text_c)


similarity_ab = cosine_similarity(
    [vector_a],
    [vector_b]
)[0][0]


similarity_ac = cosine_similarity(
    [vector_a],
    [vector_c]
)[0][0]


print("Similarity A ↔ B:", similarity_ab)

print("Similarity A ↔ C:", similarity_ac)