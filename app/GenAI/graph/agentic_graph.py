import json
import re
from typing import Annotated, TypedDict
from langgraph.config import get_stream_writer

from langchain_core.messages import (
    AIMessage,
    BaseMessage,
    HumanMessage,
    SystemMessage,
)
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.types import Send

from app.GenAI.llm.llm_client import llm
from app.GenAI.agents.manager_agent import (
    PlannedTask,
    create_manager_plan,
)
from app.GenAI.agents.manager_executor import execute_planned_task
from app.GenAI.prompts.summary_prompt import SUMMARY_PROMPT


def merge_results(
    existing: dict[str, dict] | None,
    incoming: dict[str, dict] | None,
) -> dict[str, dict]:
    """Merge parallel task results without overwriting other tasks."""

    merged = dict(existing or {})
    merged.update(incoming or {})
    return merged


class AgenticState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]

    plan: list[PlannedTask]
    current_step: int

    # Fields passed to each parallel worker through Send.
    task: PlannedTask
    task_index: int

    # Results are merged using unique task indexes.
    results: Annotated[dict[str, dict], merge_results]

    final_answer: str | None


def extract_consumer_id(user_request: str) -> str | None:
    """Extract a consumer identifier from the current request."""

    match = re.search(
        r"\b[A-Z]{1,5}\d{1,10}\b",
        user_request,
        re.IGNORECASE,
    )

    return match.group(0).upper() if match else None


def normalize_tasks(
    tasks: list[PlannedTask],
    user_request: str,
) -> list[PlannedTask]:
    """Make specialist instructions explicit and consistent."""

    consumer_id = extract_consumer_id(user_request)

    normalized_tasks = []

    for task in tasks:
        task_input = task.task_input.strip()

        if task.task_name == "consumer" and consumer_id:
            task_input = (
                "Retrieve the consumption level and details of "
                f"consumer {consumer_id}."
            )

        elif task.task_name == "chart" and consumer_id:
            task_input = (
                "Retrieve historical consumption records and prepare "
                f"a line chart for consumer {consumer_id}. "
                "Return the actual historical data in chart_data. "
                "If no records are available, report that clearly "
                "and do not invent data."
            )

        normalized_tasks.append(
            PlannedTask(
                task_name=task.task_name,
                task_input=task_input,
            )
        )

    return normalized_tasks


def planner_node(state: AgenticState) -> dict:
    """Create and normalize the plan from the current user request."""

    messages = state.get("messages", [])

    if not messages:
        return {
            "plan": [],
            "current_step": 0,
        }

    user_request = messages[-1].content

    print("\nMANAGER PLANNER NODE")
    print("Current request:", user_request)

    manager_plan = create_manager_plan(user_request)

    tasks = normalize_tasks(
        manager_plan.tasks,
        user_request,
    )

    print("Normalized planned tasks:")

    for index, task in enumerate(tasks, start=1):
        print(
            f"{index}. {task.task_name}: "
            f"{task.task_input}"
        )

    return {
        "plan": tasks,
        "current_step": 0,
    }


def dispatch_tasks(state: AgenticState):
    """Dispatch all planned tasks as independent parallel branches."""

    tasks = state.get("plan", [])

    if not tasks:
        print("No tasks were planned.")
        return "finish"

    print(f"\nDISPATCHING {len(tasks)} TASKS IN PARALLEL")

    return [
        Send(
            "execute_task",
            {
                "task": task,
                "task_index": index,
            },
        )
        for index, task in enumerate(tasks)
    ]



def execute_task_node(state):
    task = state["task"]
    task_index = state["task_index"]

    print(f"\nPARALLEL EXECUTOR: Task {task_index + 1}")
    print("Agent:", task.task_name)
    print("Instruction:", task.task_input)

    try:
        task_result = execute_planned_task(
            task.task_name,
            task.task_input,
        )
    except Exception as error:
        task_result = {
            "task_name": task.task_name,
            "success": False,
            "result": None,
            "error": str(error),
        }

    success = bool(task_result.get("success", False))

    print(f"Task {task_index + 1} success:", success)
    print(f"Task {task_index + 1} result:", task_result)

    # Publish an event when this individual task finishes.
    writer = get_stream_writer()

    writer({
        "event": "task_completed",
        "task_index": task_index,
        "task_name": task.task_name,
        "success": success,
        "result": task_result,
    })

    # Preserve the existing graph-state behavior.
    return {
        "results": {
            str(task_index): task_result,
        }
    }



def finish_node(state: AgenticState) -> dict:
    """Combine actual specialist results into the final answer."""

    results = state.get("results", {})
    messages = state.get("messages", [])

    user_request = (
        messages[-1].content
        if messages
        else "No user request was provided."
    )

    successful_tasks = []
    failed_tasks = []

    for index, result in sorted(
        results.items(),
        key=lambda item: int(item[0]),
    ):
        task_info = {
            "task_number": int(index) + 1,
            **result,
        }

        if result.get("success"):
            successful_tasks.append(task_info)
        else:
            failed_tasks.append(task_info)

    print("\nMANAGER FINISH NODE")
    print("Completed tasks:", len(successful_tasks))
    print("Failed tasks:", len(failed_tasks))

    result_payload = {
        "user_request": user_request,
        "successful_tasks": successful_tasks,
        "failed_tasks": failed_tasks,
    }

    # Check whether a chart contains real, non-empty data.
    chart_available = False

    for task_info in successful_tasks:
        task_result = task_info.get("result") or {}

        if task_info.get("task_name") != "chart":
            continue

        
        # First level: execute_planned_task result
        execution_result = task_info.get("result") or {}

        # Second level: specialist handler result
        #specialist_result = execution_result.get("result") or {}    

        chart_data = execution_result.get("chart_data")

        if (
            isinstance(chart_data, dict)
            and isinstance(chart_data.get("data"), list)
            and len(chart_data["data"]) > 0
        ):
            chart_available = True
            break

    print("Chart contains data:", chart_available)

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        SUMMARY_PROMPT
                        + "\n\nAdditional requirements:\n"
                        "1. Answer the original user request directly.\n"
                        "2. Use the supplied specialist results; do not "
                        "ask the user to repeat their request.\n"
                        "3. Do not invent consumer details, historical "
                        "records, or results.\n"
                        "4. A successful handler does not necessarily "
                        "mean useful data was retrieved.\n"
                        "5. If chart data is empty, explicitly state that "
                        "no historical records were returned and that "
                        "a populated chart cannot yet be displayed.\n"
                        "6. Do not claim a chart was successfully prepared "
                        "unless non-empty chart data was returned.\n"
                        "7. Mention failed tasks or missing data honestly."
                    )
                ),
                HumanMessage(
                    content=json.dumps(
                        result_payload,
                        ensure_ascii=False,
                        default=str,
                    )
                ),
            ]
        )

        final_answer = response.content

        if not isinstance(final_answer, str):
            final_answer = str(final_answer)

    except Exception as error:
        print("Final summarization failed:", error)

        if not successful_tasks:
            final_answer = (
                "The requested tasks could not be completed."
            )
        else:
            final_answer = (
                "The specialist tasks returned results, but the final "
                "summary could not be generated. Please review the "
                "backend task results."
            )

    return {
        "final_answer": final_answer,
        "messages": [
            AIMessage(content=final_answer)
        ],
    }


# --------------------------------------------------
# Build the parallel multi-agent graph
# --------------------------------------------------

graph_builder = StateGraph(AgenticState)

graph_builder.add_node("planner", planner_node)
graph_builder.add_node("execute_task", execute_task_node)
graph_builder.add_node("finish", finish_node)

graph_builder.add_edge(START, "planner")

graph_builder.add_conditional_edges(
    "planner",
    dispatch_tasks,
    {
        "finish": "finish",
    },
)

graph_builder.add_edge("execute_task", "finish")
graph_builder.add_edge("finish", END)

agentic_graph = graph_builder.compile()