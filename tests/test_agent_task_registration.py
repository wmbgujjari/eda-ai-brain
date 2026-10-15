from app.GenAI.tools.task_registry import get_task_handler
from app.GenAI.agents.agent_task_registration import register_agent_tasks


def test_agent_task_registration():
    register_agent_tasks()

    for task_name in ("consumer", "rag", "chart"):
        handler = get_task_handler(task_name)

        assert handler is not None, (
            f"Task '{task_name}' was not registered"
        )
        assert callable(handler), (
            f"Task '{task_name}' is not callable"
        )

    print("Consumer, RAG, and Chart tasks registered successfully.")


if __name__ == "__main__":
    test_agent_task_registration()
