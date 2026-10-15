from app.GenAI.agents.workflow_router import choose_workflow
from app.GenAI.prompts.workflow_router import WORKFLOW_ROUTER_PROMPT

requests = [
    "Get the consumption level of consumer C001.",
    "Show a historical consumption chart for consumer C001.",
    (
        "Get the consumption level of consumer C001 "
        "and prepare a chart of its historical consumption."
    ),
]

for request in requests:
    decision = choose_workflow(request)

    print("Required capabilities:", decision.required_capabilities)
    print("Workflow:", decision.workflow)
    print("Reason:", decision.reason)

