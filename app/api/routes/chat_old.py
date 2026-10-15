from fastapi import APIRouter
from pydantic import BaseModel
from langchain_core.messages import HumanMessage
from app.services.conversation_service import ConversationService

from app.graph.main_agent_graph import main_agent_graph

conversation_service = ConversationService()

router = APIRouter(
    prefix="/api",
    tags=["Chat"]
)


class ChatRequest(BaseModel):
    message: str
    thread_id: str


@router.post("/chat")
def chat(request: ChatRequest):

    user_id="user-001"

    # 1. Save user message
    conversation_service.add_message(
        request.thread_id,
        user_id,
        "user",
        request.message 
    )

    # 2. Send message to LangGraph
    config = {
        "configurable": {
            "thread_id": request.thread_id
        }
    }    
    result = main_agent_graph.invoke(
        {
            "messages": [
                HumanMessage(content=request.message)
            ]
        },
        config
    )
 
    response = result["messages"][-1].content

    chart_data = result.get("chart_data")

    print("FINAL CHART DATA BEFORE SAVE:", chart_data)
    
    conversation_service.add_message(
        request.thread_id,
        user_id,
        "assistant",
        response,
        chart_data
    )

    return {
        "response": response,
        "thread_id": request.thread_id,
        "chart_data": result.get("chart_data")
    }

@router.get("/conversations")
def get_conversations_userId():
    user_id="user-001"

    conversations=conversation_service.get_conversations_userId(user_id)
    return {"conversations":conversations}

@router.get("/conversations/{thread_id}")
def get_conversation(thread_id: str):

    conversation = conversation_service.get_conversation(thread_id)

    if conversation is None:
        return { "The Selected Chat Conversation is not Found" }

    return conversation
