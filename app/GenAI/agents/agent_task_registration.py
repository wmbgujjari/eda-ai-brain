
from langchain_core.messages import HumanMessage

from app.GenAI.tools.task_registry import register_task

from app.GenAI.graph.consumer_agent_graph import consumer_graph
from app.GenAI.graph.rag_agent_graph import rag_graph
from app.GenAI.graph.chart_agent_graph import chart_graph


def create_graph_handler(graph, agent_name):
    """Create a reusable handler for a specialist graph."""

    def handler(task_input: str) -> dict:
        result = graph.invoke({
            "messages": [
                HumanMessage(content=task_input)
            ]
        })

        messages = result.get("messages", [])

        response = ""
        if messages:
            response = messages[-1].content

        return {
            "agent": agent_name,
            "response": response,
            "chart_data": result.get("chart_data"),
        }

    return handler


def register_agent_tasks():
    """Register existing specialist agents as reusable tasks."""

    register_task(
        "consumer",
        create_graph_handler(consumer_graph, "consumer"),
    )

    register_task(
        "rag",
        create_graph_handler(rag_graph, "rag"),
    )

    register_task(
        "chart",
        create_graph_handler(chart_graph, "chart"),
    )
