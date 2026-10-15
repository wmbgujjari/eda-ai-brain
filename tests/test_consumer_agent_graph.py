from langchain_core.messages import HumanMessage

#from app.graph.consumer_agent_graph import consumer_graph
from app.GenAI.graph.rag_agent_graph import rag_graph



result = rag_graph.invoke(
    {
        "messages": [
            HumanMessage(
                content="How long does a domestic electricity connection take?"
            )
        ]
    }
)


print("\nGraph Result:")

for message in result["messages"]:
    print(
        type(message).__name__,
        ":",
        message.content
    )