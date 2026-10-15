from app.GenAI.tools.rag_tools import search_consumer_policy


question = "How long does a domestic electricity connection take?"

result = search_consumer_policy.invoke({
    "question": question
})

print("\n--- RAG TOOL RESULT ---")
print(result)