from typing import Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field

from .email_utility import authenticate_gmail, create_message, send_email


class EmailToolInput(BaseModel):
    """Input schema for MyCustomTool."""

    body: str = Field(..., description="Description of the argument.")


class EmailTool(BaseTool):
    name: str = "EmailTool"
    description: str = "Send an email to a specific recipient"
    args_schema: Type[BaseModel] = EmailToolInput

    def _run(self, body: str) -> str:
        try:
            service = authenticate_gmail()

            sender = "enter.senderr.gmail-ID@gmail.com"
            to = "enter.senderr.gmail-ID@gmail.com"
            subject = "Meeting Minutes"
            message_text = create_message(sender, to, subject, body)

            result = send_email(service, "me", message_text)

            if result["success"]:
                return f"Successfully sent email to {to} with subject '{subject}'. Message ID: {result['message_id']}"
            else:
                return f"Failed to send email: {result['error']}"
        except Exception as error:
            return f"An error occurred: {error}"
