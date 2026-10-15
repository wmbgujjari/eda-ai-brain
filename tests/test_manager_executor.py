
from app.GenAI.agents.manager_executor import execute_planned_task


def main():
    tasks = [
        ("consumer", "C001"),
        ("chart", "C001"),
    ]

    for task_name, task_input in tasks:
        print(f"\nExecuting task: {task_name}")

        result = execute_planned_task(
            task_name=task_name,
            task_input=task_input,
        )

        print(f"Success: {result['success']}")

        if result["success"]:
            print("Result:")
            print(result["result"])
        else:
            print(f"Error: {result['error']}")


if __name__ == "__main__":
    main()
