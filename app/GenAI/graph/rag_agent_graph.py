from typing import TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph import StateGraph, START, END

from app.GenAI.agents.rag_agent import agent


class RagAgentState(TypedDict):
    messages: list[BaseMessage]


def rag_agent_node(state: RagAgentState):

    response = agent.invoke({
        "messages": state["messages"]
    })

    return {
        "messages": response["messages"]
    }


graph_builder = StateGraph(RagAgentState)

graph_builder.add_node(
    "rag_agent",
    rag_agent_node
)

graph_builder.add_edge(
    START,
    "rag_agent"
)

graph_builder.add_edge(
    "rag_agent",
    END
)

rag_graph = graph_builder.compile()