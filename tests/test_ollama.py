from ollama import chat

response = chat(
    model="llama3.2",
    messages=[
        {
            "role": "user",
            "content": "Explain what an AI Agent ? in one simple sentence"
        }
    ]
)

print("LLM Response")
print(response.message.content)