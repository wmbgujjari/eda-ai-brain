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
from app.GenAI.core.manager_executor import execute_planned_task
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

    thread_id: str
    plan: list[PlannedTask]
    current_step: int

    # Fields passed to each parallel worker through Send.
    task: PlannedTask
    task_index: int

    # Results are merged using unique task indexes.
    results: Annotated[dict[str, dict], merge_results]

    final_answer: str | None

def general_response_node(state: AgenticState) -> dict:
    """Respond directly without invoking specialist agents."""

    messages = state.get("messages", [])

    print("\nGENERAL RESPONSE NODE")
    print("No specialist agents will be executed.")

    try:
        response = llm.invoke(
            [
                SystemMessage(
                    content=(
                        "You are a helpful AI assistant for an "
                        "electricity distribution platform. "
                        "Respond naturally to the user's latest message. "
                        "Use previous conversation messages when relevant. "
                        "For greetings and casual conversation, respond "
                        "conversationally. Do not invent specialist results."
                    )
                ),
                *messages,
            ]
        )

        final_answer = response.content

        if not isinstance(final_answer, str):
            final_answer = str(final_answer)

    except Exception as error:
        print("General response failed:", error)
        final_answer = (
            "Sorry, I couldn't generate a response. Please try again."
        )

    return {
        "final_answer": final_answer,
        "messages": [
            AIMessage(content=final_answer)
        ],
    }

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
    tasks = state.get("plan", [])

    # No specialist tasks: handle as general conversation.
    if not tasks:
        print("\nNo specialist tasks. Routing to General LLM.")
        return "general_response"

    # Email and Word tasks execute after analysis tasks.
    deferred_tasks = {"email", "word"}

    analysis_tasks = [
        (index, task)
        for index, task in enumerate(tasks)
        if task.task_name.strip().lower() not in deferred_tasks
    ]

    has_email = any(
        task.task_name.strip().lower() == "email"
        for task in tasks
    )

    has_word = any(
        task.task_name.strip().lower() == "word"
        for task in tasks
    )

    print("\nTASKS RECEIVED BY DISPATCHER:")
    for index, task in enumerate(tasks):
        print(index, task.task_name)

    print("\nANALYSIS TASKS:")
    for index, task in analysis_tasks:
        print(index, task.task_name)

    if not analysis_tasks:
        if has_word:
            return "execute_word"

        if has_email:
            return "execute_email"

        return "finish"

    print(
        f"\nDISPATCHING {len(analysis_tasks)} ANALYSIS TASKS IN PARALLEL"
    )

    return [
        Send(
            "execute_task",
            {
                "task": task,
                "task_index": index,
            },
        )
        for index, task in analysis_tasks
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


def execute_email_node(state: AgenticState) -> dict:
    """Execute email tasks after all analysis tasks have completed."""

    plan = state.get("plan", [])
    results = state.get("results", {})

    email_tasks = [
        (index, task)
        for index, task in enumerate(plan)
        if task.task_name == "email"
    ]

    if not email_tasks:
        return {}

    # Give the email agent the completed analysis results,
    # using task names instead of numeric keys.
    specialist_results = {
        result.get("task_name", index): result
        for index, result in sorted(
            results.items(),
            key=lambda item: int(item[0]),
        )
        if isinstance(result, dict)
        and result.get("task_name") != "email"
    }

    email_results = {}

    for task_index, task in email_tasks:
        print("\nDEFERRED EMAIL EXECUTION")
        print("Instruction:", task.task_input)
        print("Available analysis results:", list(specialist_results))

        try:
            task_result = execute_planned_task(
                task.task_name,
                task.task_input,
                context=specialist_results,
            )
        except Exception as error:
            task_result = {
                "task_name": task.task_name,
                "success": False,
                "result": None,
                "error": str(error),
            }

        email_results[str(task_index)] = task_result

        writer = get_stream_writer()
        writer({
            "event": "task_completed",
            "task_index": task_index,
            "task_name": task.task_name,
            "success": bool(task_result.get("success", False)),
            "result": task_result,
        })

        print("Email task success:", task_result.get("success"))

    return {"results": email_results}


def execute_word_node(state: AgenticState) -> dict:
    """Execute Word document tasks after required analysis tasks."""

    plan = state.get("plan", [])
    results = state.get("results", {})

    word_tasks = [
        (index, task)
        for index, task in enumerate(plan)
        if task.task_name == "word"
    ]

    if not word_tasks:
        return {}

    specialist_results = {
        result.get("task_name", index): result
        for index, result in sorted(
            results.items(),
            key=lambda item: int(item[0]),
        )
        if isinstance(result, dict)
        and result.get("task_name") not in ("email", "word")
    }

    word_results = {}

    for task_index, task in word_tasks:
        print("\nDEFERRED WORD EXECUTION")
        print("Instruction:", task.task_input)
        print("Available analysis results:", list(specialist_results))
        print("\nSPECIALIST RESULTS CONTENT:")
        print(
            json.dumps(
                specialist_results,
                indent=2,
                ensure_ascii=False,
                default=str
            )
        )        

        try:
            task_result = execute_planned_task(
                task.task_name,
                task.task_input,
                context=specialist_results,
                thread_id=state.get("thread_id"),
            )
        except Exception as error:
            task_result = {
                "task_name": task.task_name,
                "success": False,
                "result": None,
                "error": str(error),
            }

        word_results[str(task_index)] = task_result

        writer = get_stream_writer()
        writer({
            "event": "task_completed",
            "task_index": task_index,
            "task_name": task.task_name,
            "success": bool(task_result.get("success", False)),
            "result": task_result,
        })

        print("Word task success:", task_result.get("success"))

    return {"results": word_results}


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



def route_after_analysis(state: AgenticState):
    tasks = state.get("plan", [])

    has_word = any(
        task.task_name.strip().lower() == "word"
        for task in tasks
    )

    has_email = any(
        task.task_name.strip().lower() == "email"
        for task in tasks
    )

    # Generate Word document after specialist analysis.
    if has_word:
        return "execute_word"

    # Prepare email after specialist analysis.
    if has_email:
        return "execute_email"

    return "finish"

def route_after_word(state: AgenticState):
    tasks = state.get("plan", [])

    has_email = any(
        task.task_name.strip().lower() == "email"
        for task in tasks
    )

    if has_email:
        return "execute_email"

    return "finish"




# --------------------------------------------------
# Build the multi-agent graph
# --------------------------------------------------

graph_builder = StateGraph(AgenticState)

graph_builder.add_node("planner", planner_node)
graph_builder.add_node("execute_task", execute_task_node)
graph_builder.add_node("execute_email", execute_email_node)
graph_builder.add_node("execute_word", execute_word_node)
graph_builder.add_node("finish", finish_node)
graph_builder.add_node("general_response", general_response_node)

graph_builder.add_edge(START, "planner")

# --------------------------------------------------
# Planner routing
# --------------------------------------------------

graph_builder.add_conditional_edges(
    "planner",
    dispatch_tasks,
    {
        "finish": "finish",
        "execute_email": "execute_email",
        "execute_word": "execute_word",
        "general_response": "general_response",
    },
)

# --------------------------------------------------
# Parallel analysis execution
# --------------------------------------------------

graph_builder.add_edge("execute_task", "after_analysis")

graph_builder.add_node(
    "after_analysis",
    lambda state: {},
)

# --------------------------------------------------
# Route after analysis completion
# --------------------------------------------------

graph_builder.add_conditional_edges(
    "after_analysis",
    route_after_analysis,
    {
        "execute_word": "execute_word",
        "execute_email": "execute_email",
        "finish": "finish",
    },
)

# --------------------------------------------------
# Route after Word document generation
# --------------------------------------------------

graph_builder.add_conditional_edges(
    "execute_word",
    route_after_word,
    {
        "execute_email": "execute_email",
        "finish": "finish",
    },
)

# --------------------------------------------------
# Email completion
# --------------------------------------------------

graph_builder.add_edge("execute_email", "finish")

# --------------------------------------------------
# Final graph edges
# --------------------------------------------------

graph_builder.add_edge("finish", END)
graph_builder.add_edge("general_response", END)

agentic_graph = graph_builder.compile()
