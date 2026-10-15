from app.GenAI.graph.agentic_graph import agentic_graph
from langchain_core.messages import HumanMessage


result = agentic_graph.invoke({
    "messages": [HumanMessage(
        content="Analyze C001 consumption and tell me whether there is an unusual trend."
    )],
    "plan": [],
    "current_step":0,
    "results": {},
    "final_answer": None
})


print("\nFINAL STATE:")
print(result)

