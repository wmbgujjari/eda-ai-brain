from app.GenAI.agents.forecast_agent import forecast_agent


response = forecast_agent.invoke(
    {
        "messages": [
            {
                "role": "user",
                "content": "Please handle this as a forecast request."
            }
        ]
    }
)


print("\nForecast Agent Response:")

for message in response["messages"]:
    print(
        type(message).__name__,
        ":",
        message.content
    )