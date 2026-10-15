from typing import TypedDict
import json

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END

from app.GenAI.agents.chart_agent import agent


class ChartAgentState(TypedDict):
    messages: list[BaseMessage]
    chart_data: dict | None


def chart_agent_node(state: ChartAgentState):

    response = agent.invoke({
        "messages": state["messages"]
    })

    chart_data = None

    for message in response["messages"]:

        if message.type == "tool":
            print("RAW CHART AGENT OUTPUT:", repr(message.content))
            chart_data = json.loads(message.content)
    print("CHART AGENT DATA:", chart_data)

    return {
        "messages": response["messages"],
        "chart_data": chart_data
    }


graph_builder = StateGraph(ChartAgentState)

graph_builder.add_node(
    "chart_agent",
    chart_agent_node
)

graph_builder.add_edge(
    START,
    "chart_agent"
)

graph_builder.add_edge(
    "chart_agent",
    END
)

chart_graph = graph_builder.compile()