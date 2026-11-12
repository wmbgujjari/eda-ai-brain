
import os
from datetime import datetime

from docx import Document
from langchain.tools import tool

from app.services.conversation_service import ConversationService


conversation_service = ConversationService()

OUTPUT_DIR = os.path.abspath("generated_documents")
os.makedirs(OUTPUT_DIR, exist_ok=True)


@tool
def generate_word_document(
    thread_id: str,
    document_title: str = "EDA AI Brain Report",
    document_content: str = "",
    execution_id: str = "",
) -> dict:
    """
    Generate a downloadable Word document.

    Supports:
    1. Current specialist task results.
    2. Previously saved execution.
    3. Complete conversation history.
    """

    document = Document()

    document.add_heading("EDA AI Brain - Report", 0)

    document.add_paragraph(
        f"Generated on: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )

    # OPTION 1: Current task results
    if document_content.strip():

        document.add_heading(document_title, level=1)

        # Process document content line by line
        lines = document_content.splitlines()

        for line in lines:

            line = line.strip()

            if not line:
                continue

            # Remove empty limitation placeholders
            normalized_line = line.lstrip("·•-* ").strip().lower()

            if normalized_line in ["none reported", "none reported."]:
                continue

            skip_section = False
            # Skip Limitations heading and its content
            if line.lower().rstrip(":").lstrip("# ").strip() == "limitations":
                skip_section = True
                continue

            # Stop skipping when another heading starts
            if skip_section:
                if line.startswith("#"):
                    skip_section = False
                else:
                    continue

            # Markdown headings
            if line.startswith("### "):
                document.add_heading(line[4:].strip(), level=3)

            elif line.startswith("## "):
                document.add_heading(line[3:].strip(), level=2)

            elif line.startswith("# "):
                document.add_heading(line[2:].strip(), level=1)

            # Common report section headings
            elif line.lower().rstrip(":") in [
                "key findings",
                "summary key findings",
                "methodology",
                "result interpretation",
                "limitations",
                "consumption history",
                "consumer details",
            ]:
                continue

            # Bullet lists
            elif line.startswith(("- ", "* ", "• ")):
                bullet_content = line[2:].strip()

                document.add_paragraph(
                    bullet_content,
                    style="List Bullet"
                )

            # Numbered lists
            elif (
                len(line) > 2
                and line[0].isdigit()
                and line[1:3] in [". ", ") "]
            ):
                document.add_paragraph(
                    line[3:].strip(),
                    style="List Number"
                )

            # Normal paragraphs
            else:
                document.add_paragraph(line)

    # OPTION 2: Previously saved execution
    elif execution_id:

        executions = conversation_service.get_executions(thread_id)

        execution = next(
            (
                item for item in executions
                if item.get("execution_id") == execution_id
            ),
            None,
        )

        if not execution:
            return {
                "success": False,
                "message": f"No execution found for ID: {execution_id}",
            }

        document.add_heading("Execution Details", level=1)

        document.add_paragraph(
            f"Request: {execution.get('user_request', '')}"
        )

        document.add_paragraph(
            f"Workflow: {execution.get('workflow', '')}"
        )

        document.add_paragraph(
            f"Status: {execution.get('status', '')}"
        )

        document.add_heading("Execution Plan", level=2)

        for task in execution.get("plan", []):
            document.add_paragraph(
                str(task),
                style="List Bullet"
            )

        document.add_heading("Task Results", level=2)

        document.add_paragraph(
            str(execution.get("task_results", {}))
        )

        document.add_heading("Final Answer", level=2)

        document.add_paragraph(
            execution.get("final_answer") or ""
        )

    # OPTION 3: Complete conversation
    else:

        conversation = conversation_service.get_conversation(thread_id)

        if not conversation:
            return {
                "success": False,
                "message": f"No conversation found for thread: {thread_id}",
            }

        document.add_heading("Conversation History", level=1)

        for message in conversation.get("messages", []):

            role = message.get("role", "unknown").capitalize()

            document.add_heading(role, level=2)

            document.add_paragraph(
                str(message.get("content", ""))
            )

            if message.get("task_results"):
                document.add_paragraph(
                    f"Task Results: {message['task_results']}"
                )

        executions = conversation_service.get_executions(thread_id)

        if executions:

            document.add_heading("Execution History", level=1)

            for index, execution in enumerate(executions, start=1):

                document.add_heading(
                    f"Execution {index}",
                    level=2
                )

                document.add_paragraph(
                    f"Request: {execution.get('user_request', '')}"
                )

                document.add_paragraph(
                    f"Workflow: {execution.get('workflow', '')}"
                )

                document.add_paragraph(
                    f"Final Answer: {execution.get('final_answer', '')}"
                )

    # SAVE DOCUMENT
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    filename = f"word_report_{timestamp}.docx"

    filepath = os.path.join(OUTPUT_DIR, filename)

    document.save(filepath)

    print("\nWORD DOCUMENT SAVED")
    print("OUTPUT_DIR:", OUTPUT_DIR)
    print("FILEPATH:", filepath)
    print("FILE EXISTS:", os.path.exists(filepath))

    return {
        "success": True,
        "filename": filename,
        "filepath": filepath,
        "file_type": (
            "application/vnd.openxmlformats-officedocument."
            "wordprocessingml.document"
        ),
        "message": "Word document generated successfully.",
    }
