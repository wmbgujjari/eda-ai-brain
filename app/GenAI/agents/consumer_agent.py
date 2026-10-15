from langchain.agents import create_agent

from app.GenAI.llm.llm_client import llm
from app.GenAI.tools.tool_registry import TOOLS
from app.GenAI.prompts.consumer_prompt import CONSUMER_AGENT_SYSTEM_PROMPT

agent = create_agent(
    model=llm,
    tools=TOOLS,
    system_prompt=CONSUMER_AGENT_SYSTEM_PROMPT
)