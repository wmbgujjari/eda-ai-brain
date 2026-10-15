from pydantic import BaseModel
from typing import Literal

from app.GenAI.llm.llm_client import llm
from app.GenAI.prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT


class SupervisorDecision(BaseModel):

    next_agent: Literal[
        "consumer",
        "rag",
        "forecast",
        "chart"
    ]


supervisor_llm = llm.with_structured_output(
    SupervisorDecision
)