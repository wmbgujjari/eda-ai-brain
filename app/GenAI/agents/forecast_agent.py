from langchain.agents import create_agent

from app.GenAI.llm.llm_client import llm
from app.GenAI.tools.tool_registry import TOOLS

forecast_agent = create_agent(
    model=llm,
    tools=[]
)