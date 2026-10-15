from langchain.agents import create_agent

from app.GenAI.llm.llm_client import llm
from app.GenAI.tools.chart_tool_registry import CHART_TOOLS
from app.GenAI.prompts.chart_prompt import CHART_AGENT_SYSTEM_PROMPT


agent = create_agent(
    model=llm,
    tools=CHART_TOOLS,
    system_prompt=CHART_AGENT_SYSTEM_PROMPT
)