
from app.GenAI.agents.email_agent import email_agent

response = email_agent.invoke({
    "messages": [
        {
            "role": "user",
            "content": """
            Draft a professional email to a division manager.

            Subject: September Consumption Analysis

            Findings:
            - Consumer C001 recorded 255 units in September 2026.
            - The email should briefly summarize this finding.

            Return the email subject and body.
            """
        }
    ]
})

print("\n--- Email Agent Response ---\n")
print(response["messages"][-1].content)
