
from app.GenAI.tools.task_registry import get_task_handler
from app.GenAI.agents.agent_task_registration import register_agent_tasks
import json



def execute_planned_task(task_name: str, task_input: str,context: dict | None = None,thread_id: str | None = None,user_request: str | None = None,) -> dict:
    """Execute one planned task using the task registry."""

    register_agent_tasks()
    handler = get_task_handler(task_name)

    if handler is None:
        return {
            "task_name": task_name,
            "success": False,
            "result": None,
            "error": f"No handler registered for task: {task_name}",
        }

    if task_name == "consumer" and task_input.strip().upper().startswith("C"):
        task_input = (
            f"Get the consumption level and details of consumer "
            f"{task_input.strip()}."
        )
    elif task_name == "chart" and task_input.strip().upper().startswith("C"):
        task_input = (
            f"Retrieve historical consumption data and prepare a chart "
            f"for consumer {task_input.strip()}."
        )

    try:
        if task_name == "email":
            email_input = {
                "task_input": task_input,
                "specialist_results": context or {},
            }

            result = handler(
                "Prepare a professional email using the following information:\n"
                + json.dumps(email_input, ensure_ascii=False, default=str)
            )
        elif task_name == "word":
            result = handler(
                task_input,
                thread_id=thread_id,
                context=context or {},
            )
        else:
            result = handler(task_input)
            
        return {
            "task_name": task_name,
            "success": True,
            "result": result,
            "task_explanation": (
                result.get("explanation", {})
                if isinstance(result, dict)
                else {}
            ),
            "error": None,
        }
    except Exception as error:
        return {
            "task_name": task_name,
            "success": False,
            "result": None,
            "error": f"{type(error).__name__}: {error}",
        }
