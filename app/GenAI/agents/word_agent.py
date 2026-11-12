
from app.GenAI.llm.llm_client import llm
from app.GenAI.tools.word_tool import generate_word_document

from langchain.agents import create_agent
from app.GenAI.prompts.word_system_prompt import WORD_AGENT_SYSTEM_PROMPT

word_agent = create_agent(
    model=llm,
    tools=[generate_word_document],
    system_prompt=WORD_AGENT_SYSTEM_PROMPT,
)
