from langchain.agents import create_agent
from app.GenAI.llm.llm_client import llm
from app.GenAI.tools.rag_tool_registry import RAG_TOOLS
from app.GenAI.prompts.rag_prompt import RAG_AGENT_SYSTEM_PROMPT

agent = create_agent(
    model=llm,
    tools=RAG_TOOLS,
    system_prompt=RAG_AGENT_SYSTEM_PROMPT
)