from langchain_core.messages import HumanMessage, ToolMessage

from app.GenAI.llm.llm_client import llm
from app.GenAI.tools.consumer_tools import get_consumption_level

llm_with_tools = llm.bind_tools(
    [get_consumption_level]
)

user_message = HumanMessage(
    content = "What is the Consumption Level of the Consumer C001"
)

response = llm_with_tools.invoke(
    [user_message]
)

print("LLM Tool Call:")
print(response.tool_calls)

tool_call = response.tool_calls[0]

tool_result = get_consumption_level.invoke(
    tool_call["args"]
)

print("\nTool Result:")
print(tool_result)

tool_message = ToolMessage(
    content = str(tool_result),
    tool_call_id = tool_call["id"]
)

final_response = llm_with_tools.invoke(
    [
        user_message,
        response,
        tool_message
    ]
)

print("/nFinal Answer from LLM")
print(final_response.content)