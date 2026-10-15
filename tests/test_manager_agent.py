
from app.GenAI.agents.manager_agent import create_manager_plan


def main():
    request = (
        "Get consumption level of consumer C001's and historical consumption data "
        "and prepare a chart."
    )

    plan = create_manager_plan(request)

    print("User request:")
    print(request)

    print("\nManager plan:")
    for number, task in enumerate(plan.tasks, start=1):
        print(f"{number}. {task}")


if __name__ == "__main__":
    main()
