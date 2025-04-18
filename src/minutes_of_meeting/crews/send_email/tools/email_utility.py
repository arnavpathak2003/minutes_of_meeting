import os
import base64
from email.mime.text import MIMEText
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from email.message import EmailMessage
import markdown
from pathlib import Path

SCOPES = ["https://www.googleapis.com/auth/gmail.compose"]

HTML_TEMPLATE = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
    </head>
    <body>
        {final_email_body}
    </body>
    </html>
"""


def authenticate_gmail():
    current_dir = Path(__file__).parent
    token_path = current_dir / "token.json"
    credentials_path = current_dir / "credentials.json"

    creds = None

    if token_path.exists():
        creds = Credentials.from_authorized_user_file(token_path, SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            if not credentials_path.exists():
                raise FileNotFoundError(
                    f"credentials.json not found at {credentials_path}. "
                    "Please ensure you have downloaded your OAuth 2.0 credentials "
                    "from Google Cloud Console and placed them in the correct location."
                )
            flow = InstalledAppFlow.from_client_secrets_file(credentials_path, SCOPES)
            creds = flow.run_local_server(port=0)

        with open(token_path, "w") as token:
            token.write(creds.to_json())

    service = build("gmail", "v1", credentials=creds)
    return service


def create_message(sender, to, subject, message_text):
    """Create a message for an email.

    Args:
    sender: Email address of the sender.
    to: Email address of the receiver.
    subject: The subject of the email.
    message_text: The text of the email.

    Returns:
        An object containing a base64url encoded email object.
    """

    md = markdown.Markdown(extensions=["tables", "fenced_code", "nl2br"])

    formatted_html = HTML_TEMPLATE.format(final_email_body=md.convert(message_text))

    msg = EmailMessage()
    content = formatted_html

    msg["To"] = to
    msg["From"] = sender
    msg["Subject"] = subject
    msg.add_header("Content-Type", "text/html")
    msg.set_payload(content)

    encodedMsg = base64.urlsafe_b64encode(msg.as_bytes()).decode()

    return {"raw": encodedMsg}


def create_draft(service, user_id, message_body):
    """Create and insert a draft email.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
             can be used to indicate the authenticated user.
    message_body: The body of the draft email.

    Returns:
        The created draft.
    """
    try:
        draft = (
            service.users()
            .drafts()
            .create(userId=user_id, body={"message": message_body})
            .execute()
        )
        print(f"Draft id: {draft['id']}\nDraft message: {draft['message']}")
        return draft
    except Exception as error:
        print(f"An error occurred: {error}")
        return None


def send_email(service, user_id, message_body):
    """Send an email message.

    Args:
    service: Authorized Gmail API service instance.
    user_id: User's email address. The special value "me"
             can be used to indicate the authenticated user.
    message_body: The body of the email message.

    Returns:
        The sent message.
    """
    try:
        message = (
            service.users().messages().send(userId=user_id, body=message_body).execute()
        )
        print(f"Message Id: {message['id']}")
        return {
            "success": True,
            "message_id": message["id"],
            "error": None,
            "status": "sent",
        }
    except Exception as error:
        print(f"An error occurred while sending the email: {error}")
        return {
            "success": False,
            "message_id": None,
            "error": str(error),
            "status": "failed",
        }
