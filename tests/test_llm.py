from app.GenAI.llm.llm_client import llm

response= llm.invoke("Explain what an AI Agent is in one simple sentence")

print("LLM response")
print(response.content)