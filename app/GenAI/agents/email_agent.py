
from langchain.agents import create_agent

from app.GenAI.llm.llm_client import llm
from app.GenAI.prompts.email_prompt import EMAIL_AGENT_SYSTEM_PROMPT


email_agent = create_agent(
    model=llm,
    tools=[],
    system_prompt=EMAIL_AGENT_SYSTEM_PROMPT
)
