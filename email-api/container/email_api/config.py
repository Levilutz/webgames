import os


TEST_MODE = os.getenv("TEST_MODE")


def _get_env_required(name: str) -> str:
    """Retrieve a required environment variable."""
    value = os.getenv(name)
    if not value:
        if TEST_MODE:
            return ""
        else:
            raise Exception(f"Required env var not set: {name}")
    return value


# The SMTP server to connect to (e.g. mail.example.com)
MAIL_SERVER = _get_env_required("MAIL_SERVER")

# The port for the SMTP server
MAIL_SERVER_PORT = int(os.getenv("MAIL_SERVER_PORT") or "25")

# The domain to use in the 'from' line of emails (e.g. example.com)
MAIL_FROM_DOMAIN = _get_env_required("MAIL_FROM_DOMAIN")

# The displayed "from" addr for outgoing mail (e.g. Example Site)
MAIL_FROM_DISPLAY = os.getenv("MAIL_FROM_DISPLAY") or ""
