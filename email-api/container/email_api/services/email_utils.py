from email.headerregistry import Address
from email.message import EmailMessage
from smtplib import SMTP
from typing import List

from email_api import config


def send_email(
    to_addrs: List[Address], subject: str, content: str, from_user: str = "no-reply"
) -> None:
    """Send an email to a given list of recipients."""
    # Construct the email
    msg = EmailMessage()
    msg.set_content(content)
    msg["Subject"] = subject
    msg["From"] = Address(
        display_name=config.MAIL_FROM_DISPLAY,
        username=from_user,
        domain=config.MAIL_FROM_DOMAIN,
    )
    msg["To"] = to_addrs

    # Send the email
    with SMTP(config.MAIL_SERVER, port=config.MAIL_SERVER_PORT) as smtp:
        smtp.starttls()
        smtp.send_message(msg)


if __name__ == "__main__":
    dest = Address("Levi Lutz", "levi6900", "gmail.com")
    send_email([dest], "Important information", "I'm some content")
