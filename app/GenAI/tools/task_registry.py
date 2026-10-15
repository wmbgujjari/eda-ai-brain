from typing import Callable, Any


TASK_REGISTRY: dict[str, Callable[..., Any]] = {}


def register_task(
    task_name: str,
    handler: Callable[..., Any]
):
    TASK_REGISTRY[task_name] = handler


def get_task_handler(task_name: str):
    return TASK_REGISTRY.get(task_name)
