from langchain_core.messages import HumanMessage

from app.GenAI.graph.main_agent_graph import main_agent_graph


config = {
    "configurable": {
        "thread_id": "chart-test-001"
    }
}


result = main_agent_graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="Prepare a chart for C001 consumption history."
            )
        ]
    },
    config=config
)


print("\nFINAL RESPONSE:")
print(result["messages"][-1].content)

print("\nNEXT AGENT:")
print(result["next_agent"])

print("\nCHART DATA:")
print(result["chart_data"])