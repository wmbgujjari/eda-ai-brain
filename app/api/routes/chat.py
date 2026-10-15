from uuid import uuid4

from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage

from app.services.conversation_service import ConversationService
from app.GenAI.agents.workflow_router import choose_workflow
from app.GenAI.graph.main_agent_graph import main_agent_graph
from app.GenAI.graph.agentic_graph import agentic_graph

import json

from fastapi.responses import StreamingResponse

conversation_service = ConversationService()

router = APIRouter(
    prefix="/api",
    tags=["Chat"],
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str | None = None


def get_thread_id(thread_id: str | None) -> str:
    """Reuse an existing conversation ID or create a new one."""
    if not thread_id or thread_id.strip().lower() in {"none", "null"}:
        return str(uuid4())

    return thread_id.strip()


def extract_history(conversation) -> list[dict]:
    """Normalize stored conversation messages."""

    if isinstance(conversation, list):
        messages = conversation
    elif isinstance(conversation, dict):
        messages = conversation.get("messages", [])
    else:
        messages = []

    history = []

    for item in messages:
        if not isinstance(item, dict):
            continue

        role = (
            item.get("role")
            or item.get("sender")
            or item.get("type")
            or ""
        )

        content = (
            item.get("content")
            or item.get("message")
            or item.get("text")
        )

        if not isinstance(content, str) or not content.strip():
            continue

        role = str(role).lower()

        if role in {"user", "human"}:
            history.append({
                "role": "user",
                "content": content,
            })
        elif role in {"assistant", "ai"}:
            history.append({
                "role": "assistant",
                "content": content,
            })

    return history


def build_context(history: list[dict], current_message: str) -> str:
    """Provide prior turns as context without changing the current request."""

    recent_history = history[-6:]

    if not recent_history:
        return current_message

    lines = [
        "The following is prior conversation context.",
        "Use it only to understand references in the current question.",
        "Do not repeat or execute old requests unless the current question asks for them.",
        "",
    ]

    for item in recent_history:
        speaker = "User" if item["role"] == "user" else "Assistant"
        lines.append(f"{speaker}: {item['content']}")

    lines.extend([
        "",
        f"Current user question: {current_message}",
        "Answer the current question using relevant prior context.",
    ])

    return "\n".join(lines)


def extract_chart_data(result: dict, workflow: str):
    """Extract chart data from either workflow."""

    chart_data = result.get("chart_data")

    if chart_data:
        return chart_data

    if workflow == "multi":
        for task_result in result.get("results", {}).values():
            if not task_result.get("success"):
                continue

            specialist_result = task_result.get("result") or {}
            specialist_chart_data = specialist_result.get("chart_data")

            if specialist_chart_data:
                return specialist_chart_data

    return None



@router.post("/chat")
async def chat(request: ChatRequest):
    user_id = "user-001"
    thread_id = get_thread_id(request.thread_id)

    previous_conversation = conversation_service.get_conversation(
        thread_id
    )
    history = extract_history(previous_conversation)

    decision = choose_workflow(request.message)
    workflow = decision.workflow

    print("THREAD ID:", thread_id)
    print("PREVIOUS HISTORY MESSAGES:", len(history))
    print("CURRENT REQUEST:", request.message)
    print("SELECTED WORKFLOW:", workflow)
    print("ROUTING REASON:", decision.reason)

    conversation_service.add_message(
        thread_id,
        user_id,
        "user",
        request.message,
    )

    config = {
        "configurable": {
            "thread_id": thread_id,
        }
    }

    # Keep the existing single-agent workflow unchanged.
    if workflow == "single":
        contextualized_message = build_context(
            history,
            request.message,
        )

        result = main_agent_graph.invoke(
            {
                "messages": [
                    HumanMessage(content=contextualized_message)
                ],
                "requested_capability": decision.required_capabilities[0]
            },
            config,
        )

        messages = result.get("messages", [])
        response = messages[-1].content if messages else ""
        chart_data = extract_chart_data(result, workflow)

        conversation_service.add_message(
            thread_id,
            user_id,
            "assistant",
            response,
            chart_data,
        )

        return {
            "response": response,
            "thread_id": thread_id,
            "chart_data": chart_data,
            "workflow": workflow,
        }

    # Stream multi-agent task events to the client.
    async def stream_multi_agent():
        final_state = {}

        def send_event(event_name: str, payload: dict) -> str:
            event_json = json.dumps(
                payload,
                ensure_ascii=False,
                default=str,
            )
            return f"event: {event_name}\ndata: {event_json}\n\n"

        try:
            yield send_event(
                "workflow_started",
                {
                    "thread_id": thread_id,
                    "workflow": workflow,
                    "message": request.message,
                },
            )

            graph_input = {
                "messages": [
                    HumanMessage(content=request.message)
                ],
                "plan": [],
                "current_step": 0,
                "results": {},
                "final_answer": None,
            }

            async for mode, chunk in agentic_graph.astream(
                graph_input,
                config=config,
                stream_mode=["custom", "values"],
            ):
                if mode == "custom":
                    # A specialist has completed an individual task.
                    yield send_event(
                        "task_completed",
                        chunk,
                    )

                elif mode == "values":
                    # Keep the latest complete graph state.
                    final_state = chunk

            response = (
                final_state.get("final_answer")
                or "The multi-agent workflow did not produce a final answer."
            )

            chart_data = extract_chart_data(
                final_state,
                workflow,
            )

            conversation_service.add_message(
                thread_id,
                user_id,
                "assistant",
                response,
                chart_data,
            )

            yield send_event(
                "final",
                {
                    "response": response,
                    "thread_id": thread_id,
                    "chart_data": chart_data,
                    "workflow": workflow,
                },
            )

        except Exception as error:
            print("Multi-agent streaming failed:", error)

            yield send_event(
                "error",
                {
                    "thread_id": thread_id,
                    "message": str(error),
                },
            )

    return StreamingResponse(
        stream_multi_agent(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )



@router.get("/conversations")
def get_conversations_userId():

    user_id = "user-001"

    conversations = conversation_service.get_conversations_userId(
        user_id
    )

    return {"conversations": conversations}


@router.get("/conversations/{thread_id}")
def get_conversation(thread_id: str):

    conversation = conversation_service.get_conversation(thread_id)

    if conversation is None:
        return {
            "error": "The selected chat conversation was not found."
        }

    return conversation