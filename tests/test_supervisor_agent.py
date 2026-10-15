from langchain_core.messages import HumanMessage,SystemMessage
from app.GenAI.prompts.supervisor_prompt import SUPERVISOR_SYSTEM_PROMPT

from app.GenAI.agents.supervisor_agent import (
    supervisor_llm,
    SupervisorDecision
)

questions = [
    "What is the consumption level of C001?",
    "How many days does a consumer domestic electricity connection take?",
    "Predict tomorrow's a consumer C001 demand.",
    "Prepare a chart for C001 consumption history."
]


for question in questions:


    decision = supervisor_llm.invoke([
        SystemMessage(
            content=SUPERVISOR_SYSTEM_PROMPT
        ),
        HumanMessage(
            content=question
        )
    ])

    print("\nQuestion:", question)
    print("Decision:", decision)
    print("Next Agent:", decision.next_agent)