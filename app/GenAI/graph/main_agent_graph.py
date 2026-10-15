from app.core.database.checkpointer import checkpointer

from typing import Annotated,TypedDict

from langchain_core.messages import BaseMessage,SystemMessage
from langgraph.graph.message import add_messages
from langgraph.graph import StateGraph, START, END

from app.GenAI.graph.consumer_agent_graph import consumer_graph
from app.GenAI.agents.forecast_agent import forecast_agent
from app.GenAI.graph.rag_agent_graph import rag_graph
from app.GenAI.graph.chart_agent_graph import chart_graph
from app.GenAI.prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT

from app.GenAI.agents.supervisor_agent import (
    supervisor_llm,
    SupervisorDecision
)

class MainAgentState(TypedDict):
    messages: Annotated[list[BaseMessage],add_messages]
    next_agent: str
    chart_data: dict | None
    requested_capability: str | None


def supervisor_node(state: MainAgentState):

    # Respect the capability already selected by workflow_router.py.
    requested_capability = state.get("requested_capability")

    if requested_capability:
        print("SUPERVISOR DECISION: capability selected by workflow router:", requested_capability)

        return {
            "next_agent": requested_capability,
            "chart_data": None
        }

    # Preserve the existing LLM supervisor as a fallback.
    response = supervisor_llm.invoke([
        SystemMessage(
            content=SUPERVISOR_SYSTEM_PROMPT
        ),
        *state["messages"]
    ])

    print("SUPERVISOR DECISION:", response.next_agent)

    return {
        "next_agent": response.next_agent,
        "chart_data": None
    }


#def supervisor_node(state: MainAgentState):
#
#    message = state["messages"][-1].content.lower()
#
#    if "forecast" in message or "predict" in message:
#        next_agent = "forecast"
#
#    elif "consumer" in message or "consumption" in message:
#        next_agent = "consumer"
#
#    else:
#        next_agent = "rag"
#
#    return {
#        "next_agent": next_agent
#    }


def route_from_supervisor(state: MainAgentState):

    return state["next_agent"]


def consumer_node(state: MainAgentState):

    result = consumer_graph.invoke(
        {
            "messages": state["messages"]
        }
    )

    return {
        "messages": result["messages"]
    }

def rag_node(state: MainAgentState):

    result = rag_graph.invoke(
        {
            "messages": state["messages"]
        }
    )

    return {
        "messages": result["messages"]
    }

def chart_node(state: MainAgentState):

    result = chart_graph.invoke({
        "messages": state["messages"]
    })
    print("CHART GRAPH RESULT:", result)
    return {
        "messages": result["messages"],
        "chart_data": result["chart_data"]
    }

def forecast_node(state: MainAgentState):

    result = forecast_agent.invoke(
        {
            "messages": state["messages"]
        }
    )

    return {
        "messages": result["messages"]
    }


graph_builder = StateGraph(MainAgentState)


graph_builder.add_node(
    "supervisor",
    supervisor_node
)

graph_builder.add_node(
    "consumer",
    consumer_node
)

graph_builder.add_node(
    "rag",
    rag_node
)

graph_builder.add_node(
    "chart",
    chart_node
)

graph_builder.add_node(
    "forecast",
    forecast_node
)


graph_builder.add_edge(
    START,
    "supervisor"
)


graph_builder.add_conditional_edges(
    "supervisor",
    route_from_supervisor,
    {
        "consumer": "consumer",
        "forecast": "forecast",
        "rag": "rag",
        "chart":"chart"
    }
)


graph_builder.add_edge(
    "consumer",
    END
)

graph_builder.add_edge(
    "forecast",
    END
)

graph_builder.add_edge(
    "rag",
    END
)

graph_builder.add_edge(
    "chart", 
    END
)

main_agent_graph = graph_builder.compile(
    checkpointer = checkpointer
)