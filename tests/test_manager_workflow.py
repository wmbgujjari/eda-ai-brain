
from app.GenAI.agents.manager_agent import create_manager_plan
from app.GenAI.agents.manager_executor import execute_planned_task


def main():
    request = (
        "Get the consumption level of consumer C001, "
        "retrieve its historical consumption data, "
        "and prepare a chart."
    )

    print("User request:")
    print(request)

    plan = create_manager_plan(request)

    print("\nManager plan:")
    for number, task in enumerate(plan.tasks, start=1):
        print(f"{number}. {task.task_name}: {task.task_input}")

    results = []

    print("\nExecuting planned tasks:")

    for task in plan.tasks:
        result = execute_planned_task(
            task_name=task.task_name,
            task_input=task.task_input,
        )

        results.append(result)

        print(f"\nTask: {task.task_name}")
        print(f"Success: {result['success']}")
        print(result.get("result", result.get("error")))

    print("\nWorkflow summary:")
    print(f"Planned tasks: {len(plan.tasks)}")
    print(f"Successful tasks: {sum(r['success'] for r in results)}")
    print(f"Failed tasks: {sum(not r['success'] for r in results)}")


if __name__ == "__main__":
    main()
