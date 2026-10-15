
from typing import Literal

from pydantic import BaseModel, Field

from app.GenAI.llm.llm_client import llm
from app.GenAI.prompts.workflow_router import WORKFLOW_ROUTER_PROMPT
from app.GenAI.agents.capability_classifier import classify_capabilities


Capability = Literal["consumer", "rag", "chart", "forecast"]


class WorkflowDecision(BaseModel):
    required_capabilities: list[Capability] = Field(
        description="All specialist capabilities required by the request."
    )
    reason: str = Field(
        description="Brief explanation of the capability selection."
    )
    workflow: Literal["single", "multi"] = Field(
        description="Execution strategy derived from the capabilities."
    )


workflow_router_llm = llm.with_structured_output(WorkflowDecision)


def choose_workflow(user_request: str) -> WorkflowDecision:
    # Step 1: Use deterministic classification first.
    capabilities = classify_capabilities(user_request)

    if capabilities:
        print("ROUTER MODE: deterministic")
        print("DETECTED CAPABILITIES:", capabilities)

        reason = (
            "Capabilities identified by the deterministic classifier: "
            + ", ".join(capabilities)
        )

    else:
        # Step 2: Use the LLM when no capability was detected.
        print("ROUTER MODE: LLM fallback")

        decision = workflow_router_llm.invoke(
            [
                ("system", WORKFLOW_ROUTER_PROMPT),
                ("human", user_request),
            ]
        )

        capabilities = list(
            dict.fromkeys(decision.required_capabilities)
        )
        reason = decision.reason

    # Step 3: Validate that at least one capability was identified.
    if not capabilities:
        raise ValueError(
            "Unable to identify the capabilities required for this request."
        )

    # Step 4: Derive workflow in Python.
    workflow = (
        "single" if len(capabilities) == 1 else "multi"
    )

    return WorkflowDecision(
        required_capabilities=capabilities,
        reason=reason,
        workflow=workflow,
    )