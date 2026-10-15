
from langchain_core.messages import HumanMessage

from app.GenAI.graph.agentic_graph import agentic_graph


def main():
    request = (
        "Get the consumption level of consumer C001, "
        "retrieve its historical consumption data, "
        "and prepare a chart."
    )

    result = agentic_graph.invoke({
        "messages": [
            HumanMessage(content=request)
        ],
        "plan": [],
        "current_step": 0,
        "results": {},
        "final_answer": None,
    })

    print("\n" + "=" * 60)
    print("FINAL MANAGER RESPONSE")
    print("=" * 60)
    print(result["final_answer"])

    print("\nTASK RESULTS")
    for step, task_result in result["results"].items():
        print(f"\nTask {step}: {task_result['task_name']}")
        print(f"Success: {task_result['success']}")

        if task_result["success"]:
            print(task_result["result"])
        else:
            print(task_result["error"])


if __name__ == "__main__":
    main()
