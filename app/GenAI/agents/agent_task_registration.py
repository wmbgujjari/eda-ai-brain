
from langchain_core.messages import HumanMessage

from app.GenAI.tools.task_registry import register_task

from app.GenAI.graph.consumer_agent_graph import consumer_graph
from app.GenAI.graph.rag_agent_graph import rag_graph
from app.GenAI.graph.chart_agent_graph import chart_graph
from app.GenAI.agents.email_agent import email_agent
from app.GenAI.agents.word_agent import word_agent
import json
import traceback
from langchain_core.messages import SystemMessage



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

        # Parse structured specialist response
        if isinstance(response, str):
            try:
                response = json.loads(response)
            except json.JSONDecodeError:
                response = {
                    "result": {
                        "response": response
                    },
                    "explanation": {}
                }

        return {
            "agent": agent_name,
            "response": response.get("result", {}),
            "explanation": response.get("explanation", {}),
            "chart_data": result.get("chart_data"),
        }

    return handler



def create_email_handler(task_input: str) -> dict:
    """Prepare a structured email draft."""

    result = email_agent.invoke({
        "messages": [
            HumanMessage(content=task_input)
        ]
    })

    messages = result.get("messages", [])
    response = messages[-1].content if messages else ""

    try:
        # Extract JSON even if the LLM adds explanatory text.
        if isinstance(response, list):
            response = "".join(
                item.get("text", "")
                for item in response
                if isinstance(item, dict)
            )

        response = response.strip()

        decoder = json.JSONDecoder()
        email_draft = None

        for index, character in enumerate(response):
            if character == "{":
                try:
                    email_draft, _ = decoder.raw_decode(response[index:])
                    break
                except json.JSONDecodeError:
                    continue

        if not isinstance(email_draft, dict):
            raise ValueError("No valid email JSON object found.")

        required_fields = ["to", "cc", "bcc", "subject", "body", "attachments"]

        if not all(field in email_draft for field in required_fields):
            raise ValueError("Email draft is missing required fields.")

        print("\nEMAIL AGENT RAW RESPONSE:")
        print(response)

        print("\nEMAIL AGENT PARSED DRAFT:")
        print(email_draft if 'email_draft' in locals() else None)

        return {
            "agent": "email",
            "success": True,
            "response": "Email draft prepared successfully.",
            "email_draft": email_draft,
            "chart_data": None,
        }

    except (ValueError, TypeError) as error:
        return {
            "agent": "email",
            "success": False,
            "response": f"Email draft parsing failed: {error}",
            "email_draft": None,
            "chart_data": None,
        }


def create_word_handler(
    task_input: str,
    thread_id: str | None = None,
    context: dict | None = None,
) -> dict:
    """Generate a Word document using the Word Agent."""

    if not thread_id:
        return {
            "agent": "word",
            "success": False,
            "response": "Conversation ID is missing.",
            "explanation": {},
            "chart_data": None,
        }

    word_input = {
        "thread_id": thread_id,
        "user_request": task_input,
        "specialist_results": context or {},
    }

    try:
        result = word_agent.invoke({
            "messages": [
                HumanMessage(
                    content=(
                        "Prepare a Word document based on the following information:\n"
                        f"{word_input}"
                    )
                )
            ]
        })

    except Exception:
        traceback.print_exc()
        raise

    messages = result.get("messages", [])

    final_response = messages[-1].content if messages else ""

    # Extract explanation from the Word agent's final response.
    agent_output = {}

    if isinstance(final_response, dict):
        agent_output = final_response

    elif isinstance(final_response, str):

        cleaned_response = final_response.strip()

        # Handle JSON enclosed in Markdown code fences.
        if cleaned_response.startswith("```"):
            cleaned_response = cleaned_response.strip("`")

            if cleaned_response.startswith("json"):
                cleaned_response = cleaned_response[4:].strip()

        try:
            agent_output = json.loads(cleaned_response)

        except json.JSONDecodeError:
            agent_output = {}

    explanation = agent_output.get("explanation", {})

    if not isinstance(explanation, dict):
        explanation = {}

    agent_result = agent_output.get("result", {})

    if not isinstance(agent_result, dict):
        agent_result = {}

    agent_response = agent_result.get("response", "")

    # Extract the actual Word tool result.
    document_info = None

    for message in messages:

        if getattr(message, "name", None) == "generate_word_document":

            content = message.content

            if isinstance(content, dict):
                document_info = content

            elif isinstance(content, str):
                try:
                    document_info = json.loads(content)
                except json.JSONDecodeError:
                    pass

            break

    if not document_info or not document_info.get("success"):
        return {
            "agent": "word",
            "success": False,
            "response": agent_response or str(final_response),
            "explanation": explanation,
            "chart_data": None,
        }

    filename = document_info["filename"]

    # Build Word-specific explanation without another LLM call.
    source_tasks = [
        task_name.replace("_", " ").title()
        for task_name, task_result in (context or {}).items()
        if isinstance(task_result, dict)
        and task_result.get("success", False)
    ]

    task_explanation = {
        "summary": (
            f"Word Document Generated Successfully "
            f"'{document_info['filename']}' ."
        ),
        "methodology": [
            "Created a Word document using the Consumer data.",
            "Formatted the available information into a downloadable report."

        ],
        "key_findings": [

        ],
        "result_interpretation": (

        ),
        "limitations": []
    }

    return {
        "agent": "word",
        "success": True,
        "response": document_info["message"],
        "document": {
            "filename": document_info["filename"],
            "filepath": document_info["filepath"],
            "file_type": document_info["file_type"],
            "download_url": f"/api/documents/{document_info['filename']}"
        },
        "explanation": task_explanation,
        "chart_data": None
    }

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

    register_task(
        "email",
        create_email_handler,
    )

    register_task(
        "word",
        create_word_handler,
    )
