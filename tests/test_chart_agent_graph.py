from langchain_core.messages import HumanMessage

from app.GenAI.graph.chart_agent_graph import chart_graph


result = chart_graph.invoke({
    "messages": [
        HumanMessage(
            content="prepare a chart for consumer C001 from Consumer History"
        )
    ]
})


for message in result["messages"]:
    print(type(message).__name__, ":", message.content)

print("\nCHART DATA:")
print(result["chart_data"])

print("\nCONSUMER ID:")
print(result["chart_data"]["consumer_id"])

print("\nCHART TYPE:")
print(result["chart_data"]["chart_type"])

print("\nNUMBER OF DATA POINTS:")
print(len(result["chart_data"]["data"]))   