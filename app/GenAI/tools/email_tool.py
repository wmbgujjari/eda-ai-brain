
import os
import smtplib
import mimetypes

from pathlib import Path
from dotenv import load_dotenv
from email.message import EmailMessage
from langchain.tools import tool


load_dotenv()

SMTP_HOST = "smtp.gmail.com"
SMTP_PORT = 587

GMAIL_SENDER = os.getenv("GMAIL_SENDER")
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")

PROJECT_ROOT = Path(__file__).resolve().parents[3]
OUTPUT_DIR = PROJECT_ROOT / "generated_documents"

@tool
def send_email(
    to: list[str],
    subject: str,
    body: str,
    cc: list[str] | None = None,
    bcc: list[str] | None = None,
    attachment_filenames: list[str] | None = None,
) -> dict:
    """Send an email through Gmail SMTP with optional CC, BCC and attachments."""
    
    try:
        if not GMAIL_SENDER or not GMAIL_APP_PASSWORD:
            raise ValueError("Gmail SMTP credentials are missing.")

        if not to:
            raise ValueError("At least one recipient is required.")

        cc = cc or []
        bcc = bcc or []
        attachment_filenames = attachment_filenames or []

        message = EmailMessage()

        message["From"] = GMAIL_SENDER
        message["To"] = ", ".join(to)
        message["Subject"] = subject

        if cc:
            message["Cc"] = ", ".join(cc)

        message.set_content(body)

        # Attach generated Word documents.
        for filename in attachment_filenames:

            if Path(filename).name != filename:
                raise ValueError("Invalid attachment filename.")

            file_path = OUTPUT_DIR / filename

            if not file_path.is_file():
                raise FileNotFoundError(
                    f"Attachment not found: {filename}"
                )

            mime_type, _ = mimetypes.guess_type(str(file_path))

            maintype, subtype = (
                mime_type.split("/", 1)
                if mime_type
                else ("application", "octet-stream")
            )

            with open(file_path, "rb") as file:
                message.add_attachment(
                    file.read(),
                    maintype=maintype,
                    subtype=subtype,
                    filename=filename,
                )

        recipients = to + cc + bcc

        with smtplib.SMTP(
            SMTP_HOST,
            SMTP_PORT,
            timeout=30
        ) as server:

            server.starttls()

            server.login(
                GMAIL_SENDER,
                GMAIL_APP_PASSWORD
            )

            refused = server.send_message(
                message,
                from_addr=GMAIL_SENDER,
                to_addrs=recipients,
            )

        if refused:
            return {
                "success": False,
                "message": "Some recipients were rejected.",
                "refused_recipients": list(refused.keys()),
            }

        return {
            "success": True,
            "message": "Email sent successfully.",
            "to": to,
            "cc": cc,
            "attachments": attachment_filenames,
        }

    except Exception as error:

        return {
            "success": False,
            "message": str(error),
        }
