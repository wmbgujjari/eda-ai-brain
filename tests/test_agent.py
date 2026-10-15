from app.GenAI.agents.chart_agent import agent

response = agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "prepare a chart for consumer C001 from Consumer History "
            }
        ]
    }
)

print("Agent Response")

for message in response["messages"]:
    print(type(message).__name__,":",message.content)