from user_api.services.email.client import send_email


def send_test_email(to_email: str) -> None:
    """Send a generic test email."""
    send_email(
        to_emails=[to_email],
        subject="Test email",
        html_content="This is a test email",
    )


def send_verification_email(to_email: str, code: str) -> None:
    """Send an email address confirmation email."""
    content = f"Your email verification code is {code}"
    send_email(
        to_emails=[to_email],
        subject="[Web Games] Confirm your email address",
        html_content=content,
    )


def send_post_verification_email(to_email: str, first_name: str) -> None:
    """Send an email welcoming the user and confirming verification."""
    subject = f"Welcome to Web Games, {first_name}"
    content = "Your verification was successful. Log in now!"
    send_email(
        to_emails=[to_email],
        subject=subject,
        html_content=content,
    )
