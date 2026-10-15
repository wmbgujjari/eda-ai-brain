from langchain_core.messages import HumanMessage
from app.GenAI.graph.main_agent_graph import main_agent_graph


config = {
    "configurable": {
        "thread_id": "chat-001"
    }
}


# First conversation
result1 = main_agent_graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="How many days does a domestic electricity connection take?"
            )
        ],
        "next_agent": ""
    },
    config
)

print("\nFirst Response:")
print(result1["messages"][-1].content)


# Second conversation
result2 = main_agent_graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="Is that high?"
            )
        ],
        "next_agent": ""
    },
    config
)

print("\nSecond Response:")
print(result2["messages"][-1].content)