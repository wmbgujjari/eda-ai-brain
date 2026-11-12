
import json

from langchain_core.messages import HumanMessage, SystemMessage

from app.GenAI.llm.llm_client import llm


def generate_task_explanation(
    user_request: str,
    task_name: str,
    task_input: str,
    task_result: dict,
) -> dict:
    """Generate a user-friendly explanation from actual task results."""

    system_prompt = """
You are an explanation generator for an electricity distribution AI platform.

Your job is to explain what a specialist task actually accomplished.

Rules:
1. Use only the supplied task result as evidence.
2. Never invent data, calculations, findings, or methodology.
3. Do not claim success if the task failed.
4. Keep simple tasks concise.
5. For analytical tasks, explain the methodology and key findings
   only when the result provides supporting evidence.
6. If information is unavailable, use empty arrays or an empty string.
7. Avoid repeatedly starting explanations with "I have".
8. Use natural, professional language suitable for electricity
   distribution officers.
9. Return valid JSON only. Do not include Markdown or code fences.

Return exactly this JSON structure:

{
    "summary": "A short explanation of the completed task.",
    "methodology": [],
    "key_findings": [],
    "result_interpretation": "",
    "limitations": []
}

All array values must be strings.
"""

    input_payload = {
        "user_request": user_request,
        "task_name": task_name,
        "task_instruction": task_input,
        "actual_task_result": task_result,
    }

    try:
        response = llm.invoke([
            SystemMessage(content=system_prompt),
            HumanMessage(
                content=json.dumps(
                    input_payload,
                    ensure_ascii=False,
                    default=str,
                )
            ),
        ])

        content = response.content

        if isinstance(content, list):
            content = "".join(
                item.get("text", "")
                for item in content
                if isinstance(item, dict)
            )

        content = content.strip()

        decoder = json.JSONDecoder()

        for index, character in enumerate(content):
            if character == "{":
                try:
                    explanation, _ = decoder.raw_decode(content[index:])

                    if isinstance(explanation, dict):
                        return explanation

                except json.JSONDecodeError:
                    continue

        raise ValueError("No valid explanation JSON found.")

    except Exception as error:
        print("Task explanation generation failed:", error)

        return {
            "summary": f"The {task_name} task was completed.",
            "methodology": [],
            "key_findings": [],
            "result_interpretation": "",
            "limitations": [
                "A detailed task explanation could not be generated."
            ],
        }
