from user_api.services.email.client import send_email
from user_api.services.email.premade import (
    send_post_verification_email,
    send_test_email,
    send_verification_email,
)

__all__ = [
    "send_email",
    "send_post_verification_email",
    "send_test_email",
    "send_verification_email",
]
