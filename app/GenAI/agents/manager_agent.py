
from pydantic import BaseModel, Field
from typing import Literal

from app.GenAI.llm.llm_client import llm
from app.GenAI.prompts.manager_prompt import MANAGER_SYSTEM_PROMPT


class PlannedTask(BaseModel):
    """One task assigned to a registered specialist."""

    task_name: Literal["consumer", "rag", "chart"]
    task_input: str = Field(
        description="The specific instruction for this specialist."
    )


class ManagerPlan(BaseModel):
    """Structured execution plan produced by the manager."""

    tasks: list[PlannedTask]


manager_llm = llm.with_structured_output(ManagerPlan)


def create_manager_plan(user_request: str) -> ManagerPlan:
    """Create a structured plan for the requested goal."""

    return manager_llm.invoke([
        ("system", MANAGER_SYSTEM_PROMPT),
        ("human", user_request),
    ])
