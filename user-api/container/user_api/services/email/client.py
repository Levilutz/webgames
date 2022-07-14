from typing import List

from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, MailSettings, SandBoxMode

from user_api.config import EMAIL_FROM, SENDGRID_KEY
from user_api.exceptions import InternalError


def send_email(
    to_emails: List[str],
    subject: str,
    html_content: str,
    from_email: str = EMAIL_FROM,
    sandbox: bool = False,
) -> None:
    """Send email to the given addresses."""
    if SENDGRID_KEY is None:
        raise InternalError("Cannot send mail without sendgrid key")

    message = Mail(
        from_email=from_email,
        to_emails=to_emails,
        subject=subject,
        html_content=html_content,
    )

    if sandbox:
        mail_settings = MailSettings(sandbox_mode=SandBoxMode(True))
        message.mail_settings = mail_settings

    sg = SendGridAPIClient(SENDGRID_KEY)
    response = sg.send(message)

    expected_status = 200 if sandbox else 202
    if response.status_code != expected_status:
        raise Exception(f"Got unexpected mail status: {response.status_code}")
