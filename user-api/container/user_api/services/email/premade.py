from user_api.services.email.client import send_email


def send_test_email(to_email: str) -> None:
    """Send a generic test email."""
    send_email(
        to_emails=[to_email],
        subject="Test email",
        html_content="This is a test email",
    )
