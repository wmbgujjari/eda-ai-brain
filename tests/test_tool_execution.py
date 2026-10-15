from app.GenAI.llm.llm_client import llm
from app.GenAI.tools.consumer_tools import get_consumption_level

llm_with_tools = llm.bind_tools(
    [get_consumption_level]
)

response = llm_with_tools.invoke(
    "what is the consumption level of consumer C001"
)

print("LLM Respnse")
print("/n Tool calls",response.tool_calls)

tool_call = response.tool_calls[0]

tool_result = get_consumption_level.invoke(
    tool_call["args"]
)

print("/nTool Results",tool_result)