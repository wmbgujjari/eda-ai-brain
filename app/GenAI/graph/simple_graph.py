from typing import TypedDict

from langgraph.graph import StateGraph, START, END


class GraphState(TypedDict):
    message: str


def greeting_node(state: GraphState):

    return {
        "message": state["message"] + " - processed by LangGraph"
    }


graph_builder = StateGraph(GraphState)

graph_builder.add_node(
    "greeting",
    greeting_node
)

graph_builder.add_edge(
    START,
    "greeting"
)

graph_builder.add_edge(
    "greeting",
    END
)

graph = graph_builder.compile()