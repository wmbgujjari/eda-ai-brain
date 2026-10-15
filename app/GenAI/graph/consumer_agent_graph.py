from typing import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END

from app.GenAI.agents.consumer_agent import agent


class ConsumerAgentState(TypedDict):
    messages: list[BaseMessage]


def consumer_agent_node(state: ConsumerAgentState):

    response = agent.invoke({
        "messages": state["messages"]
    })

    return {
        "messages": response["messages"]
    }


graph_builder = StateGraph(ConsumerAgentState)

graph_builder.add_node(
    "consumer_agent",
    consumer_agent_node
)

graph_builder.add_edge(
    START,
    "consumer_agent"
)

graph_builder.add_edge(
    "consumer_agent",
    END
)

consumer_graph = graph_builder.compile()